import os
import pandas as pd
from settings import DATA_PATH, COL_MAPPING, TABLE_MAPPING


def get_dimension_names():
	return ['EmployeeName', 'JobTitle', 'ProductName', 'ProductNumber', 'ProductSubcategoryName', 'ProductCategoryName',
			'ShipMethodName', 'VendorAccountNumber', 'VendorName', 'VendorCreditRating', 'CalendarDate',
			'Month', 'Year', 'MonthYear', 'Quarter', 'QuarterYear']


def load_data(columns):
	mapping_col_df = pd.read_csv(os.path.join(DATA_PATH, COL_MAPPING))
	table_mapping = pd.read_csv(os.path.join(DATA_PATH, TABLE_MAPPING))
	tables = list(mapping_col_df[mapping_col_df['column'].isin(columns)]['table'].unique())
	# first load fact table i.e., tables[0]
	l_table = tables[0]
	date_col = mapping_col_df[mapping_col_df['table'] == l_table]['date_col']
	date_col = eval(date_col.iloc[0]) if date_col.any() else False
	df = pd.read_csv(os.path.join(DATA_PATH, l_table), parse_dates=date_col)
	tables = tables[1:]
	for table in tables:
		date_col = mapping_col_df[mapping_col_df['table'] == table]['date_col']
		date_col = [date_col.iloc[0]] if date_col.any() else False
		temp_df = pd.read_csv(os.path.join(DATA_PATH, table), parse_dates=date_col)
		left_on = eval(table_mapping[(table_mapping['l_table'] == l_table) & (table_mapping['r_table'] == table)][
						   'l_columns'].iloc[0])
		right_on = eval(table_mapping[(table_mapping['l_table'] == l_table) & (table_mapping['r_table'] == table)][
							'r_columns'].iloc[0])
		df = pd.merge(df, temp_df, left_on=left_on, right_on=right_on, how='left')
	columns = [x for x in columns if x in df.columns]
	df = df[columns]
	return df


def get_columns_from_entities(raw_entities):
	columns = []
	for entity in raw_entities:
		if entity['entity'] in ['dim', 'fact', 'adject']:
			columns.append(entity['value'])
		# entity time for duckling pipeline
		elif entity['entity'] == 'time':
			columns.append('CalendarDate')
		elif entity['entity'] in get_dimension_names():
			columns.append(entity['entity'])
		# Load extra Columns  for Business logic
		elif entity['entity'] == 'logic':
			columns += ['SalesAmount', 'TargetAmount', 'CalendarDate', 'Month', 'Year', 'MonthYear', 'Quarter',
						'QuarterYear']
	return columns


if __name__ == '__main__':
	df = load_data(['EmployeeName'])
	print(df)
