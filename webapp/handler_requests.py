# ---------------------------------
# libraries

import json
import numpy                                    as np
import pandas                                   as pd
import pickle

from flask             import Flask, request, render_template
from rossmann.Rossmann import Rossmann


# initialize Flask app
app = Flask( __name__ )


# --------------------------------
# Helper Functions
# --------------------------------
def load_artifact( path, name ):
    print( '===> Loading {} model'.format( name ) )

    # load model
    p = pickle.load( open( path + name, 'rb' ) )

    return p


# ---------------------------------
# Loadings 
# ---------------------------------
# models
model_path = '/Users/meigarom/repos/Predictive-Analytics/model/'
model_name = 'model_xgb.pkl'

model_rossmann = load_artifact( model_path, model_name )


# ---------------------------------
# Endpoint 
# ---------------------------------
@app.route( '/' )
def main():
    return render_template( 'main.html' )


@app.route( '/rossmann/predict', methods=['POST'] )
def rossmann_predict():
    # input data for prediction
    print( '===> getting the data from request' )
    test_json = request.get_json()

    # convert json to DataFrame
    if isinstance( test_json, dict ): # an unique example of test
        test_raw = pd.DataFrame( test_json, index=[0] )
    else:                             # multiple examples
        test_raw = pd.DataFrame( test_json, columns=list( test_json[0].keys() ) )

    # class to prediction
    pipeline = Rossmann()

    # pre-process the test data to prediction
    print( '===> pre-process test data to prediction' )
    test_transformed = pipeline.transform( test_raw.copy() )

    # feature engineering
    print( '===> feature engineering' )
    data = pipeline.feature_engineering( test_transformed )

    # make a prediction
    print( '===> prediction' )
    response_json = pipeline.get_prediction( model=model_rossmann, test_original=test_raw, test_data=data ) 

    return response_json


if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5000 )
