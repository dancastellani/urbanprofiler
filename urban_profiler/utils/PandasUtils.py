# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 23, 2014 12:10:21 PM$"

import pandas
import os
import json

from urban_profiler.utils import CLI
from urban_profiler.utils import FileUtils
from urban_profiler import ApplicationOptions as App
from urban_profiler import ApplicationConstants as Constants
import numpy

DEBUG = False

NUMERIC = 'Numeric'
TEXTUAL = 'Textual'
GEO = 'Geographic'
TEMPORAL = 'Temporal'
NULL = 'Null'

NEW_COLUMN_NAME_SEPARATOR = '_@_'
LOW_MEMORY=True

def is_valid(x):
    if x is None or type(x) == type(None) or x == numpy.nan or str(x) == 'nan' or x == Constants.MISSING_DATA_SYMBOL:
        # App.debug('is_valid({0})'.format(x), 'type:{0}'.format(type(x)), '= False')
        return False
    else:
        # App.debug('is_valid({0})'.format(x), 'type:{0}'.format(type(x)), '= True')
        return True

def join_lat_lon_into_gps(dataset, lat_col, lon_col):
    return dataset[lat_col].astype(str) + ',' + dataset[lon_col].astype(str)

def split_lat_lon_from_gps(value):
    value = value.lstrip('(').rstrip(')')
    if ',' in value: return value.split(',')
    elif ' ' in value: return value.split(' ')
    else: return [None, None]

def get_lat_lon_from_gps(gps_col_values):
    lat_values = gps_col_values.astype(str).apply(lambda x: split_lat_lon_from_gps(x)[0])
    lon_values = gps_col_values.astype(str).apply(lambda x: split_lat_lon_from_gps(x)[1])
    return lat_values, lon_values


def shrink(col, size_limit = 50):
    return col.apply(lambda x: x[:size_limit] + ' ...' if len(x) > size_limit else x)


def get_encoding(file_name):
    # To make sure it is a file as a directory would not suffice.
    if not os.path.isfile(file_name):
        return

    file_encode = CLI.run_bash('file -i ' + file_name)
    # print 'file_encode=', file_encode
    file_encode = file_encode.split('charset=')[1]
    encodings = ['utf-16', 'utf-8']
    for enc in encodings:
        if enc in file_encode:
            return enc
    # return Nonespark


def prepare_dtypes_for_loading(cols):
    ''' This method prepares the dtypes to use with pandas read_csv or read_json.
        So all columns will be considered strings and no presentation modification will be done to them.

        For example, if a column with int values has a null value the dtype of the column will be float64.
        When this column is processed by the TypeDetectors and it is transformed to string, the ints will receive a .0 
        at the end that makes the comparison and evaluation more complex. To ilustrate, 1 will become 1.0 when astype(str)
        is used to analize the values by the TypeDetectors.
    '''
    dtypes = {}
    for c in cols:
        dtypes[c] = object
    return dtypes


def load_database(database_file, skiprows=None, nrows=None):
    # It is a socrata CSV database. The wget on compute is not geting the extension as should.
    file_type = 'CSV' #default if no extension is found.
    if database_file.endswith('.csv'): file_type = 'CSV'
    if database_file.endswith('.json'): file_type = 'JSON'

    file_encoding = get_encoding(database_file)
    App.info('   > File encoding: %s' % file_encoding)

    if file_type == 'CSV':
        App.debug('CSV: Reading column headers from first line.')
        cols = FileUtils.get_cols_from_csv_header(database_file)
        App.debug('Preparing column types for pandas.')
        dtypes = prepare_dtypes_for_loading(cols)
        try:
            App.debug('Trying to read csv...')
            return pandas.read_csv(database_file, skiprows=skiprows, nrows=nrows, low_memory=LOW_MEMORY, encoding=file_encoding, dtype=dtypes)
        except:
            App.debug('Default CSV did not work.')
            App.debug('Trying to read with tab as separator...')
            # This error can be because the file is a tab separated values instead of comma
            return pandas.read_csv(database_file, skiprows=skiprows, nrows=nrows, low_memory=LOW_MEMORY, encoding=file_encoding, sep='\t', dtype=dtypes)

    elif file_type == 'JSON':
        # This works for json under socrata format, which have data field.
        # If not this way, lets supose it is already the data.
        json_file = open(database_file)
        json_data = json.load(json_file)

        if 'data' in json_data.keys():
            App.debug('JSON: Read data from data field. (Socrata format)')
            data = json_data['data']
            cols = []
            cols_with_sub_cols = []

            App.debug('Getting column names from metadata...')
            for col in json_data['meta']['view']['columns']:
                cols.append(col['name'])

                if 'subColumnTypes' in col.keys():
                    print '    (!) Column ', col['name'] , ' has sub columns: ', col['subColumnTypes']
                    cols_with_sub_cols.append(col)

            dtypes = prepare_dtypes_for_loading(cols)
            df = pandas.DataFrame(data, columns=cols)

            #create subcolumn data
            for col in cols_with_sub_cols:
                print '    Fetching sub columns of ', col['name']
                i = 0
                for sub_col in col['subColumnTypes']:
                    print '         >', sub_col
                    df[col['name'] + NEW_COLUMN_NAME_SEPARATOR + sub_col] = df[col['name']].apply(lambda x: x[i])
                    i +=1
                print '    Removing source column ', col['name'], ' from data frame.'
                #Then remove multivalored column
                df.drop(col['name'], axis=1, inplace=True)
            return df

        else:
            App.debug('JSON: There is no data field. Getting column names from JSON keys.')
            #get the list of cols from the json
            cols = list(json_data.keys())
            dtypes = prepare_dtypes_for_loading(cols)
            return pandas.DataFrame(json_data, dtypes=dtypes)
    else:
        print '===> PandasUtilError: Invalid database file: [{0}]'
#        raise ApplicationExecption('File must be json or csv!'.format(database_file))
        raise RuntimeError('File must be json (with data inside a data field) or csv!'.format(database_file))


# def data_type(col_data):
#    col_name = col_data.name
#    if DEBUG: print '[DEBUG]','is_gps_name(col_name)=', is_gps_name(col_name)
#    if DEBUG: print '[DEBUG]','is_zipcode_name(col_name)=', is_zipcode_name(col_name)
#    if DEBUG: print '[DEBUG]','is_geo_data(col_data)=', is_geo_data(col_data)
#    
#    if is_gps_name(col_name) or is_zipcode_name(col_name):
#        if is_geo_data(col_data): 
#            return GEO
#
#    if col_data.dtype in ["float64", 'int64']:
#        return NUMERIC
#
#    if is_temporal_name(col_name):
#        return TEMPORAL
#    
#    return TEXTUAL

def merge_by_database(a, b, b_id):
    # print 'Merging'
    if a is None or b is None:
        if a is not None:   # only b is None
            return a.copy()
        elif b is not None: # only a is None
            return b.copy()
        else:               # both are None
            return None

    else: # Neither is None, Must merge
        temp_a = a
        temp_b = pandas.DataFrame()
#        print '========================+> ', b.index
        temp_b['GPS'] = b.index
        temp_b['Count'] = b.values
        temp_b['DB'] = b_id

        merged = pandas.concat([temp_a, temp_b])
#        print 'len of merged = ', len(merged)
#        print 'merged\n', merged

        return merged


def merge_series_summing_values(a, b, on_columns=['count']):
    # print 'Merging'
    if a is None or b is None:
        if a is not None:   # only b is None
            return a.copy()
        elif b is not None: # only a is None
            return b.copy()
        else:               # both are None
            return None

    else: # Neither is None, Must merge
        temp_a = a
        temp_b = b
        if type(a) is pandas.Series: temp_a = pandas.DataFrame(a, columns = on_columns).reset_index();
        if type(b) is pandas.Series: temp_b = pandas.DataFrame(b, columns = on_columns).reset_index();
        merged = pandas.concat([temp_a, temp_b]).groupby('index').sum()['count']

#    print '----------------------'
#    print 'len(a) = ', len(a)
#    print 'len(b) = ', len(b)
#    print 'len(merged) = ', len(merged)
#    inter = set(a.keys()).intersection(set(b.keys()))
#    print 'a /\ b = ',  len(inter), ' :: ', list(inter)[:1]
#    print 'a U b = ',  len(set(a.keys()).union(set(b.keys())))
#    print 'a - b = ',  len(set(a.keys()) - set(b.keys()))
#    print 'b - a = ',  len(set(b.keys()) - set(a.keys()))
#    print '----------------------'
#    if len(inter)>0:
#        i = list(inter)[0]
#        print 'a[{0}]={1}'.format(i, a[i])
#        print 'b[{0}]={1}'.format(i, b[i])
#        print 'merged[{0}]={1}'.format(i, merged[i])
#        print '----------------------'

    return merged
