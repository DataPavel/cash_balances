import pandas as pd
from sqlalchemy import create_engine

def company_choices(database_uri):
    
    engine = create_engine(database_uri)
    data = pd.read_sql("""

    SELECT company_name FROM companies
    ORDER BY 1

    """, con=engine)
    company_choices = data['company_name'].tolist()
    
    return company_choices


def currency_choices(database_uri):
    
    engine = create_engine(database_uri)
    data = pd.read_sql("""

    SELECT currency FROM currencies
    ORDER BY 1

    """, con=engine)
    currency_choices = data['currency'].tolist()
    
    return currency_choices


def company_balance_choices(database_uri):
    
    engine = create_engine(database_uri)
    data = pd.read_sql("""

    SELECT DISTINCT company_name FROM banks
    ORDER BY 1

    """, con=engine)
    company_balance_choices = data['company_name'].tolist()
    
    return company_balance_choices

def currency_balance_choices(database_uri):
    
    engine = create_engine(database_uri)
    data = pd.read_sql("""

    SELECT DISTINCT currency FROM banks
    ORDER BY 1

    """, con=engine)
    currency_balance_choices = data['currency'].tolist()
    
    return currency_balance_choices

def sum_balance(database_uri, date):
    
    engine = create_engine(database_uri)
    data = pd.read_sql("""

    SELECT SUM(balance_usd) FROM balances
    WHERE date = {}
    ORDER BY 1

    """.format(date), con=engine)
    sum_balance = data['sum'][0]
    if sum_balance == None:
        return None

    else:
        if 10000 <=sum_balance<100000:
            sum_balance = str(sum_balance)[:2]+"K"
        elif 100000 <=sum_balance<1000000:
            sum_balance = str(sum_balance)[:3]+"K"
        elif sum_balance>=1000000:
            sum_balance = str(round((sum_balance/1000000),2))+"M"
        else: 
            sum_balance = str(sum_balance)
    
        return sum_balance

