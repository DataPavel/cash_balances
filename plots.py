import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import plotly.express as px


def line_balances(database_uri):
	engine = create_engine(database_uri)

	data = pd.read_sql('SELECT date, SUM(balance_usd) FROM balances  GROUP BY date ORDER BY date', con=engine)
	fig = go.Figure()
	fig = fig.add_trace(go.Scatter(x=data['date'], y=data['sum'], fill='tozeroy',
		mode="lines+markers+text", text=data['sum']))

	fig = fig.update_xaxes(type='category',
		title = dict(text="Reporting Date",font_size=14),
                     tickfont = dict(size=12), range=[-0.1, int(len(data['date']))-0.9])

	fig = fig.update_yaxes(title = dict(text="Amount,USD", 
		font_size=14),
                     showgrid=True,
                     tickfont = dict(size=12),
                    )
	fig = fig.update_traces(
                    marker_line_width=1.5, marker_color='#0060BA', 
                    marker_symbol = 'diamond', marker_size=6,
                    texttemplate='%{text:.2s}',
                    textposition="top center",
                    textfont=dict(size=12)
                        )

	fig = fig.update_layout(
                        template = 'simple_white',
                        title=dict(text="<b>Bank Balances</b>", 
                        	font_size=20,
                        	x=0.5),
                        margin=dict(l=20, r=20, t=30, b=20),

                        plot_bgcolor='#FAFAFA',
                        paper_bgcolor= '#FAFAFA'
                        )
	return fig



def pie_currency(database_uri, date, company_name):
	engine = create_engine(database_uri)

	data = pd.read_sql("""
		SELECT currency, SUM(balance_usd) AS balance
			FROM(
		SELECT date, company_name, currency, balance_usd
			FROM balances
		WHERE date = {}
		AND company_name IN {}) a

		GROUP BY 1

			""".format(date, company_name), con=engine)
	fig2 = go.Figure()
	fig2 = fig2.add_trace(go.Pie(labels=data['currency'], values=data['balance'], hole = 0.4,
		marker_colors=px.colors.qualitative.Bold
		))
	fig2 = fig2.update_traces(rotation = 90,
                      marker = dict(line = dict(color = 'grey', width = 1)), opacity = 0.9,
                      hovertemplate = "%{label}: %{percent} </br>")
	fig2 = fig2.update_layout(
                        template = 'simple_white',
                        title=dict(text='<b>Proportion of currencies</b>', font_size=20),
                        title_x=0.4,
                        plot_bgcolor='#FAFAFA',
                        paper_bgcolor= '#FAFAFA',
                        margin=dict(l=0, r=0, t=30, b=20),
                        )


	return fig2



def stack_bar(database_uri):
	engine = create_engine(database_uri)

	data = pd.read_sql('''

		SELECT date, company_name, balance, SUM(balance) OVER (PARTITION BY date),
		    balance/SUM(balance) OVER (PARTITION BY date) AS percent
		FROM(
			SELECT date, company_name, SUM(balance_usd) AS balance
			FROM balances
			GROUP BY 1,2) a
		

		''', con=engine)

	fig3 = px.bar(data, x='date', y='percent', color='company_name', 
		color_discrete_sequence=px.colors.qualitative.Bold)
	fig3 = fig3.update_xaxes(type='category',
		title = dict(text="Date",font_size=14),
                     tickfont = dict(size=12))
	fig3 = fig3.update_yaxes(title = dict(text="Proportion", 
			font_size=14),
	                     showgrid=True,
	                     tickfont = dict(size=12),
	                    )
	fig3 = fig3.update_traces(
                    marker_line_width=1,
                    )
	fig3 = fig3.update_layout(
                        template = 'simple_white',
                        title=dict(text="<b>Proportion of balances</b>", 
                        	font_size=20,
                        	x=0.5),
                        margin=dict(l=20, r=20, t=30, b=20),
                        legend_title_text='Company',
                        plot_bgcolor='#FAFAFA',
                        paper_bgcolor= '#FAFAFA'
                        )



	return fig3

def extract_rates(uri, curr, date):

    engine = create_engine(uri)

    data = pd.read_sql('''

    SELECT  
        (rates ->> '{}')::FLOAT AS curr
        FROM forex
        WHERE date = '{}'

    '''.format(curr, date), con=engine)
    rate = data.iloc[0,0]
    return rate

    