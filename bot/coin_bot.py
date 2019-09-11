from tokens       import cmc_token
from flask        import Flask, request, Response
from configparser import ConfigParser

import requests
import json
import re

config = ConfigParser()
config.read( os.environ['HOME'] + '/' + '.config.ini' )

token = config['COIN']['TOKEN']


app = Flask( __name__ )


def write_json( data, filename='response.json' ):
    with open( filename, 'w' ) as f:
        json.dump( data, f, indent=4, ensure_ascii=False )


def get_cmc_data( crypto ):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {'symbol': crypto, 'convert': 'USD'}
    headers = {'X-CMC_PRO_API_KEY': cmc_token}

    r = requests.get( url, headers=headers, params=params ).json()

    price = r['data'][crypto]['quote']['USD']['price']

    return price


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']

    pattern = r'/[a-zA-Z]{2,4}'

    ticker = re.findall( pattern, txt ) # [...]

    if ticker:
        symbol = ticker[0][1:].upper()   # /btc > btc  .strip('/')
    else:
        symbol = ''

    return chat_id, symbol


def send_message( chat_id, text='bla-bla-bla' ):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}

    r = requests.post( url, json=payload )
    return r



@app.route( '/', methods=['POST', 'GET'] )
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message( msg )

        if not symbol:
            send_message( chat_id, 'Wrong data' )
            return Response( 'Ok', status=200 )

        price = get_cmc_data( symbol )
        send_message( chat_id, price )

        return Response( 'Ok', status=200 ) 

    else:
        return '<h1>Coin Market Cap bot </h1>'



if __name__ == '__main__':
    app.run( debug=True )
