from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length





# Create a Form Class
class BankForm(FlaskForm):
	company_name = SelectField('Company Name', 
		validators=[DataRequired()], validate_choice=True)
	bank_name = StringField('Bank Name', validators=[DataRequired()])
	account_number = StringField('Account Number', validators=[DataRequired()])
	currency = SelectField('Currency', 
		validators=[DataRequired()], validate_choice=True)
	address = StringField('Address', validators=[DataRequired()])
	submit = SubmitField('Submit')


	# Create a Form Class
class BalanceForm(FlaskForm):
	
	date = DateField('Date', validators=[DataRequired()])
	company_name = SelectField('Company Name', 
		validators=[DataRequired()], validate_choice=True)
	bank_name = SelectField('Bank Name', choices=[],
		validators=[DataRequired()], validate_choice=True)
	currency = SelectField('Currency', choices=[],
		validators=[DataRequired()], validate_choice=True)
	balance_curr = DecimalField('Balance', validators=[DataRequired()],
		number_format='# ###,##')
	submit = SubmitField('Submit')



	# Create a Form Class
class FilterForm(FlaskForm):
	
	date = DateField('Date', validators=[DataRequired()])
	company_name = SelectMultipleField('Company Name',
		validate_choice=False, validators=[DataRequired()])
	currency = SelectMultipleField('Currency', choices=[],
		validate_choice=False, validators=[DataRequired()])
	submit = SubmitField('Submit')


	# Create a Form Class for Companies
class CompanyForm(FlaskForm):
	
	company_name = StringField('Company in your group', 
		validators=[DataRequired()])
	submit = SubmitField('Submit')

# Create a Form Class for Companies
class CurrencyForm(FlaskForm):
	
	currency = StringField('Currency in your group', 
		validators=[Length(min=3, max=3), DataRequired()])
	submit = SubmitField('Submit')