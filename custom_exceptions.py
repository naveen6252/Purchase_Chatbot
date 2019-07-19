class DialogFlowDataError(Exception):
	"""Raised when the DialogFlowData is None or Intent not found"""
	pass


class NoFactError(Exception):
	"""Raised when No fact is found in fact condition hence fact and its condition could not be bounded"""
	pass


class ConditionNotDefined(Exception):
	"""Raised when multiple fact conditions found"""
	pass


class NoFactInOperand(Exception):
	"""Raised when there is no fact in fact_value"""
	pass


class NoLeftOperandInPercentage(Exception):
	"""Raised when there is no filter on either of dim_filters or date_condition"""
	pass

class NoCardinalForFactCondition(Exception):
	"""Raised when Cardinal not found for fact condition"""
	pass
