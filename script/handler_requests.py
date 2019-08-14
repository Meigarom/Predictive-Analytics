# ---------------------------------
# libraries

import json
import numpy                                    as np
import pandas                                   as pd
import pickle

from flask             import Flask, request
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
model_path = '/Users/meigarom/repos/Predictive-Analytics/models/'
model_name = 'model_xgb.pkl'

model_rossmann = load_artifact( model_path, model_name )

## transformations
#feat_transf_path = '/Users/meigarom/respos/Predictive-Analytics/parameters/'
#feat_transf_name = 'feature_transformation.dat' 
#
#feat_transf = load_artifact( feat_transf_path, feat_transf_name )


# ---------------------------------
# Endpoint 
# ---------------------------------
@app.route( '/rossmann/predict', methods=['POST'] )
def rossmann_predict():
    # input data for prediction
    print( '===> getting the data from request' )
    test_json = request.get_json()

    # convert json to DataFrame
    test = pd.DataFrame( test_json, index=[0] )

    # class to prediction
    pipeline = Rossmann()

    # pre-process the test data to prediction
    print( '===> pre-process test data to prediction' )
    test = pipeline.transform( test )

    # feature engineering
    print( '===> feature engineering' )
    data = pipeline.feature_engineering( test, feat_transf )

    # make a prediction
    print( '===> prediction' )
    response_json = pipeline.get_prediction( model=model_rossmann, original_data=test, test_data=data ) 
    return response_json


if __name__ == '__main__':
    app.run( host = '0.0.0.0' )
