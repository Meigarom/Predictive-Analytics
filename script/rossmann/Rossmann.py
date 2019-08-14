import pandas as pd
import numpy  as np

class Rossmann( object ):
    def __init__( self ):
        self.config = 1

    def feature_engineering( self, data, feat_transf ):
        """Create New Features.
            01. year_normalized
            02. week_of_year 
        """
        return data


    def transform( self, data ):
        """Transform input data into a dataset for prediction
        """
        return data


    def get_prediction( self, model, original_data, test_data ):
        # make prediction
        pred = model.predict( test_data )

        # 
        response = original_data

        print( '===> returning prediction' )
        response_json = response.to_json( orient='records' )
