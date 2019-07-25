import pandas as pd
import numpy as np
import json
from rasa_nlu import train
from datetime import datetime
from rasa_nlu.model import Interpreter
from rasa_nlu import training_data
from custom_exceptions import NoFactError, NoFactInOperand, FilterAndCardinalNotBound
from chatbot import duckling
from settings import NLU_MODEL_PATH, RASA_CONFIG_PATH, RASA_NLU_DATA_PATH, RASA_MODEL_SAVE_PATH

interpreter = Interpreter.load(NLU_MODEL_PATH)


# Function to fill aggregation in fact_condition
def fill_aggregation(raw_agg, intent):
	df = pd.DataFrame(raw_agg)
	# if first is present then fill them down first
	if all(df.iloc[0].isna()):
		df = df.fillna(method='ffill').fillna(method='bfill')
	else:
		df = df.fillna(method='bfill').fillna(method='ffill')
	# default aggregate_function
	if 'aggregate_functions' not in df.columns:
		df['aggregate_functions'] = 'sum'
	elif 'facts' not in df.columns:
		if intent in ('POHeaderDetails', 'POHeader'):
			df['facts'] = 'SubTotal'
		if intent in ('PODetails'):
			df['facts'] = 'LineTotal'
	raw_agg = df.to_dict('records')
	return raw_agg


# function to get aggregation same as dialogflow
def get_aggregation(entities, i):
	aggregation = {}
	if entities[i]['entity'] == 'agg':
		aggregation['aggregate_functions'] = entities[i]['value']
		i += 1
		ent = entities[i]['entity'] if i < len(entities) else 'NULL'
		if ent == 'fact':
			aggregation['facts'] = entities[i]['value']
			return aggregation, i
		else:
			return aggregation, i - 1
	if entities[i]['entity'] == 'fact':
		aggregation['facts'] = entities[i]['value']
		i += 1
		ent = entities[i]['entity'] if i < len(entities) else 'NULL'
		if ent == 'agg':
			aggregation['aggregate_functions'] = entities[i]['value']
			return aggregation, i
		else:
			return aggregation, i - 1
	else:
		raise NotImplementedError("get_aggregation should be used for agg and fact only")


# Function to get fact_condition from entities array(sorted)
# [{'confidence': 0.98031535130008, 'end': 4, 'entity': 'selection', 'extractor': 'CRFEntityExtractor',
#  'processors': ['EntitySynonymMapper'], 'start': 0, 'value': 'top'},
# {'confidence': 0.9260231614421714, 'end': 13, 'entity': 'adject', 'extractor': 'CRFEntityExtractor',
#  'processors': ['EntitySynonymMapper'], 'start': 5, 'value': 'CustomerName'},
# {'confidence': 0.985661558719627, 'end': 26, 'entity': 'fact', 'extractor': 'CRFEntityExtractor',
#  'processors': ['EntitySynonymMapper'], 'start': 21, 'value': 'SalesAmount'},
# {'confidence': 0.8685900264418185, 'end': 39, 'entity': 'fact_condition',
#  'extractor': 'CRFEntityExtractor', 'processors': ['EntitySynonymMapper'], 'start': 27,
#  'value': 'greater_than'},
# {'confidence': nan, 'end': 45, 'entity': 'CARDINAL', 'extractor': 'SpacyEntityExtractor',
#  'processors': nan, 'start': 27, 'value': 'greater than 50000'}]
# ------------------------------- TO --------------------------------------------
# {'aggregation': {'SalesAmount': ['sum']},
# 'conditions': [{'fact_name': 'SalesAmount sum', 'conditions': 'greater_than', 'fact_value': 50000.0}]}
def get_fact_condition_formatted(entities, intent):
	fact_conditions = []
	i = 0
	while i < len(entities):
		if entities[i]['entity'] in ('agg', 'fact'):
			aggregation, i = get_aggregation(entities, i)
			fact_condition = {'aggregation': aggregation}
			i += 1
			ent = entities[i]['entity'] if i < len(entities) else 'NULL'
			val = entities[i]['value'] if i < len(entities) else 'NULL'
			if ent != 'fact_condition':
				i -= 1
			else:
				condition = val
				i += 1
				ent = entities[i]['entity'] if i < len(entities) else 'NULL'
				if ent in ('agg', 'fact'):
					aggregation, i = get_aggregation(entities, i)
					fact_condition['conditions'] = condition
					fact_condition['fact_value'] = aggregation
				elif ent == 'CARDINAL':
					fact_condition['conditions'] = condition
					fact_condition['fact_value'] = duckling.parse_number(entities[i]['value'])[0]['value']['value']
				else:
					i -= 1
			fact_conditions.append(fact_condition)
		elif entities[i]['entity'] == 'fact_condition':
			fact_condition = {}
			fact_condition['conditions'] = entities[i]['value']
			i += 1
			ent = entities[i]['entity'] if i < len(entities) else 'NULL'
			val = entities[i]['value'] if i < len(entities) else 'NULL'
			if ent == 'CARDINAL':
				fact_condition['fact_value'] = duckling.parse_number(val)[0]['value']['value']
			elif ent in ('agg', 'fact'):
				aggregation, i = get_aggregation(entities, i)
				fact_condition['fact_value'] = aggregation
			else:
				i -= 1
			fact_conditions.append(fact_condition)
		i += 1
	raw_fact_conditions = fact_conditions
	if not raw_fact_conditions:
		return {}

	# try to fill aggregations in raw_fact_conditions
	df = pd.DataFrame(raw_fact_conditions)

	# No fact found and condition found, fact and its condition could not be bounded
	if 'aggregation' not in df.columns:
		raise NoFactError("Facts not found! or their conditions could not bounded")

	# default condition and fact_value
	if 'conditions' not in df.columns:
		df['conditions'] = np.nan
		df['fact_value'] = np.nan

	df['aggregation'] = df['aggregation'].fillna(method='ffill').fillna(method='bfill')
	raw_fact_conditions = df.to_dict('records')

	# try to fill aggregate_function and facts
	raw_agg = [agg['aggregation'] for agg in raw_fact_conditions]
	raw_agg = fill_aggregation(raw_agg, intent)

	# raw_agg back to fact_conditions
	for i, fact_condition in enumerate(raw_fact_conditions):
		fact_condition['aggregation'] = raw_agg[i]

	facts = [cond['aggregation']['facts'] for cond in raw_fact_conditions] + [
		fact['fact_value']['facts'] if type(fact['fact_value']) == dict and 'facts' in fact['fact_value'] else np.nan
		for fact in raw_fact_conditions]

	# unique and drop na
	facts = [x for x in list(set(facts)) if x is not np.nan]

	aggregation = {fact: [] for fact in facts}
	conditions = []
	for i, cond in enumerate(raw_fact_conditions):
		if type(cond['fact_value']) == dict:
			if 'facts' not in cond['fact_value']:
				raise NoFactInOperand("Could not compare facts with multiple aggregations...")
			if 'aggregate_functions' not in cond['fact_value']:
				cond['fact_value']['aggregate_functions'] = cond['aggregation']['aggregate_functions']
			aggregation[cond['fact_value']['facts']].append(cond['fact_value']['aggregate_functions'])
			cond['fact_value'] = cond['fact_value']['facts'] + ' ' + cond['fact_value']['aggregate_functions']
		agg = cond['aggregation']
		dictionary = {'fact_name': agg['facts'] + ' ' + agg['aggregate_functions'], 'conditions': cond[
			'conditions'], 'fact_value': cond['fact_value']}
		if agg['aggregate_functions'] not in aggregation[agg['facts']]:
			aggregation[agg['facts']].append(agg['aggregate_functions'])
		if dictionary not in conditions:
			conditions.append(dictionary)

	return {'aggregation': aggregation, 'conditions': conditions}


# Function for fixing date returned by duckling for text last month to last 1 month
def fix_date_duckling(text, val):
	text_array = text.split()
	if len(text_array) == 2 and text_array[0].lower() in ('this', 'current'):
		val_from = duckling.parse_time(" ".join(text_array))[0]['value']['value']
		text_array[0] = 'next'
		val_to = duckling.parse_time(" ".join(text_array))[0]['value']['value']
		val_dict = {"to": val_to, "from": val_from}
		val = val_dict
	elif len(text_array) == 2 and text_array[0].lower() in ('last', 'next'):
		text_array.insert(1, "1")
		text = " ".join(text_array)
		val = duckling.parse_time(text)[0]['value']['value']
	return val


# Function for getting date condition from entities array (sorted)
def get_date_condition_formatted(entities):
	# First fix date for duckling
	for ent in entities:
		if ent['entity'] == 'time':
			ent['value'] = fix_date_duckling(ent['text'], ent['value'])

	date_conditions = []
	i = 0
	while i < len(entities):
		ent = entities[i]['entity'] if i < len(entities) else 'NULL'
		val = entities[i]['value'] if i < len(entities) else 'NULL'
		if ent == 'date_condition':
			date_condition = {}
			condition = val
			while ent != 'time' and i < len(entities):
				i += 1
				ent = entities[i]['entity'] if i < len(entities) else 'NULL'
				val = entities[i]['value'] if i < len(entities) else 'NULL'
			if ent == 'time':
				text = entities[i]['text'] if i < len(entities) else 'NULL'
				date_condition['date_condition'] = condition
				date_condition['text'] = text
				if type(val) == dict:
					# When any condition is None then make lesser_than_equal instead of lesser_than
					if date_condition['date_condition'] in ('lesser_than', 'greater_than'):
						date_condition['date_condition'] += '_equal'
					if val['to'] and val['from']:
						date_condition['DateRange'] = val
					if val['to']:
						date_condition['OrderDate'] = val['to']
					else:
						date_condition['OrderDate'] = val['from']
				else:
					date_condition['OrderDate'] = val
			date_conditions.append(date_condition)
		elif ent == 'time':
			date_condition = {}
			date = val
			text = entities[i]['text'] if i < len(entities) else 'NULL'
			while ent != 'date_condition' and i < len(entities):
				i += 1
				ent = entities[i]['entity'] if i < len(entities) else 'NULL'
				val = entities[i]['value'] if i < len(entities) else 'NULL'
			if ent == 'date_condition':
				date_condition['date_condition'] = val
			else:
				# default date condition when date condition not found
				date_condition['date_condition'] = 'equal_to'
			if type(date) == dict:
				# When any condition is None then make lesser_than_equal instead of lesser_than
				if date_condition['date_condition'] in ('lesser_than', 'greater_than'):
					date_condition['date_condition'] += '_equal'
				if date['to'] and date['from']:
					date_condition['DateRange'] = date
				elif date['to']:
					date_condition['OrderDate'] = date['to']
				else:
					date_condition['OrderDate'] = date['from']
			else:
				date_condition['OrderDate'] = date
			date_condition['text'] = text
			date_conditions.append(date_condition)
		i += 1

	if not date_conditions:
		return date_conditions
	formatted_date_condition = []
	for condition in date_conditions:
		# Default condition
		if 'date_condition' not in condition:
			condition['date_condition'] = 'equal_to'

		if 'DateRange' not in condition.keys():
			date = condition['OrderDate']
			date = date[0:10]
			date = datetime.strptime(date, '%Y-%m-%d')
			date_dict = {'conditions': condition['date_condition'], 'OrderDate': date}
			formatted_date_condition.append(date_dict)
		else:
			date_period = condition['DateRange']
			# Less than equal to max date and Greater than equal to min date
			if condition['date_condition'] == 'equal_to':
				date_period_to = date_period['to']
				date_period_to = date_period_to[0:10]
				date_period_to = datetime.strptime(date_period_to, '%Y-%m-%d')
				date_dict = {'conditions': 'lesser_than', 'OrderDate': date_period_to}
				formatted_date_condition.append(date_dict)

				date_period_from = date_period['from']
				date_period_from = date_period_from[0:10]
				date_period_from = datetime.strptime(date_period_from, '%Y-%m-%d')
				date_dict = {'conditions': 'greater_than_equal', 'OrderDate': date_period_from}
				formatted_date_condition.append(date_dict)

			elif condition['date_condition'] == 'greater_than' or condition['date_condition'] == 'greater_than_equal':
				date_period_to = date_period['to']
				date_period_to = date_period_to[0:10]
				date_period_to = datetime.strptime(date_period_to, '%Y-%m-%d')
				date_dict = {'conditions': 'greater_than_equal', 'OrderDate': date_period_to}
				formatted_date_condition.append(date_dict)

			elif condition['date_condition'] == 'lesser_than' or condition['date_condition'] == 'lesser_than_equal':
				date_period_from = date_period['from']
				date_period_from = date_period_from[0:10]
				date_period_from = datetime.strptime(date_period_from, '%Y-%m-%d')
				date_dict = {'conditions': 'greater_than_equal', 'OrderDate': date_period_from}
				formatted_date_condition.append(date_dict)

	return formatted_date_condition


# Function for final formatting of entities
def format_entities(entities, intent):
	# Sort Entities by their end position in the query
	formatted_entity = {'dim': [], 'graph': [], 'date_condition': [], 'fact_condition': {}, 'select_upto': [],
						'logic': [], 'dim_filters': {}, 'adject': []}
	if not entities:
		return formatted_entity
	entities_df = pd.DataFrame(entities).sort_values('end', ascending=True)
	entities = list(entities_df.T.to_dict().values())

	i = 0
	while i < len(entities):
		ent = entities[i]['entity']
		val = entities[i]['value']
		if ent in ('dim', 'graph', 'logic', 'adject'):
			formatted_entity[ent].append(val)
		elif ent in get_dimension_names():
			if ent in formatted_entity['dim_filters'].keys():
				formatted_entity['dim_filters'][ent].append(val)
			else:
				formatted_entity['dim_filters'][ent] = [val]
		elif ent == 'filter':
			filter_column = val
			prev_ent = entities[i - 1]['entity'] if i - 1 < -1 else 'NULL'
			next_ent = entities[i + 1]['entity'] if i + 1 < len(entities) else 'NULL'
			filter_value = ''
			if next_ent in ('CARDINAL', 'number'):
				filter_value = str(entities[i + 1]['value'])
			elif prev_ent in ('CARDINAL', 'number'):
				filter_value = str(entities[i - 1]['value'])
			if not filter_value:
				prev_ent = entities[i - 2]['entity'] if i - 2 < -1 else 'NULL'
				next_ent = entities[i + 2]['entity'] if i + 2 < len(entities) else 'NULL'
				if next_ent in ('CARDINAL', 'number'):
					filter_value = str(entities[i + 2]['value'])
				elif prev_ent in ('CARDINAL', 'number'):
					filter_value = str(entities[i - 2]['value'])

			if filter_value:
				if filter_column in formatted_entity['dim_filters'].keys():
					formatted_entity['dim_filters'][filter_column].append(filter_value)
				else:
					formatted_entity['dim_filters'][filter_column] = [filter_value]

		elif ent == 'selection':
			upto = 1
			prev_ent = entities[i - 1]['entity'] if i - 1 < -1 else 'NULL'
			next_ent = entities[i + 1]['entity'] if i + 1 < len(entities) else 'NULL'

			if next_ent == 'CARDINAL':
				upto = int(duckling.parse_number(entities[i + 1]['value'])[0]['value']['value'])
			elif prev_ent == 'CARDINAL':
				upto = int(duckling.parse_number(entities[i - 1]['value'])[0]['value']['value'])

			formatted_entity['select_upto'].append({'selection': val, 'upto': upto})
		i += 1
	formatted_entity['fact_condition'] = get_fact_condition_formatted(entities, intent)
	formatted_entity['date_condition'] = get_date_condition_formatted(entities)
	return formatted_entity


def convert_text_md_format(text, entities):
	if not entities:
		return text
	length_to_add = 0
	for entity in entities:
		if entity['entity'] not in ('ORG', 'PERSON', 'CARDINAL', 'DATE', 'NORP', 'FAC', 'LOC', 'PRODUCT', 'EVENT',
									'LANGUAGE', 'LAW', 'WORK_OF_ART', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY',
									'ORDINAL', 'GPE', 'time', 'number'):
			start = entity['start'] + length_to_add
			end = entity['end'] + length_to_add
			value = entity['value']
			ent = entity['entity']
			val_ent = ent + ":" + value
			prev = text[start:end]
			new = "[" + prev + "]" + "(" + val_ent + ")"
			text = text[:start] + new + text[end:]
			length_to_add += len(new) - len(prev)
	return text


def read_nlu_data(path):
	td = training_data.load_data(path)
	output = td.as_json(indent=2)

	json_data = json.loads(output)

	intents = []
	for d in json_data['rasa_nlu_data']['common_examples']:
		intents.append({'intent': d['intent'], 'text': convert_text_md_format(d['text'], d.get('entities'))})

	intent_dict = {}
	for example in intents:
		if example['intent'] in intent_dict.keys():
			intent_dict[example['intent']].append(example['text'])
		else:
			intent_dict[example['intent']] = [example['text']]

	lookup_dict = {val['name']: val['elements'] for val in json_data['rasa_nlu_data']['lookup_tables']}
	synonym_dict = {val['value']: val['synonyms'] for val in json_data['rasa_nlu_data']['entity_synonyms']}

	return {'intent': intent_dict, 'lookup': lookup_dict, 'synonym': synonym_dict}


def save_nlu_data(data, path, append=True):
	write_mode = 'w'
	if append:
		write_mode = 'a'
	nlu_text = ""
	with open(path, write_mode) as nlu_data:
		for intent, texts in data['intent'].items():
			nlu_text += '\n## intent:' + intent + '\n'
			for text in texts:
				nlu_text += '- ' + text + '\n'

		for intent, texts in data['lookup'].items():
			nlu_text += '\n## lookup:' + intent + '\n'
			for text in texts:
				nlu_text += '- ' + text + '\n'

		for intent, texts in data['synonym'].items():
			nlu_text += '\n## synonym:' + intent + '\n'
			for text in texts:
				nlu_text += '- ' + text + '\n'

		nlu_data.write(nlu_text)

	train(RASA_CONFIG_PATH, RASA_NLU_DATA_PATH, RASA_MODEL_SAVE_PATH, 'current', 'model')
	global interpreter
	interpreter = Interpreter.load(NLU_MODEL_PATH)


def get_nlu_parameters(text):
	return interpreter.parse(text)


def get_dimension_names():
	return ['PurchaseOrderID', 'EmployeeName', 'JobTitle', 'DepartmentName', 'ProductName', 'ProductNumber', 'Status',
			'ProductSubcategoryName', 'ProductCategoryName', 'ShipMethodName', 'VendorAccountNumber', 'VendorName',
			'VendorCreditRating', 'OrderDate', 'Month', 'Year', 'MonthYear', 'Quarter', 'QuarterYear']


if __name__ == '__main__':
	text = input("Enter Query /stop to stop\n->")
	while text != '/stop':
		parameters = interpreter.parse(text)
		print(parameters)
		formatted_parameters = convert_text_md_format(parameters['text'], parameters['entities'])
		print(formatted_parameters)
		text = input("Enter Query /stop to stop\n->")
