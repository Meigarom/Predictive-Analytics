import math
import numpy   as np
import pandas  as pd
import pickle
import xgboost as xgb

class Rossmann( object ):
    def __init__( self ):
        param_path = '/Users/meigarom/repos/Predictive-Analytics/parameters/'
        self.param_store_type = pickle.load( open( param_path + 'param_store_type.pkl', 'rb' ) )
        self.param_assortment = pickle.load( open( param_path + 'param_assortment.pkl', 'rb' ) )
        self.param_competition_distance = pickle.load( open( param_path + 'param_competition_distance.pkl', 'rb' ) )
        self.param_month_of_promo = pickle.load( open( param_path + 'param_month_of_promo.pkl', 'rb' ) )
        self.param_competition_open_since_year = pickle.load( open( param_path + 'param_competition_open_since_year.pkl', 'rb' ) )
        self.param_year = pickle.load( open( param_path + 'param_year.pkl', 'rb' ) )
        self.param_promo2_since_year = pickle.load( open( param_path + 'param_promo2_since_year.pkl', 'rb' ) )
        self.param_month_of_competition = pickle.load( open( param_path + 'param_month_of_competition.pkl', 'rb' ) )



    def transform( self, data ):
        """Transform input data into a dataset for prediction
        """
        # new columns name
        new_cols=['id', 'store', 'day_of_week', 'date', 'open', 'promo', 'state_holiday', 'school_holiday', 'store_type', 'assortment', 'competition_distance', 'competition_open_since_month', 
                  'competition_open_since_year', 'promo2', 'promo2_since_week', 'promo2_since_year', 'promo_interval']
        data.columns = new_cols

        # change the column type
        data['date'] = pd.to_datetime( data['date'] )

        # NA treatment
        data['promo2_since_year'] = data.apply( lambda x: x['date'].year if math.isnan( x['promo2_since_year'] ) else x['promo2_since_year'], axis=1 )
        data['promo2_since_week'] = data.apply( lambda x: x['date'].weekofyear if math.isnan( x['promo2_since_week'] ) else x['promo2_since_week'], axis=1 )
        data['competition_distance'] = data['competition_distance'].apply( lambda x: 200000.0 if math.isnan( x ) else x )
        data['competition_open_since_month'] = data.apply( lambda x: x['date'].month if math.isnan( x['competition_open_since_month'] ) else x['competition_open_since_month'], axis=1 )
        data['competition_open_since_year'] = data.apply( lambda x: x['date'].year if math.isnan( x['competition_open_since_year'] ) else x['competition_open_since_year'], axis=1 )

        # fill na with 0
        data.fillna( 0, inplace=True )

        # if date is in the promo interval, there is promo.
        monthmap = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sept', 10:'Oct', 11:'Nov', 12:'Dec'}
        data['month_map'] = data['date'].dt.month.map( monthmap )
        data['is_promo'] = data[['promo_interval', 'month_map']].apply( lambda x: 0 if x['promo_interval'] == 0 else 1 if x['month_map'] in x['promo_interval'].split( ',' ) else 0, axis=1 )

        # change competition data - Month and Year
        data['competition_open_since_month'] = data['competition_open_since_month'].astype( int )
        data['competition_open_since_year'] = data['competition_open_since_year'].astype( int )

        # change competition data - Week
        data['promo2_since_week'] = data['promo2_since_week'].astype( int )
        data['promo2_since_year'] = data['promo2_since_year'].astype( int )

        # create features
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        data['day'] = data['date'].dt.day
        data['week_of_year'] = data['date'].dt.weekofyear
        data['state_holiday'] = data['state_holiday'].apply( lambda x: 'public_holiday' if x == 'a' else 'easter_holiday' if x == 'b' else 'christmas' if x == 'c' else 'regular_day' )
        data['assortment'] = data['assortment'].apply( lambda x: 'basic' if x == 'a' else 'extra' if x == 'b' else 'extended' )
        data['month_of_competition'] = 12*( data['year'] - data['competition_open_since_year'] ) + ( data['month'] - data['competition_open_since_month'] )
        data['month_of_competition'] = data['month_of_competition'].apply( lambda x: x if x > 0 else 0 )
        data['month_of_promo'] = 12*( data['year'] - data['promo2_since_year'] ) + ( data['week_of_year'] - data['promo2_since_week'] )/4
        data['month_of_promo'] = data['month_of_promo'].apply( lambda x: x if x > 0 else 0 )

        # filtering data
        data = data.drop( ['id', 'date', 'open', 'state_holiday', 'school_holiday', 'is_promo', 'year', 'month', 'week_of_year', 'promo_interval', 'month_map'], axis=1 )

        return data



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

        # -----  Convert data types -----
        data['store_type'] = data['store_type'].astype( int )
        data['assortment'] = data['assortment'].astype( int )


        # -----  Organize columns -----
        cols = ['store', 'store_type', 'assortment', 'promo', 'month_of_promo', 'promo2', 'promo2_since_year', 'promo2_since_week_sin', 'promo2_since_week_cos', 'competition_distance', 
                'competition_open_since_month_sin', 'competition_open_since_month_cos', 'competition_open_since_year', 'month_of_competition', 'day_of_week_sin', 'day_of_week_cos', 'day_sin', 'day_cos']
        data = data[ cols ]

        return data



    def get_prediction( self, model, test_original, test_data ):
        # make prediction
        pred = model.predict( test_data )

        # add to test_data 
        test_original['Prediction'] = np.expm1( pred )
        response =  test_original

        print( '===> returning prediction' )
        response_json = response.to_json( orient='records', date_format='iso' )

        return response_json
