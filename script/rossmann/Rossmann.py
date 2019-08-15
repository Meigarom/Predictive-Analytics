import pandas as pd
import numpy  as np
import pickle

class Rossmann( object ):
    def __init__( self ):
        param_path = '/Users/meigarom/repos/Predictive-Analytics/parameter/'
        self.param_store_type =                  pickle.load( open( param_path + 'param_store_type.pkl', 'rb' ) )
        self.param_assortment =                  pickle.load( open( param_path + 'param_assortment.pkl', 'rb' ) )
        self.param_competition_distance =        pickle.load( open( param_path + 'param_competition_distance.pkl', 'rb' ) )
        self.param_month_of_promo =              pickle.load( open( param_path + 'param_month_of_promo.pkl', 'rb' ) )
        self.param_competition_open_since_year = pickle.load( open( param_path + 'param_competition_open_since_year.pkl', 'rb' ) )
        self.param_year =                        pickle.load( open( param_path + 'param_year.pkl', 'rb' ) )
        self.param_promo2_since_year =           pickle.load( open( param_path + 'param_promo2_since_year.pkl', 'rb' ) )
        self.param_month_of_competition =        pickle.load( open( param_path + 'param_month_of_competition.pkl', 'rb' ) )



    def feature_engineering( self, data):
        """Feature Transformation
            01. day_of_week 
            02. competition open since month
            03. promo 2 since week
            04. day
        """

        # -----  Rescaling -----
        # competition distance
        data['competition_distance'] = ( data['competition_distance'] - self.param_competition_distance['min'][0] ) / (self.param_competition_distance['max'][0] - self.param_competition_distance['min'][0])

        # month of promotion
        data['month_of_promo'] = ( data['month_of_promo'] - self.param_competition_distance['min'][0] ) / ( self.param_competition_distance['max'][0] - self.param_competition_distance['min'][0] )

        # competition open since year
        data['competition_open_since_year'] = ( data['competition_open_since_year'] - self.param_competition_open_since_year['min'][0] ) / ( self.param_competition_open_since_year['max'][0] - self.param_competition_open_since_year['min'][0] )

        # promo2 since year
        data['promo2_since_year'] = ( data['promo2_since_year'] - self.param_promo2_since_year['min'][0] ) / ( self.param_promo2_since_year['max'][0] - self.param_promo2_since_year['min'][0] )

        # month of competition
        data['month_of_competition'] = ( data['month_of_competition'] - self.param_month_of_competition['min'][0] ) / ( self.param_month_of_competition['max'][0] - self.param_month_of_competition['min'][0] )

        # -----  Transformation -----
        # day of week
        data['day_of_week_sin'] = data['day_of_week'].apply( lambda x: np.sin( x * ( 2. * np.pi/7 ) ) )
        data['day_of_week_cos'] = data['day_of_week'].apply( lambda x: np.cos( x * ( 2. * np.pi/7 ) ) )

        # competition open since month
        data['competition_open_since_month_sin'] = data['competition_open_since_month'].apply( lambda x: np.sin( x * ( 2. * np.pi/12 ) ) )
        data['competition_open_since_month_cos'] = data['competition_open_since_month'].apply( lambda x: np.cos( x * ( 2. * np.pi/12 ) ) )

        # promo 2 since week
        data['promo2_since_week_sin'] = data['promo2_since_week'].apply( lambda x: np.sin( x * ( 2. * np.pi/52 ) ) )
        data['promo2_since_week_cos'] = data['promo2_since_week'].apply( lambda x: np.cos( x * ( 2. * np.pi/52 ) ) )

        # day
        data['day_sin'] = data['day'].apply( lambda x: np.sin( x * ( 2. * np.pi/31 ) ) )
        data['day_cos'] = data['day'].apply( lambda x: np.cos( x * ( 2. * np.pi/31 ) ) )

        # -----  Label Encoding -----
        # store type
        data['store_type'] = data['store_type'].replace( self.param_store_type )

        # assortment
        data['assortment'] = data['assortment'].replace( self.param_assortment )

        # drop original features
        data = data.drop( ['day_of_week', 'competition_open_since_month', 'promo2_since_week', 'day'], axis=1 )

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
