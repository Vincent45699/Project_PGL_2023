import dash
from dash import dcc
from dash import html
import requests
from datetime import datetime
import numpy as np
import re
import plotly.graph_objs as go

app = dash.Dash(__name__)

eth_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
eth_data = eth_response.json()
pg_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd')
pg_data = pg_response.json()

eth_datareg = eth_response.text
eth_match = re.search(r'"ethereum":\s*{\s*"usd":\s*(\d+(\.\d+)?)\s*}', eth_datareg)
ethereum_price_usd = eth_match.group(1)
pg_datareg = pg_response.text
pg_match = re.search(r'"pax-gold":\s*{\s*"usd":\s*(\d+(\.\d+)?)\s*}', pg_datareg)
pax_gold_price_usd = pg_match.group(1)

def get_historical_data(coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7'
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    return [(datetime.fromtimestamp(x[0]/1000.0), x[1]) for x in prices]

eth_historical_data = get_historical_data('ethereum')
pg_historical_data = get_historical_data('pax-gold')

def get_metrics_data(coin_id):
    url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=7'
    response = requests.get(url)
    data = response.json()
    daily_data = {}
    for metric in ['prices', 'market_caps', 'total_volumes']:
        daily_data[metric] = [x[1] for x in data[metric]]
    daily_metrics = {}
    daily_metrics['Open'] = daily_data['prices'][0]
    daily_metrics['Close'] = daily_data['prices'][-1]
    daily_metrics['High'] = max(daily_data['prices'])
    daily_metrics['Low'] = min(daily_data['prices'])
    daily_metrics['Volatility'] = np.std(daily_data['prices'])
    ma_10 = np.mean(daily_data['prices'][-10:])
    ma_30 = np.mean(daily_data['prices'][-30:])
    report_data = [
        {'name': 'Open', 'value': f'${daily_metrics["Open"]:.2f}'},
        {'name': 'Close', 'value': f'${daily_metrics["Close"]:.2f}'},
        {'name': 'High', 'value': f'${daily_metrics["High"]:.2f}'},
        {'name': 'Low', 'value': f'${daily_metrics["Low"]:.2f}'},
        {'name': 'Volatility', 'value': f'{daily_metrics["Volatility"]:.2f}'},
        {'name': 'MA 10', 'value': f'${ma_10:.2f}'},
        {'name': 'MA 30', 'value': f'${ma_30:.2f}'},
    ]
    return report_data

report_data_eth = get_metrics_data('ethereum')
report_data_pg= get_metrics_data('pax-gold')


app.layout = html.Div(children=[
    html.Div(children=[        
        html.H1(children='Ethereum & PAX Gold dashboard', style={'textAlign': 'center', 'marginBottom': '30px'})], 
             style={'backgroundColor': '#2B2D42', 'padding': '20px', 'color': 'white'}),

    html.Div(children=[        
        html.Div(children=[            
            html.H4(children='Current Price of the ETH:', style={'textAlign': 'center'}),
            html.H2(children=f'{ethereum_price_usd} USD',
                 style={'textAlign': 'center', 'fontSize': '50px', 'marginBottom': '20px'})], 
                 style={'flex': '1', 'backgroundColor': '#F8F8F8', 'padding': '20px', 'borderRadius': '10px', 'marginRight': '20px'}),
       
        html.Div(children=[            
            html.H6(children='Current Price of the PAX Gold:', style={'textAlign': 'center'}),            
            html.H1(children=f'{pax_gold_price_usd} USD',
                    style={'textAlign': 'center', 'fontSize': '50px', 'marginBottom': '20px'})], 
                    style={'flex': '1', 'backgroundColor': '#F8F8F8', 'padding': '20px', 'borderRadius': '10px', 'marginRight': '20px'}),
        
        
        html.Div(children=[
            dcc.Graph(
                id='ethereum-price', figure={'data': [go.Scatter(x=[x[0] for x in eth_historical_data], y=[y[1] for y in eth_historical_data], mode='lines', name='Ethereum price', line={'color': '#2B2D42'}
            go.Scatter(x=[x[0] for x in pg_historical_data], y=[y[1] for y in pg_historical_data], mode='lines', name='PAX Gold price', line={'color': 'red'})
                ],
                'layout': {
                    'title': {'text': 'Ethereum and PAX Gold price over the last 7 Days', 'font': {'size': 26}},
                    'xaxis': {'title': 'Date', 'showgrid': False},
                    'yaxis': {'title': 'Price (USD)', 'showgrid': False}
                }
            },
            style={'height': '500px'}
        )
            ], style={'flex': '2', 'backgroundColor': '#F8F8F8', 'padding': '20px', 'borderRadius': '10px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'marginTop': '30px'}),
        

        html.Div(children=[
            html.H2(children='Ethereum & PAX Gold metrics', style={'textAlign': 'center', 'marginBottom': '30px'}),
            html.Div(children=[
                html.Div(children=[
                    html.H3(children='Metrics names', style={'textAlign': 'center'}),
                    html.Table(
                        [html.Tr([html.Th(metric['name'], style={'padding': '10px'})]) for metric in report_data_eth],style={'display': 'table', 'width': '100%'}
            )
        ], style={'padding': '20px', 'borderRadius': '10px', 'marginTop': '30px', 'flex': '1'}),
        
        html.Div(children=[
            html.H3(children='Ethereum metrics', style={'textAlign': 'center'}),
            html.Table(
                [html.Tr([html.Th(metric['value'], style={'padding': '10px'})]) for metric in report_data_eth],
                style={'display': 'table', 'width': '100%'}
            )
        ], style={'padding': '20px', 'borderRadius': '10px', 'marginTop': '30px', 'flex': '1'}),

        html.Div(children=[
            html.H3(children='PAX Gold metrics', style={'textAlign': 'center'}),
            html.Table(
                [html.Tr([html.Th(metric['value'], style={'padding': '10px'})]) for metric in report_data_pg],
                style={'display': 'table', 'width': '100%'}
            )
        ], style={'padding': '20px', 'borderRadius': '10px', 'marginTop': '30px', 'flex': '1'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})
], style={'backgroundColor': '#2B2D42', 'padding': '20px', 'color': 'white', 'marginTop': '50px'})

        
])

if __name__ == '__main__':
    app.run_server(debug=True)
