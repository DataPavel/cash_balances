# Cash balances

## Project Description

#### What it does

*Cash Balances* is a Flask application that facilitates collection of infomation about bank balances and displays summary in a nice and good-looking dashboard
#### Technologies used
- python  
- plotly  
- Flask
- Postgres
- HTML  
- Jinja2

## Instructions:

To run this app you need to do the following:  
1. Fork the repo and clone it to your local  
2. This app uses database so you will need to create one.
3. Specify URI of your database in app.py file.
4. This app requires API from openexchangerates.org. Get one and sepcify your app_id in app.py file.
5. If you use bash terminal, in your virtual environment in the folder where app.py is located type:
winpty python
from app import db
db.create_all()
6. You are ready to go


For more details about how the app works please check out [this](https://medium.com/@averinjr/simple-flask-apps-for-finance-part-1-647c30a69ce) medium article