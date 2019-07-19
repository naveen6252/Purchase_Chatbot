import pandas as pd
import numpy as np
from business_logic import BusinessLogic
from datetime import datetime
from chatbot.models import MONTH_NAMES


# function to groupby even without grouping
def safe_groupby(df, groupings, agg):
	# Do no group by same value multiple times
	used = []
	unique = [x for x in groupings if x not in used and (used.append(x) or True)]

	if unique:
		tdf = df.groupby(unique).agg(agg)
		# normalize columns
		tdf.columns = [" ".join(x) for x in tdf.columns.ravel()]

	else:
		tdf = df.copy()
		tdf['dummy_col'] = 1
		tdf = tdf.groupby('dummy_col').agg(agg)
		# normalize columns
		tdf.columns = [" ".join(x) for x in tdf.columns.ravel()]
		tdf = tdf.reset_index().drop('dummy_col', axis=1)

	return tdf


# function to format float values to million/billion
def format_value_to_language(val):
	if val > 1000000000:
		return str(round(val / 1000000000, 2)) + 'Bn'
	elif val > 1000000:
		return str(round(val / 1000000, 2)) + 'M'
	elif val > 1000:
		return str(round(val / 1000, 2)) + 'K'
	else:
		return str(round(val, 2))


def apply_condition(df, col_name, condition, condition_value):
	if col_name == 'CalendarDate' and type(condition_value) == str:
		condition_value = datetime.strptime(condition_value, "%Y-%m-%d")
	if condition == 'greater_than':
		return df[df[col_name] > condition_value]
	elif condition == 'lesser_than':
		return df[df[col_name] < condition_value]
	elif condition == 'equal_to':
		return df[df[col_name] == condition_value]
	elif condition == 'greater_than_equal':
		return df[df[col_name] >= condition_value]
	elif condition == 'lesser_than_equal':
		return df[df[col_name] <= condition_value]
	elif condition == 'in':
		return df[df[col_name].str.lower().isin([x.lower() for x in condition_value])]
	else:
		raise NotImplementedError("Condition is not defined in the code!")


def apply_date_condition(df, date_conditions):
	date_col_name = 'CalendarDate'
	for condition in date_conditions:
		df = apply_condition(df, date_col_name, condition['conditions'], condition[date_col_name])
	return df


# Function to get text from date condition
def get_date_text(date_condition):
	if not date_condition:
		return ""
	date_text = {
		'lesser_than': 'before ',
		'greater_than': 'after ',
		'lesser_than_equal': 'until ',
		'greater_than_equal': 'from ',
		'equal_to': 'for '
	}
	text = " "
	for date in date_condition:
		text += date_text.get(date['conditions']) + datetime.strftime(date['CalendarDate'], '%Y-%m-%d') + ' & '
	text = text[:-2]
	return text


# function to get text for dim filters
def get_dim_filter_text(dim_filters):
	if not dim_filters:
		return ""
	dim_filters_text = " "
	for k, v in dim_filters.items():
		dim_filters_text += "for " + ", ".join(v) + " " + k + " "
	# dim_filters_text = dim_filters_text[:-1]
	return dim_filters_text


# function to filters dimension apply when no business logic
def apply_dim_filters(df, dim_filters):
	for k, v in dim_filters.items():
		df = df[df[k].str.lower().isin([x.lower() for x in v])]
	return df


def apply_fact_condition(df, groupings, fact_conditions):
	df = safe_groupby(df, groupings, fact_conditions['aggregation'])
	for condition in fact_conditions['conditions']:
		if type(condition['fact_value']) == str:
			df = apply_condition(df, condition['fact_name'], condition['conditions'], df[condition['fact_value']])
		elif not np.isnan(condition['fact_value']):
			df = apply_condition(df, condition['fact_name'], condition['conditions'], condition['fact_value'])
	return df


def apply_business_logic(df, logic, entities):
	business_instance = BusinessLogic(entities['dim'] + entities['adject'], entities['fact_condition'],
									  entities['date_condition'], entities['dim_filters'])

	if logic == 'MOM':
		table = business_instance.mom_facts(df)
		default_graph = 'line'
		if len(table) > 60:
			default_graph = 'table'
	elif logic == 'QOQ':
		table = business_instance.qoq_facts(df)
		default_graph = 'line'
		if len(table) > 60:
			default_graph = 'table'
	elif logic == 'YOY':
		table = business_instance.yoy_fact(df)
		default_graph = 'line'
		if len(table) > 60:
			default_graph = 'table'
	elif logic == 'MTD':
		table = business_instance.mtd(df)
		default_graph = 'pie'
		if len(table) > 60:
			default_graph = 'table'
		if len(table) == 1 and len(table.columns) == 1:
			facts = table.columns.tolist()
			dim = list(table.index.names)
			table = "{0}{1}is {2}".format(str(table.columns[0])+" ", get_dim_filter_text(entities['dim_filters']),
											format_value_to_language(table.iloc[0, 0]))
			default_graph = 'text'
			return table, default_graph, facts, dim

	elif logic == 'QTD':
		table = business_instance.qtd(df)
		default_graph = 'pie'
		if len(table) > 60:
			default_graph = 'table'
		if len(table) == 1 and len(table.columns) == 1:
			facts = table.columns.tolist()
			dim = list(table.index.names)
			table = "{0}{1}is {2}".format(str(table.columns[0])+" ", get_dim_filter_text(entities['dim_filters']),
											format_value_to_language(table.iloc[0, 0]))
			default_graph = 'text'
			return table, default_graph, facts, dim
	elif logic == 'YTD':
		table = business_instance.ytd(df)
		default_graph = 'table'
		if len(table) > 60:
			default_graph = 'table'
		if len(table) == 1 and len(table.columns) == 1:
			facts = table.columns.tolist()
			dim = list(table.index.names)
			table = "{0}{1}is {2}".format(str(table.columns[0])+" ", get_dim_filter_text(entities['dim_filters']),
											format_value_to_language(table.iloc[0, 0]))
			default_graph = 'text'
			return table, default_graph, facts, dim
	elif logic == 'Target-Achievement':
		table = business_instance.target_achievement(df)
		default_graph = 'table'
		if len(table) == 1 and len(table.columns) == 1:
			facts = table.columns.tolist()
			dim = list(table.index.names)
			table = "{0}{1}{2}is {3}".format(str(table.columns[0])+" ", get_dim_filter_text(entities['dim_filters']),
												get_date_text(entities['date_condition']),
												format_value_to_language(table.iloc[0, 0]))
			default_graph = 'text'
			return table, default_graph, facts, dim
	elif logic == 'Contribution':
		table = business_instance.contribution(df)
		default_graph = 'table'
	else:
		raise NotImplementedError("Business Logic {0} not defined".format(logic))

	facts = table.columns.tolist()
	dim = list(table.index.names)
	table = table.reset_index().fillna(0)
	if 'index' in table.columns:
		table = table.drop('index', axis=1)
		dim = []
	if len(table) == 1:
		default_graph = 'table'
	if not entities['select_upto']:
		return table, default_graph, facts, dim
	# if selection exists
	final_df = pd.DataFrame()
	for selection in entities['select_upto']:
		select = selection['selection']
		upto = selection['upto']
		df = dynamic_selection_upto(table, entities['dim'] + entities['adject'], facts, select, upto)
		final_df = final_df.append(df)
	return final_df, default_graph, facts, dim


def dynamic_selection_upto(df, dimensions, facts, selection, upto):
	if not dimensions:
		return df

	if len(dimensions) < 2:
		if selection == 'top':
			return df.sort_values(facts, ascending=False).iloc[0:upto]
		else:
			return df.sort_values(facts, ascending=True).iloc[0:upto]

	final_df = pd.DataFrame()
	for gr in df[dimensions[0]].unique():
		if selection == 'top':
			final_df = final_df.append(df[df[dimensions[0]] == gr].sort_values(facts, ascending=False).iloc[0:upto])
		else:
			final_df = final_df.append(df[df[dimensions[0]] == gr].sort_values(facts, ascending=True).iloc[0:upto])
	return final_df


# method to get last MonthYear provided current MonthYear in format like 'Jan-2018'
def get_prev_month_year(curr_month_year):
	short_month_names = {k: v['ShortMonthName'] for k, v in MONTH_NAMES.items()}
	month, year = curr_month_year.split('-')
	year = int(year)
	prev_month = list(short_month_names.keys())[list(short_month_names.values()).index(month) - 1]
	prev_year = (year - 1) if prev_month == 12 else year
	return short_month_names[prev_month] + '-' + str(prev_year)


# method to get numbers of quarter between two dates
def get_n_quarters(e_date, s_date):
	e_qtr = (e_date.month - 1) // 3 + 1
	s_qtr = (s_date.month - 1) // 3 + 1
	year_qtr = (e_date.year + e_qtr / 4) - (s_date.year + s_qtr / 4)
	n_qtr = year_qtr * 4
	return int(n_qtr)


# method to get last QtrYear provided current QtrYear in format like 'Q1-2018'
def get_prev_qtr_year(curr_qtr_year):
	qtr, year = curr_qtr_year.split('-')
	qtr = int(qtr[1:2])
	year = int(year)
	prev_qtr = 4 if qtr - 1 < 1 else qtr - 1
	prev_year = year - 1 if prev_qtr == 4 else year
	return "Q" + str(prev_qtr) + '-' + str(prev_year)


if __name__ == '__main__':
	pass
