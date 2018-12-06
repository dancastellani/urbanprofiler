# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$Aug 22, 2014 12:08:31 PM$"

import pandas
import re
import numpy
from urban_profiler import ApplicationOptions as App
from types import FunctionType as function
from types import DictType as dict
import operator
from urban_profiler.utils import ResourceUtils
from urban_profiler.utils import TextUtils
from os.path import expanduser
import csv
import os
import usaddress
from urban_profiler import ApplicationConstants as Constants

TYPES_REFERENCE_FILE = ResourceUtils.resource_path_of('types_to_detect.csv')

DEBUG = True
PERCENTUAL_PRECISION = 3
NULL_VALUES = ['nan', 'none', 'n/a', 'null']

STATIC_DETECTORS = 'Static'
DYNAMIC_DETECTORS = 'Dynamic'

# Types - Prefixes
NUMERIC = 'Numeric'
TEXTUAL = 'Textual'
GEO = 'Geo'
TEMPORAL = 'Temporal'
NULL = 'Null'
TYPE_PREFIXES = [NULL, TEXTUAL, NUMERIC, GEO, TEMPORAL]

#Subtypes
GEO_ADDRESS = GEO + '-Address'
GEO_GPS = GEO + '-GPS'
GEO_GPS_LATLON = GEO + '-Lat-or-Lon'
GEO_ZIP = GEO + '-ZIP'
GEO_ZIP_9 = GEO + '-ZIP+4'
PHONE = TEXTUAL + '-Phone'
GEO_BOROUGH = GEO + '-BOROUGH'
TEMPORAL_DATE = TEMPORAL + '-Date'
TEMPORAL_TIME = TEMPORAL + '-Time'
TEMPORAL_DATE_TIME = TEMPORAL + '-DateTime'
NUMERIC_INT = NUMERIC + '-Integer'
NUMERIC_DOUBLE = NUMERIC + '-Double'
SSN = TEXTUAL + '-SSN'
PHONE = TEXTUAL + '-PHONE'
NULL = 'Null'



TEMPORAL_TIMESTAMP = 'Temporal-Timestamp'

ZIP_CODES_FILE = ResourceUtils.resource_path_of('zip_codes.csv')
VALID_ZIP_CODES = set(pandas.read_csv(ZIP_CODES_FILE).icol(0).astype(str))

#Regex detector keys
DETECTOR_NAME='name'
REGEX_LIST='regex-list'
DICTIONARY='DICTIONARY'
ACCEPT_NULLS = "ACCEPT_NULLS"
FUNCTION = "FUNCTION"
DICTIONARY_COMPARISON_TYPE = "DICTIONARY_COMPARISON_TYPE"
DICTIONARY_COMPARISON_TYPE_CONTAINS_WORD = 'Contains Word'

#GPS_MIN_PRECISION = 3. Replace bellow \d{3,} with desired precision.
REGEX_LAT = '[\+|-]?\d{1,2}\.\d{3,}'
REGEX_LONG = '[\+|-]?\d{1,3}\.\d{3,}'
REGEX_LAT_LONG = '\(?' + REGEX_LAT + '(\,\s?)' + REGEX_LONG + '\)?'

# SSN
# Ref. http://www.codeproject.com/Articles/651609/Validating-Social-Security-Numbers-through-Regular
REGEX_SSN_WITH_DASHES = '^(?!\b(\d)\1+-(\d)\1+-(\d)\1+\b)(?!123-45-6789|219-09-9999|078-05-1120)(?!666|000|9\d{2})\d{3}-(?!00)\d{2}-(?!0{4})\d{4}$'
REGEX_SSN_WITHOUT_DASHES = '^(?!\b(\d)\1+\b)(?!123456789|219099999|078051120)(?!666|000|9\d{2})\d{3}(?!00)\d{2}(?!0{4})\d{4}$'

# PHONE
US_PHONE_REGEX = '(\+1[-\s.]?)?\(?([\d]{3})?\)?[-\s.]?([\d]{3})[-.\s]?([\d]{4})'


# DATA DETECTORS ----------------------------------------> All regex must consider UPPER CASE strings
DETECTOR_SSN = {DETECTOR_NAME: SSN,
                REGEX_LIST: [re.compile(REGEX_SSN_WITH_DASHES), re.compile(REGEX_SSN_WITHOUT_DASHES)]
                }
DETECTOR_PHONE = {DETECTOR_NAME: PHONE,
                REGEX_LIST: [re.compile(US_PHONE_REGEX),]
                }
DETECTOR_GEO_BOROUGH = { DETECTOR_NAME: GEO_BOROUGH,
                REGEX_LIST: [re.compile('^(BROOKLYN|QUEENS|MANHATTAN|BRONX|STATEN ISLAND)$')]
}
DETECTOR_GEO_ADDRESS = { DETECTOR_NAME: GEO_ADDRESS,
                DICTIONARY: 'address_suffix.csv',
                DICTIONARY_COMPARISON_TYPE: DICTIONARY_COMPARISON_TYPE_CONTAINS_WORD,
}
DETECTOR_GEO_ZIP_9 = { DETECTOR_NAME: GEO_ZIP_9,
                REGEX_LIST: [re.compile('^\d{5}[-\s]?\d{4}$')]
}
DETECTOR_TEMPORAL_DATE = { DETECTOR_NAME: TEMPORAL_DATE,
                REGEX_LIST:
                    [re.compile('^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)?\d\d$'), #mm-dd-yyyy
                    re.compile('^(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)?\d\d$'), #dd-mm-yyyy
                    re.compile('^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$')] #yy-dd-mm
}
DETECTOR_TEMPORAL_TIME = { DETECTOR_NAME: TEMPORAL_TIME,
                REGEX_LIST:
                    [re.compile('^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9](:([0-5]?[0-9]))?$'), # 24h - 13:08
                    re.compile('^([0-9]|0[0-9]|1[0-2]):[0-5][0-9](:([0-5]?[0-9]))?( ?(AM|PM)?)$')] # 12h
}
DETECTOR_TEMPORAL_DATE_TIME = { DETECTOR_NAME: TEMPORAL_DATE_TIME,
                REGEX_LIST:
                    [re.compile('^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)?\d\d ?([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9](:([0-5]?[0-9]))?$'), # mm/dd/yyyy 24h
                    re.compile('^(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)?\d\d ?([0-9]|0[0-9]|1[0-2]):[0-5][0-9](:([0-5]?[0-9]))?( ?(AM|PM)?)$')] # mm/dd/yyyy 12h am/pm
}


DETECTOR_GEO_GPS = { DETECTOR_NAME: GEO_GPS,
                REGEX_LIST:
                    [re.compile('^' + REGEX_LAT_LONG + '$'), #lat and long toguether
                    ] #long
}
DETECTOR_GEO_GPS_LAT_OR_LON = { DETECTOR_NAME: GEO_GPS_LATLON,
                REGEX_LIST:
                    [re.compile('^' + REGEX_LAT + '$'), #lat
                    re.compile('^' + REGEX_LONG + '$'),] #long
}
DETECTOR_NUMERIC_INT = { DETECTOR_NAME: NUMERIC_INT,
                REGEX_LIST: [re.compile('^\d+$')]
}
DETECTOR_NUMERIC_DOUBLE = { DETECTOR_NAME: NUMERIC_DOUBLE,
                REGEX_LIST: [re.compile('^(?:\d*\.)?\d+$')]
}

#NAME DETECTORS ----------------------------------------> All regex must consider UPPER CASE strings
NAME_DETECTOR_GEO = [re.compile('(GPS|LOCATION|LATITUDE|LONGITUDE|BORO|BOROUGH|[.*]?ZIP\s?CODE?[.*]?)')]
NAME_DETECTOR_TEMPORAL = [re.compile('^(DATE|DATETIME|TIME)$')]

#------------------------------------------------------------------------------- Initialization
LOADED_DETECTORS = None

def data_detectors():
#    print 'aaaaaaaaaaaaaaaaaaaaaaaa'
#    print 'TYPES_REFERECE_FILE=', TYPES_REFERECE_FILE
#    print 'os.path.exists(TYPES_REFERECE_FILE)= ', os.path.exists(TYPES_REFERECE_FILE)

    types_file = App.get_option('types_file', default=None)
    if types_file and types_file.lower() == 'true':
        types_file = TYPES_REFERENCE_FILE
    if types_file and os.path.exists(types_file):
        global LOADED_DETECTORS
        if LOADED_DETECTORS is None:
            App.debug(' >>> Loading dynamic types from file: ', types_file)
            types = pandas.read_csv(types_file, header=None, skipinitialspace=True)
            types = types.where((pandas.notnull(types)), None) #Transform NaN into None
            LOADED_DETECTORS = []
            for i in types.index:
                App.debug("")
                #1. Name
                name = types.ix[i][0]
                if types.ix[i][0] != types.ix[i][1]: name += '-' + types.ix[i][1]
                App.debug("name= ",name)
                #2. Regex
                regex_list = types.ix[i][2]
                App.debug("regex= ",regex_list)
                if type(regex_list) == str: regex_list = re.compile(types.ix[i][2])
                #3 & 4. Prepare values dictionary
                values_dictionary = types.ix[i][3]
                App.debug("values_dictionary= ",values_dictionary )

                dictionary_is_file = types.ix[i][4]
                App.debug("dictionary_is_file= ",dictionary_is_file )

                if type(values_dictionary) == str: #is not None or Nan
                    #Read the file into the csv
                    if dictionary_is_file:
                        with open(ResourceUtils.resource_path_of(values_dictionary)) as dict_file:
                            values_dictionary = dict_file.read()

                    #Parse string CSV into a set
                    reader = csv.reader(values_dictionary.splitlines(), delimiter=',', skipinitialspace=True)
                    values_dictionary = []
                    for row in reader:
                        values_dictionary.extend(row)
                    values_dictionary = set(values_dictionary)

                #5. Accept Nulls?
                accept_nulls = types.ix[i][5]
                App.debug("accept_nulls= ",accept_nulls)
                #6. Comparison type
                comparisson_type = types.ix[i][6]
                App.debug("Dictionary comparisson type= ",comparisson_type)


                LOADED_DETECTORS.append({DETECTOR_NAME: name,
                                    REGEX_LIST:[regex_list],
                                    DICTIONARY:values_dictionary,
                                    ACCEPT_NULLS: accept_nulls,
                                    DICTIONARY_COMPARISON_TYPE: comparisson_type,
                                })
            App.debug( 'Loaded types:')
            for item in LOADED_DETECTORS:
                App.debug( item[DETECTOR_NAME])
        return 'Dynamic', LOADED_DETECTORS

    else:
        #Detector must be in desired order to run
        return STATIC_DETECTORS, [
                {DETECTOR_NAME: NULL, FUNCTION: detect_null},
                {DETECTOR_NAME: GEO_ZIP, FUNCTION: detect_zip},
                DETECTOR_SSN,
                DETECTOR_GEO_ZIP_9,
                DETECTOR_GEO_GPS_LAT_OR_LON,
                DETECTOR_GEO_GPS,
                DETECTOR_GEO_BOROUGH,
                DETECTOR_GEO_ADDRESS,
                # {DETECTOR_NAME: GEO_ADDRESS, FUNCTION: detect_us_address},
                DETECTOR_TEMPORAL_DATE,
                DETECTOR_TEMPORAL_TIME,
                DETECTOR_TEMPORAL_DATE_TIME,
                DETECTOR_PHONE,
                DETECTOR_NUMERIC_INT,
                DETECTOR_NUMERIC_DOUBLE,
                {DETECTOR_NAME: TEXTUAL, FUNCTION: detect_text},
                ]

def detailed_type_only(valid_type_full_name):
    return valid_type_full_name.split('-')[1]

#------------------------------------------------------------------------------- SIMPLE TYPE
def simplify(column_types_count):
    simple_types_count = {}
    for prefix in TYPE_PREFIXES:
        simple_types_count[prefix] = 0

    for type in column_types_count:
        App.debug('Computing [{0}]: {1}'.format(type, column_types_count[type]))
        prefix = type.split('-')[0]
        simple_types_count[prefix] += column_types_count[type]

    App.debug('Simple types count: ', simple_types_count)
    return simple_types_count

def match_name(name, regexes):
    for regex in regexes:
        if regex.match(name.upper()): return True
    return False

def simple_type_of(column_types_count):
    return simple_type_of_considering_all(column_types_count, '', '')

def simple_type_of_considering_all(column_types_count, metadata_type, column_name):
    App.debug('[simple_type_of_considering_all]')
    App.debug('column_types_count=', column_types_count)
    App.debug('metadata_type=', metadata_type)
    App.debug('column_name=', column_name)

    simple_types = simplify(column_types_count)
    App.debug('simple_types=', simple_types)

    #From Socrata
    if metadata_type is not None:
        if metadata_type == 'calendar_date': return TEMPORAL
        elif metadata_type == 'location': return GEO

    # With name insight
    upper_column_name = column_name.upper()
    App.debug('match_name(column_name, NAME_DETECTOR_GEO):', match_name(upper_column_name, NAME_DETECTOR_GEO))
    App.debug('match_name(column_name, NAME_DETECTOR_TEMPORAL):', match_name(upper_column_name, NAME_DETECTOR_TEMPORAL))
    if simple_types[GEO] > 0 and match_name(upper_column_name, NAME_DETECTOR_GEO): return GEO

    #remove if is GPS but name is not on name list
    elif most_detected(simple_types)[0] == GEO_GPS:
        App.debug('Removing GEO as an option!')
        simple_types.pop(GEO, None)
    if simple_types[TEMPORAL] > 0 and match_name(upper_column_name, NAME_DETECTOR_TEMPORAL): return TEMPORAL

    return most_detected(simple_types)[0]

def type_of_column_data(col_data):
    return simple_type_of(types_of(col_data))

def most_detected(detected_types):
    App.debug('Detected types: ', detected_types.keys())
    most_detected_type = NULL
    precision = detected_types[most_detected_type]

    if detected_types is None or len(detected_types) == 0:
        return NULL, 100 #%

    for key in detected_types.keys():
        current = detected_types[key]
        App.debug('Current: [{0}]={1}'.format(key, current))
        if current > 0 and current >= precision:
            most_detected_type = key
            precision = detected_types[most_detected_type]
            App.debug('most_detected updated with key:', key)

    App.debug('[most_detected] detected_types=', detected_types)
    App.debug('[most_detected]:', most_detected_type)
    return most_detected_type, precision
#------------------------------------------------------------------------------- Detector Methods
# Params:
#   * column
#   * regex (detect_from regex_only)
# Return:
#   * type_name
#   * detected values 
#   * not detected values

def detect_null(column):
    App.debug('Detecting: Null')
    not_null_indexes = column.astype(str).apply(lambda x: x.lower() not in NULL_VALUES)
    not_null = column[not_null_indexes]
    null_indexes = column[not_null_indexes == False]
    App.debug('   detected: ', len(null_indexes))
    # App.debug('   null_indexes: \n', null_indexes)
    # if len(null_indexes) > 0:
    return NULL, null_indexes, not_null
    # else:
    #     return NULL, pandas.DataFrame(), not_null

def detect_text(column):
    App.debug('Detecting: Text')
    nulls, not_nulls = detect_null(column)[1:]

    App.debug('Text Values:', not_nulls.values[:10])
    App.debug('Non Text Values:', nulls.values[:10])

    return TEXTUAL, not_nulls, nulls

def detect_zip(column):
    App.debug('Detecting: ZIP')

    prepared_col_data = column.dropna()

    if column.dtype is not numpy.int64:
        App.debug('Removing .0 from string. As can be float64 due to Pandas issue.')
        prepared_col_data = prepared_col_data.astype(str).apply(lambda x: x.replace('.0', ''))
        App.debug('Prepared data:\n', prepared_col_data)

#   type, detected, not_detected = detect_from_regex(DETECTOR_GEO_ZIP, prepared_col_data)
    type = GEO_ZIP
#    print '--------------------------------------------'
#    print column.astype(str).str.upper().apply(lambda x: x in VALID_ZIP_CODES is True)
#    print '--------------------------------------------'
#    print column.astype(str).str.upper().apply(lambda x: x not in VALID_ZIP_CODES is True)
#    print '--------------------------------------------'
    detected = prepared_col_data[prepared_col_data.astype(str).str.upper().apply(lambda x: x in VALID_ZIP_CODES)]
    not_detected = prepared_col_data[prepared_col_data.astype(str).str.upper().apply(lambda x: x not in VALID_ZIP_CODES)]

    App.debug('Detected Type:', type)
    App.debug('Detected Values:', len(detected), ' - ', detected.values[:10])
    App.debug('Non Detected Values:', len(not_detected), ' - ', not_detected.values[:10])

    return type, detected, not_detected

def is_us_address(value):
    try:
        tag = usaddress.tag(value)
        return len(tag) > 2 or tag[-1] is not 'Ambiguous'
    except usaddress.RepeatedLabelError as ex:
        App.debug('Error detecting Geo-Address:', ex)
        return False

def detect_us_address(column):
    type = GEO_ADDRESS
    prepared_col_data = column.dropna()

    is_address = prepared_col_data.astype(str).str.upper().apply(lambda x: is_us_address(x))
    detected = prepared_col_data[is_address == True]
    not_detected = prepared_col_data[is_address == False]

    App.debug('Detected Type:', type)
    App.debug('Detected Values:', len(detected), ' - ', detected.values[:10])
    App.debug('Non Detected Values:', len(not_detected), ' - ', not_detected.values[:10])

    return type, detected, not_detected

def detect_from_regex(regex_detector, column):
    type_name = regex_detector[DETECTOR_NAME]
    regex_list = regex_detector[REGEX_LIST]
    all_matched_indexes = []

    App.debug('Detecting: ', type_name, ' with ', len(regex_list), ' regexes on ', len(column), ' items.')
    if len(column) == 0:
        return type_name, column, column

    for regex in regex_list:
        matched_indexes = column.index[column.astype(str).str.upper().apply(lambda x: regex.match(x) is not None)]
        App.debug('   matched: ', len(matched_indexes))
        all_matched_indexes += list(matched_indexes)

        #stop if all is matched
        if len(all_matched_indexes) == len(column): break


    App.debug('all_matched_indexes size: ', len(all_matched_indexes))
    all_matched_indexes = set(all_matched_indexes)
    not_matched_indexes = set(column.keys()).difference(all_matched_indexes)

    if len(all_matched_indexes) > 0:
        detected = column[list(all_matched_indexes)]
    else:
        detected = pandas.Series()
    not_detected = column[list(not_matched_indexes)]

    App.debug('Example of Values: ')
    App.debug('   detected: ', detected[:10].values)
    App.debug('   not-detected: ', not_detected[:10].values)

    App.debug('Result: ')
    App.debug('   detected: ', len(detected))

    return type_name, detected, not_detected

def detect_from_dictionary(detector, values_to_detect_type, comparison_type="Equal"):
    type_name = detector[DETECTOR_NAME]
    dictionary = detector[DICTIONARY]
    all_matched_indexes = []

    App.debug('Detecting: ', type_name)
    App.debug('    with ', len(dictionary), ' dictionaty entries on ', len(values_to_detect_type), ' items.')

    if len(values_to_detect_type) == 0:
        return type_name, values_to_detect_type, values_to_detect_type

    prepared_values = values_to_detect_type
    if values_to_detect_type.dtype == numpy.float64:
        prepared_values = prepared_values.astype(str).apply(lambda x: x.replace('.0', ''))

    App.debug('comparison_type: ', comparison_type)
    if comparison_type == "Equal":
        matched_indexes = prepared_values.index[prepared_values.astype(str).str.upper().apply(lambda x: x in dictionary)]
    elif comparison_type == "Contains":
        contains = lambda x: any(valid in x for valid in list(dictionary))
        matched_indexes = prepared_values.index[prepared_values.astype(str).str.upper().apply(contains)]
    elif comparison_type == "Contains Word":
        contains = lambda x: any(word in dictionary for word in x.split(' '))
        matched_indexes = prepared_values.index[prepared_values.astype(str).str.upper().apply(contains)]
    else:
        error_message = 'Unknown Comparison type "' + comparison_type + '" in Dynamic Types File.'
        raise Exception(error_message)


    App.debug('   matched: ', len(matched_indexes))
    all_matched_indexes = list(matched_indexes)

    App.debug('all_matched_indexes size: ', len(all_matched_indexes))
    all_matched_indexes = set(all_matched_indexes)
    not_matched_indexes = set(values_to_detect_type.keys()).difference(all_matched_indexes)

    detected = values_to_detect_type[all_matched_indexes]
    not_detected = values_to_detect_type[not_matched_indexes]

    App.debug('Example of Values: ')
    App.debug('   >> detected: ', detected[:10].values)
    App.debug('   not-detected: ', not_detected[:10].values)

    App.debug('Result: ')
    App.debug('   detected: ', len(detected))


    return type_name, detected, not_detected

def detect_using_dynamic(detector, values_to_detect_type):
    App.debug('Dynamic Detecting: ', detector[DETECTOR_NAME])
    App.debug('    ACCEPT_NULLS: ', detector[ACCEPT_NULLS])
    if detector[DICTIONARY]: App.debug('    DICTIONARY (len): ', len(detector[DICTIONARY]), ' - Sample:', list(detector[DICTIONARY])[:10])
    if detector[REGEX_LIST]: App.debug('    REGEX_LIST: ', len(detector[REGEX_LIST]))

    if detector[ACCEPT_NULLS]:
        App.debug('    detect_null(...) ')
        return detect_null(values_to_detect_type)

    elif detector[DICTIONARY]:
        App.debug('    detect_from_dictionary(...) ')
        return detect_from_dictionary(detector, values_to_detect_type, detector[DICTIONARY_COMPARISON_TYPE])

    elif detector[REGEX_LIST][0]:
        App.debug('    detect_from_regex(...) ')
        return detect_from_regex(detector, values_to_detect_type)

#------------------------------------------------------------------------------- Detector Engine
def types_of(column):
    App.debug('Detecting types of: ', column.name)
    App.debug('    size: ', len(column))
    detectors_type, detectors = data_detectors()
    App.debug('    Initializing detected_types. ')
    detected_types = {}
    # Initialize with all zeros
    for detector in detectors:
        detected_types[detector[DETECTOR_NAME]] = 0.0
    if len(column) == 0:
        App.debug('Empty column!')
        return detected_types

    remaining_values_to_detect_type = column.copy()

    ## If column is in unicode, transform to ASCII to avoid errors during processing.
    ## Check for unicode in column values
    unicode_values = remaining_values_to_detect_type.apply(lambda x: (type(x) is unicode))
    unicode_values_counts = unicode_values.value_counts()
    ## Transform the unicode values into ascii if there are any
    if True in unicode_values_counts.keys() and unicode_values_counts[True] > 0 :
        App.info('Recoding values... (this can take some time)')
        remaining_values_to_detect_type = remaining_values_to_detect_type.apply(lambda x: TextUtils.reencode_text_if_not_ascii(x))

    for detector in detectors:
        detected, not_detected, type_name = detect_type(detector, detectors_type, remaining_values_to_detect_type)
        detected_types[type_name] = round(len(detected) * 100.0 / len(column), PERCENTUAL_PRECISION)
        remaining_values_to_detect_type = not_detected
        App.debug('    Remaining: ', len(not_detected))

#        if len(remaining_values_to_detect_type) == 0:
#            break
    return detected_types


def detect_type(detector, detectors_type, remaining_values_to_detect_type):
    if detectors_type == DYNAMIC_DETECTORS:
        type_name, detected, not_detected = detect_using_dynamic(detector, remaining_values_to_detect_type)

    elif DICTIONARY in detector.keys() and detector[DICTIONARY] is not None:
        type_name, detected, not_detected = detect_from_dictionary(detector, remaining_values_to_detect_type)

    elif REGEX_LIST in detector.keys() and detector[REGEX_LIST] is not None:
        type_name, detected, not_detected = detect_from_regex(detector, remaining_values_to_detect_type)

    elif FUNCTION in detector.keys() and detector[FUNCTION] is not None:
        type_name, detected, not_detected = detector[FUNCTION](remaining_values_to_detect_type)
    else:
        raise ValueError("Unknown type of detector: {0}".format(detector))

    return detected, not_detected, type_name


#------------------------------------------------------------------------------- Name Detector
# Column name Detectors
GEO_AFIXES = ['LATITUDE', 'LONGITUDE', 'LOCATION']
TEMPORAL_NAMES = ['DATE']
REGEX_NAME_ZIP_CODE = re.compile('.*ZIP\s?[CODE]?.*')

def is_zipcode_name(name):
    return REGEX_NAME_ZIP_CODE.match(name.upper()) is not None

def is_temporal_name(col_name):
    return any(name in col_name.upper() for name in TEMPORAL_NAMES)

def is_gps_name(col_name):
    return any(afix in col_name.upper() for afix in GEO_AFIXES)

#def is_geo_data(column_data):
#    for regex in GEO_REGEX_DOUBLE_CHECK:
#            if False not in column_data.str.match(regex).dropna().values:
#                return True
#    return False

#------------------------------------------------------------------------------- Get Data
def get_numeric_data(col):
    return detect_from_regex(DETECTOR_NUMERIC_DOUBLE, col)[1].astype(float)

def valid_values_of_type(type_name, column_values):
    App.debug('valid_values_of_type()')
    detectors_type, type_detectors = data_detectors()
    for detector in type_detectors:
        if detector['name'] == type_name:
            App.debug('Detecting valid values for:', type_name)
            detected, not_detected, type_name = detect_type(detector, detectors_type, column_values)
            # type_name, detected, not_detected = detect_using_dynamic(detector, column_values)
            App.debug('Detected: ', len(detected))
            return detected
    return None


