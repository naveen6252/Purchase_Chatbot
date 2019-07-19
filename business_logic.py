import pandas as pd
import numpy as np
from datetime import datetime
from chatbot import helper_methods as helpers
from dateutil import relativedelta
from custom_exceptions import NoLeftOperandInPercentage
from chatbot.models import MONTH_NAMES


# class for storing all complex business logic
# All methods should be class method and  a data frame as parameter
class BusinessLogic:

	def __init__(self, dimensions, fact_condition, date_condition, dim_filters):
		self.dimensions = dimensions
		self.fact_condition = fact_condition
		self.agg = fact_condition['aggregation']
		self.dim_filters = dim_filters
		self.date_condition = date_condition
		self.start_date = datetime.today()
		self.end_date = datetime.strptime('1899-01-01', '%Y-%m-%d')

		for cond in date_condition:
			# Use max date in date_condition for end date and min for start date
			date = cond['CalendarDate']
			if date < self.start_date:
				self.start_date = date

			if date > self.end_date:
				self.end_date = date

	def mom_facts(self, df):
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)

		final_df = pd.DataFrame()
		s_date = self.start_date
		e_date = self.end_date
		if e_date > df['CalendarDate'].max():
			# select max date of data if e_date is too large
			e_date = df['CalendarDate'].max()

		r = relativedelta.relativedelta(e_date, s_date)
		n_months = r.years * 12 + r.months
		# if there is no date or same date then make mom for last 6 months
		if n_months < 1:
			n_months = 6
			e_date = datetime.now()
			s_date = e_date - relativedelta.relativedelta(months=6)

		# show 1 extra month for current month
		for month in range(n_months + 1):
			curr_month_year = MONTH_NAMES[s_date.month]['ShortMonthName'] + '-' + str(s_date.year)
			prev_month_year = helpers.get_prev_month_year(curr_month_year)
			curr_month_facts = helpers.safe_groupby(df[df['MonthYear'] == curr_month_year], self.dimensions + [
				'MonthYear'], self.agg)
			last_month_facts = helpers.safe_groupby(df[df['MonthYear'] == prev_month_year], self.dimensions + [
				'MonthYear'], self.agg)
			if not last_month_facts.empty:
				last_month_facts.index = curr_month_facts.index

			mom_facts = (curr_month_facts / last_month_facts).fillna(
				0) if last_month_facts.empty else 100 * curr_month_facts / last_month_facts
			mom_facts = mom_facts.add_prefix("% MOM ")
			final_df = final_df.append(pd.concat([curr_month_facts, mom_facts], axis=1, sort=False))
			s_date = s_date + relativedelta.relativedelta(months=1)
		return final_df

	def qoq_facts(self, df):
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)

		final_df = pd.DataFrame()
		s_date = self.start_date
		e_date = self.end_date
		n_qtr = helpers.get_n_quarters(e_date, s_date)
		# if there is no date or same date then make qoq for last 4 quarters
		if n_qtr < 1:
			n_qtr = 4
			e_date = datetime.now()
			s_date = e_date - relativedelta.relativedelta(months=n_qtr * 3)

		# use 1 extra quarter to show current quarter facts alse
		for qtr in range(n_qtr + 1):
			curr_qtr_year = MONTH_NAMES[s_date.month]['QtrName'] + '-' + str(s_date.year)
			prev_qtr_year = helpers.get_prev_qtr_year(curr_qtr_year)
			curr_qtr_facts = helpers.safe_groupby(df[df['QuarterYear'] == curr_qtr_year], self.dimensions + [
				'QuarterYear'], self.agg)
			last_qtr_facts = helpers.safe_groupby(df[df['QuarterYear'] == prev_qtr_year], self.dimensions + [
				'QuarterYear'], self.agg)
			if not last_qtr_facts.empty:
				last_qtr_facts.index = curr_qtr_facts.index

			qoq_facts = (curr_qtr_facts / last_qtr_facts).fillna(
				0) if last_qtr_facts.empty else 100 * curr_qtr_facts / last_qtr_facts
			qoq_facts = qoq_facts.add_prefix("% QOQ ")
			final_df = final_df.append(pd.concat([curr_qtr_facts, qoq_facts], axis=1, sort=False))
			s_date = s_date + relativedelta.relativedelta(months=3)

		return final_df

	def yoy_fact(self, df):
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)

		final_df = pd.DataFrame()
		s_date = self.start_date
		e_date = self.end_date
		n_year = relativedelta.relativedelta(e_date, s_date).years

		# if there is no date or same date then make yoy for last 3 years
		if n_year <= 1:
			n_year = 3
			e_date = datetime.now()
			s_date = e_date - relativedelta.relativedelta(years=3)

		# add 1 to show current year sales also
		for year in range(n_year + 1):
			curr_year = s_date.year
			prev_year = curr_year - 1
			curr_year_facts = helpers.safe_groupby(df[df['Year'] == curr_year], self.dimensions + [
				'Year'], self.agg)
			last_year_facts = helpers.safe_groupby(df[df['Year'] == prev_year], self.dimensions + [
				'Year'], self.agg)
			if not last_year_facts.empty:
				last_year_facts.index = curr_year_facts.index
			yoy_facts = (curr_year_facts / last_year_facts).fillna(
				0) if last_year_facts.empty else 100 * curr_year_facts / last_year_facts
			yoy_facts = yoy_facts.add_prefix("% YoY ")
			final_df = final_df.append(pd.concat([curr_year_facts, yoy_facts], axis=1, sort=False))
			s_date = s_date + relativedelta.relativedelta(years=1)

		return final_df

	def mtd(self, df):
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)

		# get max date from the user query for mtd
		date = self.end_date if self.end_date > self.start_date else self.start_date
		curr_month_year = MONTH_NAMES[date.month]['ShortMonthName'] + '-' + str(date.year)
		mtd_facts = helpers.safe_groupby(df[(df['MonthYear'] == curr_month_year) & (
				df['CalendarDate'] <= date)], self.dimensions, self.agg)
		mtd_facts = mtd_facts.add_prefix(
			date.replace(day=1).strftime("%Y-%m-%d") + ' to ' + date.strftime("%Y-%m-%d") + " ")
		return mtd_facts

	def qtd(self, df):
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)

		# get max date from the user query for qtd
		date = self.end_date if self.end_date > self.start_date else self.start_date
		curr_qtr_year = MONTH_NAMES[date.month]['QtrName'] + '-' + str(date.year)
		qtd_facts = helpers.safe_groupby(df[(df['QuarterYear'] == curr_qtr_year) & (
				df['CalendarDate'] <= date)], self.dimensions, self.agg)
		qtr_first_date = datetime(date.year, (3 * int(MONTH_NAMES[date.month]['QtrName'][1:]) - 2), 1)
		qtd_facts = qtd_facts.add_prefix(
			qtr_first_date.strftime("%Y-%m-%d") + ' to ' + date.strftime("%Y-%m-%d") + " ")
		return qtd_facts

	def ytd(self, df):
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)

		# get max date from the user query for ytd
		date = self.end_date if self.end_date > self.start_date else self.start_date
		ytd_facts = helpers.safe_groupby(df[(df['Year'] == date.year) & (
				df['CalendarDate'] <= date)], self.dimensions, self.agg)
		ytd_facts = ytd_facts.add_prefix(
			date.replace(day=1, month=1).strftime("%Y-%m-%d") + ' to ' + date.strftime("%Y-%m-%d") + " ")
		return ytd_facts

	def target_achievement(self, df):
		fact_condition = self.fact_condition.copy()
		if self.dim_filters:
			df = helpers.apply_dim_filters(df, dim_filters=self.dim_filters)
		if self.date_condition:
			df = helpers.apply_date_condition(df, self.date_condition)

		# add Sales in Aggregation
		if 'SalesAmount' not in fact_condition['aggregation']:
			fact_condition['aggregation']['SalesAmount'] = ['sum']
			fact_condition['conditions'] += [
				{'fact_name': 'SalesAmount sum', 'conditions': np.nan, 'fact_value': np.nan}]

		# add Target Amount in Aggregation
		if 'TargetAmount' not in fact_condition['aggregation']:
			fact_condition['aggregation']['TargetAmount'] = fact_condition['aggregation']['SalesAmount']
			fact_condition['conditions'] += [
				{'fact_name': 'TargetAmount sum', 'conditions': np.nan, 'fact_value': np.nan}]

		# add sum to sales Amount
		if 'sum' not in fact_condition['aggregation']['SalesAmount']:
			fact_condition['aggregation']['SalesAmount'] += ['sum']
			fact_condition['conditions'] += [
				{'fact_name': 'SalesAmount sum', 'conditions': np.nan, 'fact_value': np.nan}]

		# Apply fact condition
		df = helpers.apply_fact_condition(df, self.dimensions, fact_condition)
		sale_fact_names = [c['fact_name'] for c in fact_condition['conditions'] if c['fact_name'][0:5] == 'Sales']
		target_fact_names = [c['fact_name'] for c in fact_condition['conditions'] if c['fact_name'][0:6] == 'Target']

		# target facts for 0th name
		target_facts = pd.DataFrame(100 * df[sale_fact_names[0]] / df[target_fact_names[0]])
		target_facts.columns = ["% Target Achievement"]
		# return pd.concat([df, target_facts], axis=1, sort=False)
		return target_facts

	# TODO Need to implement again for more dynamic
	def contribution(self, df):

		# Raise Error if there is no filters
		if not self.dim_filters and not self.date_condition and not self.dimensions:
			raise NoLeftOperandInPercentage(
				"Could not apply percentage without a filter! Either apply filter in dimension or date")

		all_filtered = df.copy()
		less_filtered = df.copy()
		contribution = pd.DataFrame({'Error': ["Could not applied percentage"]})

		if (self.dim_filters or self.dimensions) and self.date_condition:
			# Do not filter lowest level dimension
			all_filtered = helpers.apply_dim_filters(all_filtered, dim_filters=self.dim_filters)
			all_filtered = helpers.apply_date_condition(all_filtered, self.date_condition)
			less_filtered = helpers.apply_date_condition(less_filtered, self.date_condition)

			all_filtered = helpers.apply_fact_condition(all_filtered, self.dimensions, self.fact_condition)
			less_filtered = helpers.apply_fact_condition(less_filtered, self.dimensions[1:], self.fact_condition)

			contribution = 100 * all_filtered / less_filtered.iloc[0]
			contribution = contribution.add_prefix("% ")

		elif len(self.dim_filters.keys()) == 1 or self.dimensions:
			# Do not filter lowest level dimension
			less_dim_filters = {k: v for k, v in self.dim_filters.items() if k != list(self.dim_filters.keys())[0]}
			if not less_dim_filters:
				less_dim_filters = self.dim_filters
			all_filtered = helpers.apply_dim_filters(all_filtered, dim_filters=self.dim_filters)
			less_filtered = helpers.apply_dim_filters(less_filtered, dim_filters=less_dim_filters)
			all_filtered = helpers.apply_fact_condition(all_filtered, self.dimensions, self.fact_condition)
			less_filtered = helpers.apply_fact_condition(less_filtered, self.dimensions[1:], self.fact_condition)

			contribution = 100 * all_filtered / less_filtered.iloc[0]
			contribution = contribution.add_prefix("% ")

		elif len(self.dim_filters.keys()) > 1:
			# Do not filter lowest level dimension
			less_dim_filters = {k: v for k, v in self.dim_filters.items() if k != list(self.dim_filters.keys())[0]}
			all_filtered = helpers.apply_dim_filters(all_filtered, dim_filters=self.dim_filters)
			less_filtered = helpers.apply_dim_filters(less_filtered, dim_filters=less_dim_filters)
			all_filtered = helpers.apply_fact_condition(all_filtered, self.dimensions, self.fact_condition)
			less_filtered = helpers.apply_fact_condition(less_filtered, self.dimensions[1:], self.fact_condition)

			contribution = 100 * all_filtered / less_filtered
			contribution = contribution.add_prefix("% ")

		elif self.date_condition:
			# Do not filter first level date
			less_date_filters = self.date_condition[1:]
			more_date_filters = self.date_condition[0:1]

			if not len(self.date_condition) % 2:
				less_date_filters = self.date_condition[2:]
				more_date_filters = self.date_condition[0:2]

			all_filtered = helpers.apply_date_condition(all_filtered, more_date_filters)
			less_filtered = helpers.apply_date_condition(less_filtered, less_date_filters)

			all_filtered = helpers.apply_fact_condition(all_filtered, self.dimensions, self.fact_condition)
			less_filtered = helpers.apply_fact_condition(less_filtered, self.dimensions[1:], self.fact_condition)

			contribution = 100 * all_filtered / less_filtered
			contribution = contribution.add_prefix("% ")

		return contribution
