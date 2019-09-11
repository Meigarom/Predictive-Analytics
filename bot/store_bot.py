import os
import json
import pandas as pd
import requests

from configparser import ConfigParser

config = ConfigParser()
config.read( os.environ['HOME'] + '/' + '.config.ini' )

ROOT_PATH = config['ROSSMANN']['ROOT_PATH']
TOKEN = config['ROSSMANN']['TOKEN']

# original api
#https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe

# replace token
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/getMe

# endpoint to receive a message from Telegram 
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/getUpdates

# endpoint to send a message to Telegram 
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/sendMessage?chat_id=449124440&text=Hello User
#https://api.telegram.org/bot937473363:AAFipUhaNR042WusW5i2e1Ibh4e4ZFMh8so/sendMessage?chat_id=449124440&text=Store 1 will sell $183,801.81 in the next 6 weeks


def get_data():
    # read dataset
    test_raw = pd.read_csv( ROOT_PATH + 'data/test.csv' )
    df_stores_raw = pd.read_csv( ROOT_PATH + 'data/store.csv' )

    # merge dataset
    df_test = pd.merge( test_raw, df_stores_raw, on='Store', how='left' )

    # remove close days and undefined days
    df_test = df_test[~df_test['Open'].isnull()]
    df_test = df_test[df_test['Open'] != 0]

    # dataframe to json
    b = df_test.to_dict( orient='records' )
    d = json.dumps( b )

    return d

def get_prediction(store):
    url = 'http://0.0.0.0:5000/rossmann/predict'
    h = {'Content-type': 'application/json'}
    d = get_data()

    r = requests.post( url, data=d, headers=h )

    df_results = pd.DataFrame( r.json(), columns=list( r.json()[0].keys() ) )
    df_agg = df_results[['Store', 'Prediction']].groupby( 'Store' ).sum().reset_index()

    s = df_agg[df_agg['Store'] == store]

    return s

def main():
    p = get_prediction( store=1 )

    print( 'Store {} will sell ${:,.2f} in the next 6 weeks'.format( p['Store'][0], p['Prediction'][0] ) )

if __name__ == '__main__':
    main()
