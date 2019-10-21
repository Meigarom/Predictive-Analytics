import io
import os
import re
import json
import pandas as pd
import seaborn as sns
import requests

from matplotlib import pyplot as plt
from configparser import ConfigParser
from flask import Flask, request, Response

config = ConfigParser()
config.read( os.environ['HOME'] + '/' + '.config.ini' )

ROOT_PATH = config['ROSSMANN']['ROOT_PATH']
TOKEN = config['ROSSMANN']['TOKEN']

app = Flask( __name__ )


def get_plot( data, store ):
    # Plot the Prediction Curve
    fig = plt.figure()
    ax = plt.subplot()
    data = data.sort_values( 'Date', ascending=True )
    ax.plot( pd.to_datetime( data['Date'] ).dt.strftime( '%m-%d' ), data['Prediction'] )
    plt.title( 'Prediction of Store {}'.format( store ) )
    plt.xticks( rotation=90 )

    buf = io.BytesIO()
    fig.savefig( buf, format='png' )

    return buf


def get_data( store ):
    # read dataset
    test_raw = pd.read_csv( ROOT_PATH + 'data/test.csv' )
    df_stores_raw = pd.read_csv( ROOT_PATH + 'data/store.csv' )

    # merge dataset
    df1 = pd.merge( test_raw, df_stores_raw, on='Store', how='left' )

    # select only predicted store
    store = int( store )
    df2 = df1[df1['Store'] == store]

    # remove close days and undefined days
    df2 = df2[~df2['Open'].isnull()]
    df2 = df2[df2['Open'] != 0]

    # dataframe to json
    df3 = df2.to_dict( orient='records' )
    d = json.dumps( df3 )

    return d


def get_prediction( store ):
    url = 'http://0.0.0.0:5000/rossmann/predict'
    h = {'Content-type': 'application/json'}
    d = get_data( store )

    # make the API requestion
    r = requests.post( url, data=d, headers=h )

    if r.status_code == 201:
        df = pd.DataFrame()

    else:
        # results of the prediction
        df = pd.DataFrame( r.json(), columns=list( r.json()[0].keys() ) )

    return df


def send_message( chat_id, text='kkkk', type='text' ):
    url = f'https://api.telegram.org/bot{TOKEN}/'

    if type == 'text':
        url = url + 'sendMessage?chat_id={}'.format( chat_id )
        r = requests.post( url, json={'text': text} )

    else:
        url = url + 'sendPhoto?chat_id={}'.format( chat_id )
        r = requests.post( url, files={'photo': text} )

    return r


def parse_message( message ):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text'] # /btc or /maid

    symbol = txt.replace( '/', '' )

    return chat_id, symbol


@app.route( '/', methods=['POST', 'GET'] )
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message( msg )

        if not symbol:
            send_message( chat_id, 'Wrong Data' )
            return Response( 'Ok', status=200 )

        # get the prediction
        data = get_prediction( store=symbol )

        if not data.empty:
            # sales aggregated
            pred = data[['Store', 'Prediction']].groupby( 'Store' ).sum().reset_index()
            store_id = pred['Store'].values[0] 
            value = pred['Prediction'].values[0]
            m = 'Store {} will sell ${:,.2f} in the next 6 weeks'.format( store_id, value ) 

            send_message( chat_id, m, 'text' )

            # send sales picture
            buf = get_plot( data )
            buf.seek(0)

            send_message( chat_id, buf, 'photo' )

        else:
            m = 'Store {} Not Registered'.format( store )
            send_message( chat_id, m, 'text' )

        return Response( 'Ok', status=200 )
         
    else:
        return '<h1>Store Bot</h1>'

def main():
    chat_id = 449124440
    store = '6'

    # get the prediction
    data = get_prediction( store=store )

    if not data.empty:
        # sales aggregated
        pred = data[['Store', 'Prediction']].groupby( 'Store' ).sum().reset_index()
        store_id = pred['Store'].values[0] 
        value = pred['Prediction'].values[0]
        m = 'Store {} will sell ${:,.2f} in the next 6 weeks'.format( store_id, value ) 

        send_message( chat_id, m, 'text' )

        # send sales picture
        buf = get_plot( data, store )
        buf.seek(0)

        send_message( chat_id, buf, 'photo' )

    else:
        m = 'Store {} Not Registered'.format( store )
        send_message( chat_id, m, 'text' )

if __name__ == '__main__':
    main()
    #app.run( port=5001, debug=True )

# original api
#https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe

# replace token
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/getMe

# endpoint to receive a message from Telegram 
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/getUpdates

# endpoint to send a message to Telegram 
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/sendMessage?chat_id=449124440&text=Hello User

#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/sendMessage?chat_id=449124440&text=Store 1 will sell $183,801.81 in the next 6 weeks

# set the Webhook
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/setWebhook?url=https://nobis.serveo.net

#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/setWebhook?url=https://meigarom-n5f5.localhost.run


## -----------------------------------------
## How to Deploy to Heroku 
## -----------------------------------------
#01. Create a separated folder
#    1.1. mkdir rossmann-bot
#    
#02. Start a python virtual environment
#    2.1. virtualenv .venv -p python3
#    2.2. source .venv/bin/activate
#
#03. Structure of the files
#    Procfile
#    requirements
#    bot.py
#    model/xgboost.pkl
#    data/store.csv
#    data/test.csv
#    templates/main.html
#
#04. pip freeze > requirements.txt
#
#05. echo "web: python bot.py" > Procfile
#
#06. git init
#
#07. vim .gitignore -> *.pyc .venv
#
#08. heroku login
#
#09. heroku create rossmann-model
#
#10. git add .
#
#11. git commit -m 'first commit'
#
#12. git push heroku master 
#
#13. heroku open
#
#14. Delete Webhook
#    14.1. https://api.telegram.org/bot<chat_id>/deleteWebhook
#
#15. Set Webhook
#    15.1. https//api.telegra.org/bot<chat_id>/setWebhook?url=https://rossmann-bot.herokuapp.com
