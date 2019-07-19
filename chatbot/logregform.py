from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import csv


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		x = 0
		with open('Stitch/user_credentials.csv', 'r') as csvreader:
			reader = csv.DictReader(csvreader, delimiter=',')
			for row in reader:
				if row['username'] == username.data:
					x = 1
		csvreader.close()

		if x > 0:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		x = 0
		with open('Stitch/user_credentials.csv', 'r') as csvreader:
			reader = csv.DictReader(csvreader, delimiter=',')
			for row in reader:
				if row['email'] == email.data:
					x = 1
		csvreader.close()

		if x > 0:
			raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
