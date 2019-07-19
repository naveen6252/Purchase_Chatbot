from chatbot.actions import actions
import pandas as pd
from chatbot import entity_helpers as en_helpers, data_loader
from chatbot.entity_helpers import get_nlu_parameters
from chatbot.models import MONTH_NAMES

pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.max_columns', 10)


def get_json_from_query(query, rls_access_string):
	parameters = get_nlu_parameters(query)
	intent = parameters['intent']['name']
	entities = parameters['entities']
	entities = [{k: v for k, v in en.items() if k in ('entity', 'value', 'start', 'end', 'extractor',
													  'additional_info', 'text')} for en in entities if
				en['entity'] not in ('DATE')]
	df = data_loader.load_table_rls_filtered(entities, rls_access_string)

	# format entities after loading data
	entities = en_helpers.format_entities(entities)

	tables = actions.get(intent)(df, entities)
	final_data = {'response': []}

	for data in tables:
		if data['chart'] == 'text':
			final_data['response'].append(data)

		else:
			# Round upto 2 places for all value in table
			data['table'] = data['table'].round(2)

			# Map Month Names
			if 'Month' in data['table'].columns:
				full_month_names = {k: v['FullMonthName'] for k, v in MONTH_NAMES.items()}
				data['table'] = data['table'].replace({'Month': full_month_names})
			if 'Year' in data['table'].columns:
				data['table']['Year'] = 'Year-' + data['table']['Year'].astype(str)
			if data['chart'] == 'table':
				if len(data.get('dimensions')) == 2 and len(data['facts']) == 1:
					index_column = data.get('dimensions')[0]
					pivot_column = data.get('dimensions')[1]
					if data.get('table')[index_column].nunique() < data.get('table')[
						pivot_column].nunique():
						a = index_column
						index_column = pivot_column
						pivot_column = a

					# date dimensions should always be on pivot_column
					if index_column in ['Month', 'Year', 'MonthYear', 'Quarter', 'QuarterYear']:
						a = index_column
						index_column = pivot_column
						pivot_column = a

					if data.get('table')[pivot_column].nunique() < 15:
						data['table'] = data['table'].pivot(
							index=index_column, columns=pivot_column).reset_index().fillna(0)
						data['table'].columns = [" ".join(
							col[::-1]).strip() for col in data['table'].columns.ravel()]
						if pivot_column == 'Month':
							data['table'] = data['table'][[index_column] + [
								col_name['FullMonthName'] + " " + data['facts'][0] for col_name in
								MONTH_NAMES.values()]]

				table = [data['table'].columns.tolist()] + data['table'].to_numpy().tolist()

				table_data = {'chart': 'table', 'chart_title': 'Table', 'data': table}
				final_data['response'].append(table_data)
			else:
				dimension = data['dimensions']
				if len(data['dimensions']) > 1:
					dimension = ' Wise '.join(data['dimensions'])
					data['table'][dimension] = [' '.join(a) for a in data['table'][
						data['dimensions']].values]
					dimension = [dimension]
					data['table'] = data['table'][dimension + data['facts']]

				for fact in data['facts']:
					value_title = ""
					format_table = data['table'][dimension + [fact]]
					if format_table[fact].mean() > 1000000000:
						format_table[fact] = (format_table[fact] / 1000000000).round(2)
						value_title = "(Values in Billions)"
					elif format_table[fact].mean() > 1000000:
						format_table[fact] = (format_table[fact] / 1000000).round(2)
						value_title = "(Values in Millions)"
					elif format_table[fact].mean() > 1000:
						format_table[fact] = (format_table[fact] / 1000).round(2)
						value_title = "(Values in Thousands)"

					if not dimension:
						chart_title = fact.title()+value_title
						table = [[fact]] + [format_table[fact].tolist()]
					else:
						chart_title = " Wise ".join(data['dimensions']) + " Wise " + fact
						chart_title = chart_title.title()+value_title
						table = format_table[dimension + [fact]]
						table = [table.columns.tolist()] + table.to_numpy().tolist()
					table_data = {'chart': data['chart'], 'chart_title': chart_title, 'data': table}
					final_data['response'].append(table_data)

	return final_data, parameters


if __name__ == '__main__':
	query = input('Enter Query(/stop to stop): \n-->')
	while (query != '/stop'):
		print(get_json_from_query(query, "{}"))
		query = input('Enter Query(/stop to stop): \n-->')
