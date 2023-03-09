import dash
from dash import dcc
from dash import html
import requests
from datetime import datetime
import numpy as np
import re

app = dash.Dash(__name__)

response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
data = response.json()

datareg = response.text
match = re.search(r'"ethereum":\s*{\s*"usd":\s*(\d+(\.\d+)?)\s*}', datareg)
ethereum_price_usd = match.group(1)

def get_historical_data():
    url = 'https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=7'
    response = requests.get(url)
    data = response.json()
    prices = data['prices']
    return [(datetime.fromtimestamp(x[0]/1000.0), x[1]) for x in prices]


def get_metrics_data():
    url = 'https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=7'
    response = requests.get(url)
    data = response.json()

    # extract daily data
    daily_data = {}
    for metric in ['prices', 'market_caps', 'total_volumes']:
        daily_data[metric] = [x[1] for x in data[metric]]

    # compute daily metrics
    daily_metrics = {}
    daily_metrics['Open'] = daily_data['prices'][0]
    daily_metrics['Close'] = daily_data['prices'][-1]
    daily_metrics['High'] = max(daily_data['prices'])
    daily_metrics['Low'] = min(daily_data['prices'])
    daily_metrics['Volatility'] = np.std(daily_data['prices'])
    ma_10 = np.mean(daily_data['prices'][-10:])
    ma_30 = np.mean(daily_data['prices'][-30:])
    
    # format data for display
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

historical_data = get_historical_data()
report_data = get_metrics_data()


app.layout = html.Div(children=[
    html.H1(children='Ethereum Price'),

    html.Div(children=[
        html.H4(children=f'Current Price: {ethereum_price_usd} USD')
    ]),

    dcc.Graph(
        id='ethereum-price',
        figure={
            'data': [
                {'x': [x[0] for x in historical_data], 'y': [y[1] for y in historical_data], 'type': 'line', 'name': 'Ethereum Price'}
            ],
            'layout': {
                'title': 'Ethereum Price (Last 7 Days)',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Price (USD)'}
            }
        }
    ),
    html.H1('Ethereum Metrics'),
    html.Table(
        [html.Tr([html.Th(metric['name']), html.Td(metric['value'])]) for metric in report_data]
    )
])



if __name__ == '__main__':
    app.run_server(debug=True)
