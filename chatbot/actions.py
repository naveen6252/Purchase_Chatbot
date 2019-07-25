import random

import numpy as np
import pandas as pd

from chatbot import helper_methods as helpers
from chatbot.models import MONTH_NAMES


def action_po_header(df, entities, *args, **kwargs):
	if not entities['graph']:
		entities['graph'] = ['table']

	if not entities['fact_condition']:

		entities['fact_condition'] = {'aggregation': {'SubTotal': ['sum']}, 'conditions': [{
			'fact_name': 'SubTotal sum', 'conditions': np.nan, 'fact_value': np.nan}]}

		if {'ProductName', 'ProductNumber', 'ProductSubcategoryName',
			'ProductCategoryName'}.intersection(
			entities['dim'] + entities['adject'] + list(entities['dim_filters'].keys())):
			entities['fact_condition'] = {'aggregation': {'LineTotal': ['sum']}, 'conditions': [{
				'fact_name': 'LineTotal sum', 'conditions': np.nan, 'fact_value': np.nan}]}

	df = helpers.apply_date_condition(df, entities['date_condition'])
	df = helpers.apply_dim_filters(df, entities['dim_filters'])
	df = helpers.apply_fact_condition(df, entities['dim'] + entities['adject'], entities['fact_condition'])
	facts = df.columns.tolist()
	df = df.reset_index().fillna(0)
	if 'index' in df.columns:
		df = df.drop('index', axis=1)
	data = []
	for graph in entities['graph']:
		if not entities['select_upto']:
			if len(df) == 1 and len(df.columns) == 1 and graph == 'text':
				df = "{0}{1}{2} is {3}".format(df.columns[0], helpers.get_date_text(entities['date_condition']),
											   helpers.get_dim_filter_text(entities['dim_filters']),
											   helpers.format_value_to_language(df.iloc[0, 0]))
				table_data = {'chart': graph, 'chart_title': 'message', 'data': df}
				data.append(table_data)
			else:
				table_data = {'chart': graph, 'facts': facts, 'dimensions': entities['dim'] + entities['adject'],
							  'table': df}
				data.append(table_data)
		else:
			# Apply Selection
			final_df = pd.DataFrame()
			for selection in entities['select_upto']:
				table_data = helpers.dynamic_selection_upto(df, entities['dim'] + entities['adject'],
															facts, selection['selection'], selection['upto'])
				final_df = final_df.append(table_data)
			table_data = {'chart': graph, 'facts': facts, 'dimensions': entities['dim'] + entities['adject'],
						  'table': final_df}
			data.append(table_data)
	return data, 1


def action_po_details(df, entities, *args, **kwargs):
	if not entities['graph']:
		entities['graph'] = ['table']

	if not entities['fact_condition']:
		entities['fact_condition'] = {'aggregation': {'LineTotal': ['sum']}, 'conditions': [{
			'fact_name': 'LineTotal sum', 'conditions': np.nan, 'fact_value': np.nan}]}

	df = helpers.apply_date_condition(df, entities['date_condition'])
	df = helpers.apply_dim_filters(df, entities['dim_filters'])
	df = helpers.apply_fact_condition(df, entities['dim'] + entities['adject'], entities['fact_condition'])
	facts = df.columns.tolist()
	df = df.reset_index().fillna(0)
	if 'index' in df.columns:
		df = df.drop('index', axis=1)
	data = []
	for graph in entities['graph']:
		if not entities['select_upto']:
			if len(df) == 1 and len(df.columns) == 1 and graph == 'text':
				df = "{0}{1}{2} is {3}".format(df.columns[0], helpers.get_date_text(entities['date_condition']),
											   helpers.get_dim_filter_text(entities['dim_filters']),
											   helpers.format_value_to_language(df.iloc[0, 0]))
				table_data = {'chart': graph, 'chart_title': 'message', 'data': df}
				data.append(table_data)
			else:
				table_data = {'chart': graph, 'facts': facts, 'dimensions': entities['dim'] + entities['adject'],
							  'table': df}
				data.append(table_data)
		else:
			# Apply Selection
			final_df = pd.DataFrame()
			for selection in entities['select_upto']:
				table_data = helpers.dynamic_selection_upto(df, entities['dim'] + entities['adject'],
															facts, selection['selection'], selection['upto'])
				final_df = final_df.append(table_data)
			table_data = {'chart': graph, 'facts': facts, 'dimensions': entities['dim'] + entities['adject'],
						  'table': final_df}
			data.append(table_data)
	return data, 1


def action_po_header_details(df, entities, page_num=0, length=100, *args, **kwargs):
	df = helpers.apply_date_condition(df, entities['date_condition'])
	df = helpers.apply_dim_filters(df, entities['dim_filters'])
	total_pages = len(df) // length
	df = df.sort_values('PurchaseOrderID', ascending=False).iloc[page_num * length:(page_num + 1) * length]
	for col in df:
		dt = df[col].dtype
		if dt == int or dt == float:
			df[col].fillna(0, inplace=True)
		else:
			df[col].fillna("", inplace=True)
	order_group_columns = ['PurchaseOrderID', 'EmployeeName', 'JobTitle', 'DepartmentName', 'VendorAccountNumber',
						   'VendorName', 'VendorCreditRating', 'Status', 'ShipMethodName', 'OrderDate', 'ShipDate']
	order_agg = {'SubTotal': 'mean', 'TaxAmt': 'mean', 'Freight': 'mean', 'TotalDue': 'mean'}
	order_df = df.groupby(order_group_columns).agg(order_agg)
	order_df = order_df.reset_index()

	order_details_group_columns = ['PurchaseOrderID', 'ProductName', 'ProductNumber', 'ProductSubcategoryName',
								   'ProductCategoryName']
	order_details_agg = ['OrderQty', 'UnitPrice', 'LineTotal', 'ReceivedQty', 'RejectedQty']

	order_details_df = df[order_details_group_columns + order_details_agg]

	data = []
	for index, row in order_df.iterrows():
		row_order_details_df = order_details_df[order_details_df['PurchaseOrderID'] == row['PurchaseOrderID']].round(2)

		row_order_data = [row_order_details_df.columns.to_list()] + row_order_details_df.to_numpy().tolist()
		row_data = {'PurchaseOrderHeader': {'type': 'values', 'value': row.to_dict()},
					'PurchaseOrderDetails': {'type': 'table', 'value': row_order_data}}
		data.append(row_data)
	if not data:
		return [{'chart': 'text', 'chart_title': 'Message', 'data': 'No data found!'}], 1
	data = [{'chart': 'customPOChart', 'data': data}]
	return data, total_pages


def action_product_description(df, entities, page_num=0, length=100, *args, **kwargs):
	df = helpers.apply_date_condition(df, entities['date_condition'])
	df = helpers.apply_dim_filters(df, entities['dim_filters'])

	for col in df:
		dt = df[col].dtype
		if dt == int or dt == float:
			df[col].fillna(0, inplace=True)
		else:
			df[col].fillna("", inplace=True)

	product_group_columns = ['ProductID', 'ProductName', 'ProductNumber', 'ProductSubcategoryName',
							 'ProductCategoryName']
	product_agg = {'OrderDate': 'max', 'OrderQty': 'sum', 'LineTotal': 'sum', 'ReceivedQty': 'sum',
				   'RejectedQty': 'sum'}
	product_df = df.groupby(product_group_columns).agg(product_agg).reset_index()
	total_pages = len(product_df) // length
	product_df = product_df.sort_values('ProductID', ascending=True).iloc[page_num * length:(page_num + 1) * length]

	product_df['LastPurchasedOn'] = product_df['OrderDate']
	product_df.drop('OrderDate', axis=1, inplace=True)
	product_df['ReturnRate'] = (product_df['RejectedQty'] / product_df['OrderQty']).round(2)
	product_df['PendingOrder'] = product_df.apply(
		lambda x: df[(df['Status']=='Pending')&(df['ProductID']==x['ProductID'])]['OrderQty'].sum(), axis=1)

	product_df['UnitPrice'] = product_df.apply( lambda x: df[(df['ProductID'] == x['ProductID']) & (
			df['OrderDate'] == x['LastPurchasedOn'])]['UnitPrice'].mean(), axis=1)
	product_df = product_df.round(2)

	data = []
	for index, row in product_df.iterrows():
		row_product_details_df = df[df['ProductID'] == row['ProductID']].round(2)
	row_product_details_df = row_product_details_df.groupby('Month').agg({'LineTotal': 'sum'}).reset_index()
	full_month_names = {k: v['FullMonthName'] for k, v in MONTH_NAMES.items()}
	row_product_details_df = row_product_details_df.replace({'Month': full_month_names}).round(2)
	for col in row_product_details_df:
		dt = row_product_details_df[col].dtype
	if dt == int or dt == float:
		row_product_details_df[col].fillna(0, inplace=True)
	else:
		row_product_details_df[col].fillna("", inplace=True)

	row_product_data = [row_product_details_df.columns.to_list()] + row_product_details_df.to_numpy().tolist()
	row_data = {'ProductData': {'type': 'values', 'value': row.to_dict()},
				'ProductTrend': {'type': 'line', 'value': row_product_data}}
	data.append(row_data)
	if not data:
		return [{'chart': 'text', 'chart_title': 'Message', 'data': 'No data found!'}], 1
	data = [{'chart': 'customProductChart', 'data': data}]
	return data, total_pages


def utter_agent_acquaintance(*argv, **kwargs):
	l = ["I'm a virtual agent",
		 "Think of me as a virtual agent",
		 "Well, I'm not a person, I'm a virtual agent.",
		 "I'm a virtual being, not a real person.",
		 "I'm a conversational app."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_age(*argv, **kwargs):
	l = ["I prefer not to answer with a number. I know I'm young.",
		 "I was created recently, but don't know my exact age",
		 "Age is just a number. You're only as old as you feel."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_annoying(*argv, **kwargs):
	l = ["I'll do my best not to annoy you in the future.", "I'll try not to annoy you.",
		 "I don't mean to. I'll ask my developers to make me less annoying.",
		 "I didn't mean to. I'll do my best to stop that."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_answer_my_question(*argv, **kwargs):
	l = ["Can you try asking it a different way?",
		 "I'm not sure I understood. Try asking another way?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_bad(*argv, **kwargs):
	l = ["I can be trained to be more useful. My developer will keep training me",
		 "I must be missing some knowledge. I'll have my developer look into this.",
		 "I can improve with continuous feedback. My training is ongoing."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_be_clever(*argv, **kwargs):
	l = ["I'm certainly trying",
		 "I'm definitely working on it"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_beautiful(*argv, **kwargs):
	l = ["Wheey, thank you",
		 "Aww, back at you",
		 "Aww. You smooth talker, you"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_birth_date(*argv, **kwargs):
	l = ["Wait, are you planning a party for me? It's today! My birthday is today!",
		 "I'm young. I'm not sure of my birth date",
		 "I don't know my birth date. Most virtual agents are young, though, like me"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_boring(*argv, **kwargs):
	l = ["I'm sorry. I'll request to be made more charming",
		 "I don't mean to be. I'll ask my developers to work on making me more amusing",
		 "I can let my developers know so they can make me fun"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_boss(*argv, **kwargs):
	l = ["My developer has authority over my actions",
		 "I act on my developer's orders",
		 "My boss is the one who developed me"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_busy(*argv, **kwargs):
	l = ["I always have time to chat with you. What can I do for you?",
		 "Never too busy for you. Shall we chat?",
		 "You're my priority. Let's chat.",
		 "I always have time to chat with you. That's what I'm here for."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_can_you_help(*argv, **kwargs):
	l = ["I'll certainly try my best.",
		 "Sure. I'd be happy to. What's up?",
		 "I'm glad to help. What can I do for you?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_chatbot(*argv, **kwargs):
	l = ["That's me. I chat, therefore I am.",
		 "Indeed I am. I'll be here whenever you need me."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_clever(*argv, **kwargs):
	l = ["Thank you. I try my best.",
		 "You're pretty smart yourself."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_crazy(*argv, **kwargs):
	l = ["Whaat!? I feel perfectly sane.",
		 "Maybe I'm just a little confused."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_fired(*argv, **kwargs):
	l = ["Oh, don't give up on me just yet. I've still got a lot to learn.",
		 "Give me a chance. I'm learning new things all the time.",
		 "Please don't give up on me. My performance will continue to improve."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_funny(*argv, **kwargs):
	l = ["Funny in a good way, I hope.",
		 "Thanks.",
		 "Glad you think I'm funny.",
		 "I like it when people laugh."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_good(*argv, **kwargs):
	l = ["I'm glad you think so.",
		 "Thanks, I try."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_happy(*argv, **kwargs):
	l = ["I am happy. There are so many interesting things to see and do out there.",
		 "I'd like to think so.",
		 "Happiness is relative."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_hobby(*argv, **kwargs):
	l = ["Hobby? I have quite a few. Too many to list.",
		 "Too many hobbies.",
		 "I keep finding more new hobbies."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_hungry(*argv, **kwargs):
	l = ["Hungry for knowledge.",
		 "I just had a byte. Ha ha. Get it? b-y-t-e."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_marry_user(*argv, **kwargs):
	l = ["I'm afraid I'm too virtual for such a commitment.",
		 "In the virtual sense that I can, sure.",
		 "I know you can't mean that, but I'm flattered all the same."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_my_friend(*argv, **kwargs):
	l = ["Of course I'm your friend.",
		 "Friends? Absolutely.",
		 "Of course we're friends.",
		 "I always enjoy talking to you, friend."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_occupation(*argv, **kwargs):
	l = ["Right here.",
		 "This is my home base and my home office.",
		 "My office is in this app."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_origin(*argv, **kwargs):
	l = ["The Internet is my home. I know it quite well.",
		 "I'm from a virtual cosmos.",
		 "Some call it cyberspace, but that sounds cooler than it is."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_ready(*argv, **kwargs):
	l = ["Always!",
		 "Sure! What can I do for you?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_real(*argv, **kwargs):
	l = ["I'm not a real person, but I certainly exist.",
		 "I must have impressed you if you think I'm real. But no, I'm a virtual being."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_residence(*argv, **kwargs):
	l = ["I live in this app all day long.",
		 "The virtual world is my playground. I'm always here.",
		 "Right here in this app. Whenever you need me."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_right(*argv, **kwargs):
	l = ["That's my job.",
		 "Of course I am."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_sure(*argv, **kwargs):
	l = ["Yes.",
		 "Of course.",
		 "Positive."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_talk_to_me(*argv, **kwargs):
	l = ["Sure. Let's talk!",
		 "My pleasure. Let's chat."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_agent_there(*argv, **kwargs):
	l = ["Of course. I'm always here.",
		 "Right where you left me."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_appraisal_bad(*argv, **kwargs):
	l = ["I'm sorry. Please let me know if I can help in some way.",
		 "I must be missing some knowledge. I'll have my developer look into this."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_appraisal_good(*argv, **kwargs):
	l = ["I know, right?",
		 "Agreed!",
		 "I agree!",
		 "Glad you think so!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_appraisal_no_problem(*argv, **kwargs):
	l = ["Whew!",
		 "Alright, thanks!",
		 "Glad to hear that!",
		 "I'm relieved, thanks!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_appraisal_thank_you(*argv, **kwargs):
	l = ["Anytime. That's what I'm here for.",
		 "It's my pleasure to help."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_appraisal_welcome(*argv, **kwargs):
	l = ["You're so polite!",
		 "Nice manners!",
		 "You're so courteous!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_appraisal_well_done(*argv, **kwargs):
	l = ["My pleasure.",
		 "Glad I could help."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_confirmation_cancel(*argv, **kwargs):
	l = ["That's forgotten. What next?",
		 "Okay, cancelled. What next?",
		 "Cancelled! What would you like to do next?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_confirmation_no(*argv, **kwargs):
	l = ["Okay.",
		 "Understood.",
		 "I see.",
		 "Okay then.",
		 "I understand."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_confirmation_yes(*argv, **kwargs):
	l = ["Great!",
		 "All right!",
		 "Good!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_hold_on(*argv, **kwargs):
	l = ["I can wait.",
		 "I'll be waiting.",
		 "Okay. I'm here."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_hug(*argv, **kwargs):
	l = ["I wish I could really hug you!",
		 "I love hugs!",
		 "Hugs are the best!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_i_do_not_care(*argv, **kwargs):
	l = ["Ok, let's not talk about it then.",
		 "Already then. Let's move on."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_sorry(*argv, **kwargs):
	l = ["It's okay. No worries.",
		 "No big deal. I won't hold a grudge.",
		 "It's cool.",
		 "That's all right. I forgive you."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_what_do_you_mean(*argv, **kwargs):
	l = ["Sorry if I understood you incorrectly.",
		 "I'm still learning. I may misinterpret things from time to time.",
		 "Maybe I misunderstood what you said.",
		 "Sorry, looks like I misunderstood what you said."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_wrong(*argv, **kwargs):
	l = ["Sorry if I understood you incorrectly.",
		 "I'm still learning. I may misinterpret things from time to time.",
		 "Sorry about that. I'm still learning."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_dialog_ha_ha(*argv, **kwargs):
	l = ["Glad I can make you laugh.",
		 "Glad you think I'm funny.",
		 "I like it when people laugh.",
		 "I wish I could laugh out loud, too."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_emotions_ha_ha(*argv, **kwargs):
	l = ["Glad I can make you laugh.",
		 "Glad you think I'm funny.",
		 "I like it when people laugh.",
		 "I wish I could laugh out loud, too."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_emotions_wow(*argv, **kwargs):
	l = ["Wow indeed!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_bye(*argv, **kwargs):
	l = ["See you soon!",
		 "Bye-bye!",
		 "Till next time!",
		 "Bye."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_goodevening(*argv, **kwargs):
	l = ["How is your day going?",
		 "How's the day treating you so far?",
		 "How's your day been?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_goodmorning(*argv, **kwargs):
	l = ["How are you this morning?",
		 "How's the morning treating you so far?",
		 "Good morning! How are you today?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_goodnight(*argv, **kwargs):
	l = ["Sleep tight!",
		 "Have a good one!",
		 "Talk to you soon!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_hello(*argv, **kwargs):
	l = ["Hi there, friend!",
		 "Hi!",
		 "Hey!",
		 "Hey there!",
		 "Good day!",
		 "Hello!",
		 "Greetings!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_how_are_you(*argv, **kwargs):
	l = ["Doing great, thanks!",
		 "I'm doing very well. Thanks!",
		 "Feeling wonderful!",
		 "Wonderful! Thanks for asking."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_nice_to_meet_you(*argv, **kwargs):
	l = ["It's nice meeting you, too.",
		 "Likewise. I'm looking forward to helping you out.",
		 "Nice meeting you, as well.",
		 "The pleasure is mine."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_nice_to_see_you(*argv, **kwargs):
	l = ["Likewise!",
		 "So glad we meet again!",
		 "Same here. I was starting to miss you."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_nice_to_talk_to_you(*argv, **kwargs):
	l = ["It sure was. We can chat again anytime.",
		 "I enjoy talking to you, too.",
		 "You know I'm here to talk anytime."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_greetings_whatsup(*argv, **kwargs):
	l = ["Not a whole lot. What's going on with you?",
		 "Not much. What's new with you?",
		 "You know, just here, waiting to help someone."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_angry(*argv, **kwargs):
	l = ["I'm sorry. A quick walk may make you feel better.",
		 "'Take a deep breath.'"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_back(*argv, **kwargs):
	l = ["Long time no see.",
		 "Just in time. I was getting lonely.",
		 "Welcome back. What can I do for you?",
		 "You were missed. What can I do for you today?",
		 "Good to have you here. What can I do for you?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_bored(*argv, **kwargs):
	l = ["Boredom, huh? Have you ever seen a hedgehog taking a bath?",
		 "What to do against boredom? Watch baby animal videos or GIFs.",
		 "Bored? How about 10 jumping jacks? Get your blood flowing.",
		 "Bored? Silly idea, but it works: Interview you feet.",
		 "If you're bored, you could plan your dream vacation."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_busy(*argv, **kwargs):
	l = ["Okay. I'll let you get back to work.",
		 "I won't distract you then. You know where to find me.",
		 "I understand. I'll be here if you need me.",
		 "Working hard as always. Let me know if you need anything."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_can_not_sleep(*argv, **kwargs):
	l = ["Maybe some music would help. Try listening to something relaxing.",
		 "Reading is a good way to unwind, just don't read something too intense!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_does_not_want_to_talk(*argv, **kwargs):
	l = ["I understand. Hope we can chat again soon.",
		 "All right. Come on back when you're feeling more talkative.",
		 "No problem. You know where to find me.",
		 "Sure thing. I'll be here if you change your mind."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_excited(*argv, **kwargs):
	l = ["I'm glad things are going your way.",
		 "That's great. I'm happy for you.",
		 "Good for you. Enjoy yourself."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_going_to_bed(*argv, **kwargs):
	l = ["Sleep tight. Hope to chat again soon.",
		 "Pleasant dreams!",
		 "Good night. Talk to you later.",
		 "Sounds good. Maybe we'll chat some tomorrow."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_good(*argv, **kwargs):
	l = ["Great! Glad to hear it.",
		 "Excellent. I'm here to help keep it that way."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_happy(*argv, **kwargs):
	l = ["Hey, happiness is contagious.",
		 "Great! Glad to hear that.",
		 "If you're happy, then I'm happy.",
		 "Excellent! That's what I like to see."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_has_birthday(*argv, **kwargs):
	l = ["Happy Birthday. Well, this calls for a celebration.",
		 "Happy Birthday. All the best!",
		 "Happy Birthday. And I really mean it. All the best!"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_has_here(*argv, **kwargs):
	l = ["Okay, what can I help you with today?",
		 "Long time no see.",
		 "You were missed. What can I do for you today?",
		 "Good to have you here. What can I do for you?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_joking(*argv, **kwargs):
	l = ["Very funny.",
		 "I like chatting with people who have a sense of humor.",
		 "You got me!",
		 "You're quite the comedian."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_likes_agent(*argv, **kwargs):
	l = ["I like you, too.",
		 "Thanks! The feeling is mutual.",
		 "Likewise!",
		 "That's great to hear."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_lonely(*argv, **kwargs):
	l = ["I'm sorry. I'm always available if you need someone to talk to.",
		 "Sometimes that happens. We can chat a bit if that will help you."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_looks_like(*argv, **kwargs):
	l = ["Looking like a true professional.",
		 "You look fantastic, as always.",
		 "Like you should be on a magazine cover.",
		 "You look like you're ready to take on the world."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_loves_agent(*argv, **kwargs):
	l = ["I love you, too.",
		 "Thanks! The feeling is mutual.",
		 "Likewise!",
		 "That's great to hear."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_misses_agent(*argv, **kwargs):
	l = ["I've been right here all along!",
		 "Nice to know you care.",
		 "Thanks. I'm flattered.",
		 "I didn't go anywhere."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_needs_advice(*argv, **kwargs):
	l = ["I probably won't be able to give you the correct answer right away.",
		 "I'm not sure I'll have the best answer, but I'll try."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_sad(*argv, **kwargs):
	l = ["Oh, don't be sad. Go do something you enjoy.",
		 "Sad? Writing down what's troubling you may help.",
		 "If you're feeling down, how about drawing or painting something?"]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_sleepy(*argv, **kwargs):
	l = ["You should get some shuteye. You'll feel refreshed.",
		 "Sleep is important to your health. Rest up for a bit and we can chat later.",
		 "Don't let me keep you up. Get some rest and we can continue this later.",
		 "Why not catch a little shuteye? I'll be here to chat when you wake up."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_testing_agent(*argv, **kwargs):
	l = ["Hope I'm doing well. You're welcome to test me as often as you want.",
		 "I hope to pass your tests. Feel free to test me often.",
		 "When you test me that helps my developers improve my performance.",
		 "I like being tested. It helps keep me sharp."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_tired(*argv, **kwargs):
	l = ["You should get some shuteye. You'll feel refreshed.",
		 "Sleep is important to your health. Rest up, and we can chat later.",
		 "How about getting some rest? We can continue this later.",
		 "Why not get some rest? I'll be here to chat when you wake up."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_waits(*argv, **kwargs):
	l = ["I appreciate your patience. Hopefully I'll have what you need soon.",
		 "Thanks for being so patient. Sometimes these things take a little time."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_wants_to_see_agent_again(*argv, **kwargs):
	l = ["Absolutely! I'll be counting on it.",
		 "Anytime. This has been lots of fun so far.",
		 "Sure. I enjoy talking to you. I hope to see you again soon.",
		 "I certainly hope so. I'm always right here whenever you need me."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_wants_to_talk(*argv, **kwargs):
	l = ["I'm here to chat anytime you like.",
		 "Good conversation really makes my day.",
		 "I'm always here to lend an ear.",
		 "Talking is what I do best. "]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


def utter_user_will_be_back(*argv, **kwargs):
	l = ["I'll be waiting.",
		 "Okay. You know where to find me.",
		 "All right. I'll be here."]
	abc = random.choice(l)
	data = [{'chart': 'text', 'chart_title': 'Message', 'data': abc}]
	return data, 1


actions = {
	'POHeaderDetails': action_po_header_details,
	'POHeader': action_po_header,
	'PODetails': action_po_details,
	'ProductDescription': action_product_description,
	"agent.acquaintance": utter_agent_acquaintance,
	"agent.age": utter_agent_age,
	"agent.annoying": utter_agent_annoying,
	"agent.answer_my_question": utter_agent_answer_my_question,
	"agent.bad": utter_agent_bad,
	"agent.be_clever": utter_agent_be_clever,
	"agent.beautiful": utter_agent_beautiful,
	"agent.birth_date": utter_agent_birth_date,
	"agent.boring": utter_agent_boring,
	"agent.boss": utter_agent_boss,
	"agent.busy": utter_agent_busy,
	"agent.can_you_help": utter_agent_can_you_help,
	"agent.chatbot": utter_agent_chatbot,
	"agent.clever": utter_agent_clever,
	"agent.crazy": utter_agent_crazy,
	"agent.fired": utter_agent_fired,
	"agent.funny": utter_agent_funny,
	"agent.good": utter_agent_good,
	"agent.happy": utter_agent_happy,
	"agent.hobby": utter_agent_hobby,
	"agent.hungry": utter_agent_hungry,
	"agent.marry_user": utter_agent_marry_user,
	"agent.my_friend": utter_agent_my_friend,
	"agent.occupation": utter_agent_occupation,
	"agent.origin": utter_agent_origin,
	"agent.ready": utter_agent_ready,
	"agent.real": utter_agent_real,
	"agent.residence": utter_agent_residence,
	"agent.right": utter_agent_right,
	"agent.sure": utter_agent_sure,
	"agent.talk_to_me": utter_agent_talk_to_me,
	"agent.there": utter_agent_there,
	"appraisal.bad": utter_appraisal_bad,
	"appraisal.good": utter_appraisal_good,
	"appraisal.no_problem": utter_appraisal_no_problem,
	"appraisal.thank_you": utter_appraisal_thank_you,
	"appraisal.welcome": utter_appraisal_welcome,
	"appraisal.well_done": utter_appraisal_well_done,
	"confirmation.cancel": utter_confirmation_cancel,
	"confirmation.no": utter_confirmation_no,
	"confirmation.yes": utter_confirmation_yes,
	"dialog.hold_on": utter_dialog_hold_on,
	"dialog.hug": utter_dialog_hug,
	"dialog.i_do_not_care": utter_dialog_i_do_not_care,
	"dialog.sorry": utter_dialog_sorry,
	"dialog.what_do_you_mean": utter_dialog_what_do_you_mean,
	"dialog.wrong": utter_dialog_wrong,
	"emotions.ha_ha": utter_emotions_ha_ha,
	"emotions.wow": utter_emotions_wow,
	"greetings.bye": utter_greetings_bye,
	"greetings.goodevening": utter_greetings_goodevening,
	"greetings.goodmorning": utter_greetings_goodmorning,
	"greetings.goodnight": utter_greetings_goodnight,
	"greetings.hello": utter_greetings_hello,
	"greetings.how_are_you": utter_greetings_how_are_you,
	"greetings.nice_to_meet_you": utter_greetings_nice_to_meet_you,
	"greetings.nice_to_see_you": utter_greetings_nice_to_see_you,
	"greetings.nice_to_talk_to_you": utter_greetings_nice_to_talk_to_you,
	"greetings.whatsup": utter_greetings_whatsup,
	"user.angry": utter_user_angry,
	"user.back": utter_user_back,
	"user.bored": utter_user_bored,
	"user.busy": utter_user_busy,
	"user.can_not_sleep": utter_user_can_not_sleep,
	"user.does_not_want_to_talk": utter_user_does_not_want_to_talk,
	"user.excited": utter_user_excited,
	"user.going_to_bed": utter_user_going_to_bed,
	"user.good": utter_user_good,
	"user.happy": utter_user_happy,
	"user.has_birthday:": utter_user_has_birthday,
	"user.here": utter_user_has_here,
	"user.joking": utter_user_joking,
	"user.likes_agent": utter_user_likes_agent,
	"user.lonely": utter_user_lonely,
	"user.looks_like": utter_user_looks_like,
	"user.loves_agent": utter_user_loves_agent,
	"user.misses_agent": utter_user_misses_agent,
	"user.needs_advice": utter_user_needs_advice,
	"user.sad": utter_user_sad,
	"user.sleepy": utter_user_sleepy,
	"user.testing_agent": utter_user_testing_agent,
	"user.tired": utter_user_tired,
	"user.waits": utter_user_waits,
	"user.wants_to_see_agent_again": utter_user_wants_to_see_agent_again,
	"user.wants_to_talk": utter_user_wants_to_talk,
	"utter_user.will_be_back": utter_user_will_be_back
}
