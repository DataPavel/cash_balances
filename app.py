from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
from babel.numbers import format_decimal
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import plotly
import json
import requests
import jinja2
import os
from plots import line_balances, pie_currency, stack_bar, extract_rates
from queries import company_choices, currency_choices,\
company_balance_choices, currency_balance_choices, sum_balance

from forms import BankForm, BalanceForm, FilterForm, CompanyForm, \
CurrencyForm, BankFormUpdate, BalanceFormUpdate

# Decimal format for Jinja2
def FormatDecimal(value):
    return format_decimal(float(value), format='#,##0')

jinja2.filters.FILTERS['FormatDecimal'] = FormatDecimal

# Create a Flask Instance
app = Flask(__name__)

bank_balances_uri = os.environ.get('database')

app.config['SQLALCHEMY_DATABASE_URI'] = bank_balances_uri

# Create a Sectet Key
app.config['SECRET_KEY'] = 'KEY'

#Initialize the Database
db = SQLAlchemy(app)

# Create Model for database
class Banks(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	company_name = db.Column(db.String(200), nullable=False)
	bank_name = db.Column(db.String(200), nullable=False)
	account_number = db.Column(db.String(200), nullable=False, unique=True)
	currency = db.Column(db.String(5), nullable=False) 
	address = db.Column(db.String(200), nullable=False)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.company_name




# Create a Bank Page
@app.route('/banks/', methods = ['POST', 'GET'])
def banks():
	bank_name=None
	account_number=None
	form = BankForm()
	form.company_name.choices=['Select Company']+ company_choices(bank_balances_uri)
	form.currency.choices=['Select Currency']+ currency_choices(bank_balances_uri) 
	
	#Validate Form
	if form.validate_on_submit():
		bank = Banks.query.filter_by(account_number=form.account_number.data).first()
		if bank is None:
			bank = Banks(company_name=form.company_name.data, bank_name=form.bank_name.data, 
				account_number=form.account_number.data, currency=form.currency.data,
				address=form.address.data
				)
			db.session.add(bank)
			db.session.commit()
		bank_name = form.bank_name.data
		form.company_name.data = ''
		form.account_number.data = ''
		form.bank_name.data = ''
		form.currency.data = ''
		form.address.data = ''		
	our_banks = Banks.query.order_by(Banks.date_added)
	return render_template('banks.html', bank_name=bank_name,
		form=form, our_banks=our_banks, account_number=account_number)

# Update Banks Database
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
	form = BankFormUpdate()
	#form.company_name.choices=['Select Company']+ company_choices(bank_balances_uri)
	#form.currency.choices=['Select Currency']+ currency_choices(bank_balances_uri) 
	bank_to_update = Banks.query.get_or_404(id)
	if request.method == 'POST':
		bank_to_update.company_name = request.form['company_name']
		bank_to_update.bank_name = request.form['bank_name']
		bank_to_update.account_number = request.form['account_number']
		bank_to_update.currency = request.form['currency']
		bank_to_update.address = request.form['address']
		try:
			db.session.commit()
			flash('Record Updated Successfully')
			return render_template('update.html', form=form,
				bank_to_update=bank_to_update, id=id)
		except:
			flash('Error!! Looks like there was a problem')
			return render_template('update.html', form=form,
				bank_to_update=bank_to_update, id=id)
	else:
		return render_template('update.html', form=form,
				bank_to_update=bank_to_update, id=id)

# Delete Records from Database
@app.route('/delete/<int:id>', methods = ['GET', 'POST'])
def delete(id):
	bank_name = None
	account_number = None
	form = BankForm()
	bank_to_delete = Banks.query.get_or_404(id)
	
	try:
		db.session.delete(bank_to_delete)
		db.session.commit()
		our_banks = Banks.query.order_by(Banks.date_added)
		flash('User Deleted Successfully')
		return redirect(url_for('banks'))
	except:
		flash('There was a problem deleting a bank')
		return redirect(url_for('banks'))



# Create Model for balances database
class Balances(db.Model):
#	__bind_key__='balance'

	def __init__(self, date, company_name, bank_name, currency, balance_curr, rate, balance_usd):
		self.date = date
		self.company_name=company_name
		self.bank_name=bank_name
		self.currency=currency
		self.balance_curr=balance_curr
		self.rate=rate
		self.balance_usd=balance_usd


	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date)
	company_name = db.Column(db.String(200), nullable=False)
	bank_name = db.Column(db.String(200), nullable=False)
	currency = db.Column(db.String(5), nullable=False)	
	balance_curr = db.Column(db.Float(precision=2), nullable=False)
	rate = db.Column(db.Float(precision=2), nullable=False)
	balance_usd = db.Column(db.Float(precision=2), nullable=False)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.date


SECRET_KEY = os.environ.get('secret')



# Create a balance page
@app.route('/balances/', methods = ['GET', 'POST'])
def balances():
	form = BalanceForm()
	form.company_name.choices=['Select Company']+ company_balance_choices(bank_balances_uri)
	form.bank_name.choices=['Select Bank']
	form.currency.choices=['Select Currency']
	if request.method == 'POST':
		date=request.form['date']
		currency = request.form['currency']
		date_exists = forex.query.filter_by(date=form.date.data).first()
		if date_exists is None:
			URL = 'https://openexchangerates.org/api/historical/{}.json?app_id={}'.format(date, SECRET_KEY)
			response = requests.get(URL)
			display = response.json()['rates']
			fxes = forex(request.form['date'], 'USD', display)
			db.session.add(fxes)
			db.session.commit()
		rate = extract_rates(bank_balances_uri, currency, date).astype(float)
		balances = Balances(request.form['date'], request.form['company_name'], 
			request.form['bank_name'], request.form['currency'], request.form['balance_curr'], rate, float(request.form['balance_curr']) / rate)
		db.session.add(balances)
		db.session.commit()
		return redirect(url_for('balances'))
	else:
		#rate = ''
		our_balances = Balances.query.order_by(Balances.date.desc())
		return render_template('balances.html', form=form, our_balances=our_balances)


@app.route('/banks/<company>')
def bank(company):
	banks = Banks.query.filter_by(company_name=company).all()

	bankArray = []

	for bank in banks:
		bankObj = {}
		bankObj['id'] = bank.id
		bankObj['bank_name'] = bank.bank_name
		bankArray.append(bankObj)

	return jsonify({'banks': bankArray})

@app.route('/bank_cur/<bank>')
def bank_currency(bank):
	banks = Banks.query.filter_by(bank_name=bank).all()

	currencyArray = []

	for bank in banks:
		currencyObj = {}
		currencyObj['id'] = bank.id
		currencyObj['currency'] = bank.currency
		currencyArray.append(currencyObj)

	return jsonify({'currencies': currencyArray})

# Update Balances Database
@app.route('/update_bal/<int:id>', methods = ['GET', 'POST'])
def update_bal(id):
	form = BalanceFormUpdate()
	balances_to_update = Balances.query.get_or_404(id)
	if request.method == 'POST':
		balances_to_update.company_name = request.form['company_name']
		balances_to_update.bank_name = request.form['bank_name']
		balances_to_update.currency = request.form['currency']
		balances_to_update.balance_curr = request.form['balance_curr']
		try:
			db.session.commit()
			flash('Record Updated Successfully')
			return render_template('update_bal.html', form=form,
				balances_to_update=balances_to_update, id=id)
		except:
			flash('Error!! Looks like there was a problem')
			return render_template('update_bal.html', form=form,
				balances_to_update=balances_to_update, id=id)
	else:
		return render_template('update_bal.html', form=form,
				balances_to_update=balances_to_update, id=id)





# Delete Balances from Database
@app.route('/delbalance/<int:id>', methods = ['GET', 'POST'])
def baldelete(id):
	form = BalanceForm()
	balance_to_delete = Balances.query.get_or_404(id)
	
	try:
		db.session.delete(balance_to_delete)
		db.session.commit()
		our_balances = Balances.query.order_by(Balances.date.desc())
		flash('User Deleted Successfully')
		return redirect(url_for('balances'))
	except:
		flash('There was a problem deleting a bank')
		return redirect(url_for('balances'))




# Create Filter page
@app.route('/filter/', methods = ['GET', 'POST'])
def filter():
	form=FilterForm()
	form.company_name.choices=['All']+ company_balance_choices(bank_balances_uri)
	form.currency.choices=['All']+ currency_balance_choices(bank_balances_uri)
	if request.method == 'POST':
		company_name = form.company_name.data
		currency = form.currency.data
		date = form.date.data
		if company_name[0] == 'All' and currency[0] == 'All':
			our_balances = Balances.query.filter(Balances.date==date).order_by(Balances.date.desc())
			fig = line_balances(bank_balances_uri)
			graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			fig2 = pie_currency(bank_balances_uri, date="'"+str(date)+"'", 
				company_name = str(tuple(company_balance_choices(bank_balances_uri))).replace(",)",")"))
			graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
			fig3 = stack_bar(bank_balances_uri)
			graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
			sum_bal = sum_balance(bank_balances_uri, date="'"+str(date)+"'")

			return render_template('filter.html', graph=graph, graph2=graph2, 
				graph3=graph3, our_balances=our_balances, form=form, date=date, sum_bal=sum_bal)
		elif company_name[0] == 'All' and currency[0] != 'All':
			our_balances = Balances.query.filter(Balances.currency.in_(currency)).filter_by(date=date).order_by(Balances.date.desc())
			fig = line_balances(bank_balances_uri)
			graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			fig2 = pie_currency(bank_balances_uri, date="'"+str(date)+"'", 
				company_name = str(tuple(company_balance_choices(bank_balances_uri))).replace(",)",")"))
			graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
			fig3 = stack_bar(bank_balances_uri)
			graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
			sum_bal = sum_balance(bank_balances_uri, date="'"+str(date)+"'")

			return render_template('filter.html', graph=graph, graph2=graph2, 
				graph3=graph3, our_balances=our_balances, form=form, date=date, sum_bal=sum_bal)
		elif company_name[0] != 'All' and currency[0] == 'All':
			our_balances = Balances.query.filter(Balances.company_name.in_(company_name)).filter_by(date=date).order_by(Balances.date.desc())
			fig = line_balances(bank_balances_uri)
			graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			fig2 = pie_currency(bank_balances_uri, date="'"+str(date)+"'", 
				company_name = str(tuple(company_name)).replace(",)",")"))
			graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
			fig3 = stack_bar(bank_balances_uri)
			graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
			sum_bal = sum_balance(bank_balances_uri, date="'"+str(date)+"'")

			return render_template('filter.html', graph=graph, graph2=graph2, 
				graph3=graph3, our_balances=our_balances, form=form, date=date, sum_bal=sum_bal)		
		
		else:
			our_balances = Balances.query.filter(Balances.company_name.in_(company_name),
				Balances.currency.in_(currency)).filter_by(date=date).order_by(Balances.date.desc())
			fig = line_balances(bank_balances_uri)
			graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
			fig2 = pie_currency(bank_balances_uri, date="'"+str(date)+"'", 
				company_name = str(tuple(company_name)).replace(",)",")"))
			graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
			fig3 = stack_bar(bank_balances_uri)
			graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
			sum_bal = sum_balance(bank_balances_uri, date="'"+str(date)+"'")

			return render_template('filter.html', graph=graph, graph2=graph2, 
				graph3=graph3, our_balances=our_balances, form=form, date=date, sum_bal=sum_bal)

	else:
		fig = line_balances(bank_balances_uri)
		graph=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
		fig2 = pie_currency(bank_balances_uri, date="'"+str(Balances.query.order_by(Balances.date.desc()).first().date)+"'", 
				company_name = str(tuple(company_balance_choices(bank_balances_uri))).replace(",)",")"))
		graph2=json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
		our_balances = Balances.query.order_by(Balances.date.desc())
		fig3 = stack_bar(bank_balances_uri)
		graph3=json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
		date = Balances.query.order_by(Balances.date.desc()).first().date
		sum_bal = sum_balance(bank_balances_uri, date="'"+str(Balances.query.order_by(Balances.date.desc()).first().date)+"'")

		return render_template('filter.html', graph=graph, graph2=graph2, 
			graph3=graph3, our_balances=our_balances, form=form, date=date, sum_bal=sum_bal)



# Create Model for fx database
class forex(db.Model):
#	__bind_key__='fx'

	def __init__(self, date, base, rates):
		self.date=date
		self.base=base
		self.rates=rates


	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.Date)
	base = db.Column(db.String(200), nullable=False)
	rates = db.Column(JSON)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.date


# Create Model for companies
class Companies(db.Model):
#	__bind_key__='companies'

	def __init__(self, company_name):
		self.company_name=company_name


	id = db.Column(db.Integer, primary_key=True)
	company_name = db.Column(db.String(200), nullable=False)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.company_name

# Create Model for currencies
class Currencies(db.Model):
#	__bind_key__='currencies'

	def __init__(self, currency):
		self.currency=currency


	id = db.Column(db.Integer, primary_key=True)
	currency = db.Column(db.String(200), nullable=False)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.currency





@app.route('/initial/')
def initial():
	return render_template('initial.html')


@app.route('/company/', methods = ['GET', 'POST'])
def company():
	form = CompanyForm()
	if request.method == 'POST':
		company_exists = Companies.query.filter_by(company_name=form.company_name.data).first()
		if company_exists is None:
			comps = Companies(request.form['company_name'])
			db.session.add(comps)
			db.session.commit()
		return redirect(url_for('company'))

	else:
		our_companies = Companies.query
		return render_template('company.html', form=form,
			our_companies=our_companies)


# Delete Company from Database
@app.route('/company_del/<int:id>', methods = ['GET', 'POST'])
def company_del(id):
	form = CompanyForm()
	company_to_delete = Companies.query.get_or_404(id)
	
	try:
		db.session.delete(company_to_delete)
		db.session.commit()
		our_companies = Companies.query
		return redirect(url_for('company'))
	except:
		flash('There was a problem deleting a company')
		return redirect(url_for('company'))


@app.route('/currency/', methods = ['GET', 'POST'])
def currency():
	form = CurrencyForm()
	if request.method == 'POST':
		curr_exists = Currencies.query.filter_by(currency=form.currency.data).first()
		if curr_exists is None:
			curs = Currencies(request.form['currency'])
			db.session.add(curs)
			db.session.commit()
		return redirect(url_for('currency'))

	else:
		our_currencies = Currencies.query
		return render_template('currency.html', form=form,
			our_currencies=our_currencies)


# Delete Currency from Database
@app.route('/currency_del/<int:id>', methods = ['GET', 'POST'])
def currency_del(id):
	form = CurrencyForm()
	currency_to_delete = Currencies.query.get_or_404(id)
	
	try:
		db.session.delete(currency_to_delete)
		db.session.commit()
		our_currencies = Currencies.query
		return redirect(url_for('currency'))
	except:
		flash('There was a problem deleting a currency')
		return redirect(url_for('currency'))	

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/instructions/')
def instructions():
	return render_template('instructions.html')

@app.route('/test/')
def test():
	return render_template('test.html')