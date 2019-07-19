from chatbot import db



MONTH_NAMES = {
	1: {'FullMonthName': 'January', 'ShortMonthName': 'Jan', 'QtrName': 'Q1'},
	2: {'FullMonthName': 'February', 'ShortMonthName': 'Feb', 'QtrName': 'Q1'},
	3: {'FullMonthName': 'March', 'ShortMonthName': 'Mar', 'QtrName': 'Q1'},
	4: {'FullMonthName': 'April', 'ShortMonthName': 'Apr', 'QtrName': 'Q2'},
	5: {'FullMonthName': 'May', 'ShortMonthName': 'May', 'QtrName': 'Q2'},
	6: {'FullMonthName': 'June', 'ShortMonthName': 'Jun', 'QtrName': 'Q2'},
	7: {'FullMonthName': 'July', 'ShortMonthName': 'Jul', 'QtrName': 'Q3'},
	8: {'FullMonthName': 'August', 'ShortMonthName': 'Aug', 'QtrName': 'Q3'},
	9: {'FullMonthName': 'September', 'ShortMonthName': 'Sep', 'QtrName': 'Q3'},
	10: {'FullMonthName': 'October', 'ShortMonthName': 'Oct', 'QtrName': 'Q4'},
	11: {'FullMonthName': 'November', 'ShortMonthName': 'Nov', 'QtrName': 'Q4'},
	12: {'FullMonthName': 'December', 'ShortMonthName': 'Dec', 'QtrName': 'Q4'}
}

RLS_COLUMNS_FILTER_CHOICE = [
	{'col_name': 'CustomerName', 'operator_choice': {'equal-to': 'textbox', 'like': 'textbox', 'in': 'option'}}
	, {'col_name': 'CustomerRegion', 'operator_choice': {'equal-to': 'textbox', 'like': 'textbox', 'in': 'option'}}
	, {'col_name': 'CustomerType', 'operator_choice': {'equal-to': 'textbox', 'like': 'textbox', 'in': 'option'}}
	, {'col_name': 'Name', 'operator_choice': {'equal-to': 'textbox', 'like': 'textbox', 'in': 'option'}}
	, {'col_name': 'ProdGroup', 'operator_choice': {'equal-to': 'textbox', 'like': 'textbox', 'in': 'option'}}
	, {'col_name': 'ProductDesc', 'operator_choice': {'equal-to': 'textbox', 'like': 'textbox', 'in': 'option'}}
	, {'col_name': 'CalendarDate', 'operator_choice': {
		'equal-to': 'calendar', 'greater-than': 'calendar', 'lesser-than': 'calendar'}}
	, {'col_name': 'Month', 'operator_choice': {'equal-to': 'textbox', 'in': 'option'}}
	, {'col_name': 'Year', 'operator_choice': {'equal-to': 'textbox', 'in': 'option'}}
	, {'col_name': 'MonthYear', 'operator_choice': {'in': 'option'}}
	, {'col_name': 'Quarter', 'operator_choice': {'equal-to': 'textbox', 'in': 'option'}}
	, {'col_name': 'QuarterYear', 'operator_choice': {'in': 'option'}}
	, {'col_name': 'SalesQty', 'operator_choice': {
		'equal-to': 'textbox', 'greater-than': 'textbox', 'lesser-than': 'textbox'}}
	, {'col_name': 'SalesAmount', 'operator_choice': {
		'equal-to': 'textbox', 'greater-than': 'textbox', 'lesser-than': 'textbox'}}
	, {'col_name': 'TargetQty', 'operator_choice': {
		'equal-to': 'textbox', 'greater-than': 'textbox', 'lesser-than': 'textbox'}}
	, {'col_name': 'TargetAmount', 'operator_choice': {
		'equal-to': 'textbox', 'greater-than': 'textbox', 'lesser-than': 'textbox'}}
]


class chatbot_users(db.Model):
	__tablename__ = 'chatbot_users'
	username = db.Column(db.String(255), primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	role = db.Column(db.String(255), db.ForeignKey('user_roles.role'), nullable=False)

	def __init__(self, username, name, password_hash, role):
		self.username = username
		self.name = name
		self.password_hash = password_hash
		self.role = role


class chatbot_logs(db.Model):
	__tablename__ = 'chatbot_logs'
	log_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(255))
	user_query = db.Column(db.String(1023))
	query_parameters = db.Column(db.NVARCHAR(None))
	query_response = db.Column(db.NVARCHAR(None))
	create_time = db.Column(db.DateTime())
	status = db.Column(db.String(10))
	error_name = db.Column(db.String(63))
	error_message = db.Column(db.String(1023))

	def __init__(self, username, user_query, query_parameters, query_response, create_time, status, error_name,
				 error_message):
		self.username = username
		self.user_query = user_query
		self.query_response = query_response
		self.query_parameters = query_parameters
		self.create_time = create_time
		self.status = status
		self.error_name = error_name
		self.error_message = error_message


class error_message(db.Model):
	__tablename__ = 'error_message'
	msg_id = db.Column(db.Integer, primary_key=True)
	error_name = db.Column(db.String(23))
	message = db.Column(db.String(1023))

	def __init__(self, error_name, message):
		self.error_name = error_name
		self.message = message


class user_roles(db.Model):
	__tablename__ = 'user_roles'

	role = db.Column(db.String(255), primary_key=True)
	access_json = db.Column(db.String(4095))

	def __init__(self, role, access_json):
		self.role = role
		self.access_json = access_json


if __name__ == '__main__':
	pass
