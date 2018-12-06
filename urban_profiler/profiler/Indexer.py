import pandas
from urban_profiler import ApplicationConstants as Constants
from urban_profiler import ApplicationOptions as App
from urban_profiler.profiler import TypeDetector
from urban_profiler.utils import PandasUtils
from urban_profiler.utils import TimeUtils
from urban_profiler.utils import TextUtils
import numpy
import Enhancer

INDEX_COLUMN_GEO = '@index_geo'
INDEX_COLUMN_TEMP = '@index_temp'

NEW_GEO_COL_GPS_PREFIX = '+GPS@@'
NEW_TEMP_COL_DATETIME_PREFIX = '+DATETIME@@'

INDEX_ACCEPTED_TYPES_GEO = [TypeDetector.GEO_GPS, TypeDetector.GEO_GPS_LATLON, TypeDetector.GEO_ZIP]
INDEX_ACCEPTED_TYPES_TEMP = [TypeDetector.TEMPORAL_DATE_TIME, TypeDetector.TEMPORAL_DATE, TypeDetector.TEMPORAL_TIME]

INDEX_COLUMNS_GEO = ['lat', 'lon', 'zipcode', 'borough', 'address']
# INDEX_COLUMNS_TEMP = ['epoch_secs', 'year', 'month', 'day', 'hour']
INDEX_COLUMNS_TEMP = ['year', 'month', 'day']

INDEX_COLUMNS = INDEX_COLUMNS_GEO + ['db'] + INDEX_COLUMNS_TEMP
INDEX_COLUMNS_ORDER_IN_CSV = INDEX_COLUMNS_GEO + ['db', 'count'] + INDEX_COLUMNS_TEMP

PHANTON_COL = '<< None >>'

ENHANCE_GEO_BOUNDS = True

def generate_index(db_name, column_types, dataset):
    # App.start_debuging() # <<<<<<<<<<<<<<<<<<<<<<<<

    # Prepare geo index col
    index_geo_cols = get_geo_columns_for_index(column_types, dataset)
    # Prepare temp index col
    index_temp_cols = get_temp_columns_for_index(column_types, dataset)
    # generate geo-temp index counts
    index = generate_index_on(index_geo_cols, index_temp_cols, dataset, db_name)

    # Count index
    # index = add_index_counts(index, db_name, dataset)

    if len(index) > 0: index = prepare_to_save_csv(index, db_name)

    # App.stop_debuging()  # <<<<<<<<<<<<<<<<<<<<<<<<

    return index


def get_geo_columns_for_index(column_types, dataset):
    App.debug('Preparing Geo Index')

    geo_cols = {}
    lat_col_name = None
    lon_col_name = None
    for count_cols, row in column_types.iterrows():
        App.debug('row= ', row['profiler-most-detected'], row['column-name'])
        # print "row['profiler-most-detected'] in INDEX_ACCEPTED_TYPES_GEO=", row['profiler-most-detected'] in INDEX_ACCEPTED_TYPES_GEO
        if row['profiler-most-detected'] in INDEX_ACCEPTED_TYPES_GEO:
            col_name = row['column-name']
            App.debug('> Found:', col_name)

            # Improve for LATITUDE and LONGITUDE in different columns
            if row['profiler-most-detected'] == TypeDetector.GEO_GPS_LATLON:
                if 'LONGITUDE' in col_name.upper():
                    lon_col_name = col_name
                elif 'LATITUDE' in col_name.upper():
                    lat_col_name = col_name
            else:
                geo_cols[col_name] = row['profiler-most-detected']

    if lat_col_name and lon_col_name:
        new_gps_col = NEW_GEO_COL_GPS_PREFIX
        dataset[new_gps_col] = PandasUtils.join_lat_lon_into_gps(dataset, lat_col_name, lon_col_name)
        geo_cols[new_gps_col] = TypeDetector.GEO_GPS
        App.debug('CREATED GPS COL:', dataset[new_gps_col])

    App.debug('Geo cols to index:', geo_cols)
    return geo_cols


def get_temp_columns_for_index(column_types, dataset):
    App.debug('Preparing Temporal Index')

    temp_cols = {}
    date_col_name = None
    time_col_name = None
    for count_cols, row in column_types.iterrows():
        if row['profiler-most-detected'] in INDEX_ACCEPTED_TYPES_TEMP:
            col_name = row['column-name']
            App.debug('> Found:', col_name)

            if col_name.upper() == 'DATE':
                date_col_name = col_name
            elif col_name.upper() == 'TIME':
                time_col_name = col_name
            else:
                temp_cols[col_name] = row['profiler-most-detected']

    # print 'date_col_name and time_col_name=', date_col_name, time_col_name
    # If dataset has TIME and DATE join both as one column
    if date_col_name and time_col_name:
        new_col_name = NEW_TEMP_COL_DATETIME_PREFIX
        dataset[new_col_name] = TimeUtils.join_date_and_time(dataset[date_col_name], dataset[time_col_name])
        temp_cols[new_col_name] = TypeDetector.TEMPORAL_DATE_TIME

    # Has only date, but not date and time. If has only time, disconsider it
    elif date_col_name:
        temp_cols[date_col_name] = row['profiler-most-detected']

    App.debug('Temp cols to index', temp_cols)
    return temp_cols


# For temporal reference: https://docs.python.org/2/library/datetime.html#datetime.datetime.month
def generate_index_on(index_geo_cols, index_temp_cols, dataset, db_name):
    index = pandas.DataFrame(columns=INDEX_COLUMNS)

    # No columns to generate index
    if len(index_geo_cols.keys()) == 0 and len(index_temp_cols.keys()) == 0: return index

    # Prepare the list of cols
    # If is empty add None just to loop into it and call the generate_partial_index function
    if index_geo_cols is None or len(index_geo_cols) == 0: index_geo_cols[PHANTON_COL] = None
    if index_temp_cols is None or len(index_temp_cols) == 0: index_temp_cols[PHANTON_COL] = None

    # Clean dataset before create partial index
    print 'Cleaning dataset to process index'
    print 'dataset size:', len(dataset)
    cols_to_clean = index_geo_cols.copy()
    cols_to_clean.update(index_temp_cols)
    for col in cols_to_clean:
        print '     > {0} - {1}'.format(col, cols_to_clean[col]).ljust(50) + '@' + TimeUtils.current_time_formated()
        # If current col is the PHANTON col, skip it
        if col is PHANTON_COL: continue
        clean_invalid_values(cols_to_clean[col], col, dataset)
        print '          dataset size:', len(dataset)

    for geo_col in index_geo_cols.keys():
        geo_type = index_geo_cols[geo_col]

        for temp_col in index_temp_cols.keys():
            temp_type = index_temp_cols[temp_col]

            an_index = generate_partial_index_on(geo_col, geo_type, temp_col, temp_type, dataset, db_name)
            App.info('	Adding to index... '.ljust(50) + '@' + TimeUtils.current_time_formated())
            index = index.append(an_index, ignore_index=True)

    App.info('Index created with {0} rows'.format(len(index)))
    App.debug('>>>>> INDEX <<<<<\n', index)

    return index


# # Algorithm:
# # This is executed for every combination of geo-temp cols.
# # 1. Add values from geo col to index
# # 		ex. if the geo col is GPS than two index cols are goinng to be used lat and lon
# # 2. Add values from temporal col to index
# #		ex. if the temporal column is a DATE then the index columns year, month and day are going to be used
# # 3. Count by geo and temp cols in index - This is a count of records by geo-temp pair
# #		It is a count with groupby equivalent of SQL using all the used index columns for the current
# #		geo-temp cols.
# # 4. Clean invalid geo or temp values from used index cols
# #		In this step, invalid values from the geo-temp types must be removed from the index.
# # 5.  Add the partial index to the full index
# #
def generate_partial_index_on(geo_col, geo_type, temp_col, temp_type, dataset, db_name):
    App.info('Generating index for ({0}) and ({1})'.format(geo_col, temp_col), TimeUtils.current_time_formated())
    print geo_type

    an_index = pandas.DataFrame(columns=INDEX_COLUMNS)
    countby = []

    # ## 1. ADD GEO VALUES TO INDEX
    if geo_type:
        App.info('	Processing geo part... '.ljust(50) + '@' + TimeUtils.current_time_formated())
        # TODO: ENHANCE GEO INDEX <-------- (TODO)
        if geo_type == TypeDetector.GEO_GPS:
            an_index.lat, an_index.lon = PandasUtils.get_lat_lon_from_gps(dataset[geo_col])
            countby += ['lat', 'lon']

        elif geo_type in [TypeDetector.GEO_ZIP, TypeDetector.GEO_ZIP_9]:
            an_index.zipcode = dataset[geo_col]
            countby += ['zipcode']

    # ## 2. ADD TEMPORAL VALUES TO INDEX
    if temp_type:
        App.info('	Processing temporal part... '.ljust(50) + '@' + TimeUtils.current_time_formated())
        datetimes = dataset[temp_col].apply(lambda x: TimeUtils.datetime_from_str_date(x))
        if temp_type in [TypeDetector.TEMPORAL_DATE, TypeDetector.TEMPORAL_DATE_TIME]:
            # an_index['epoch_secs'] = dataset[temp_col].apply(lambda x: TimeUtils.epoch_from_str_date(x))

            an_index['year'] = datetimes.apply(lambda x: str(x.year) if x else Constants.MISSING_DATA_SYMBOL)
            an_index['month'] = datetimes.apply(lambda x: str(x.month) if x else Constants.MISSING_DATA_SYMBOL)
            an_index['day'] = datetimes.apply(lambda x: str(x.day) if x else Constants.MISSING_DATA_SYMBOL)
            # countby += ['epoch_secs']
            countby += ['year', 'month', 'day']

        # if temp_type == TypeDetector.TEMPORAL_DATE_TIME:
        # 	an_index['hour'] = datetimes.apply(lambda x: str(x.hour) if x else Constants.MISSING_DATA_SYMBOL)

        App.info('	Counting... '.ljust(50) + '@' + TimeUtils.current_time_formated())

    # This order cannot change unless change this algorithm! First count, then clean
    # --------- Count rows for Index ------------------------------------------------------------------
    # 3. create index counts
    # print '-------------------- countby=', countby
    temp = an_index[countby].reset_index().groupby(countby).agg(['count'])
    temp.columns = ['count']
    temp.reset_index(inplace=True)
    # join with real dataset and add to index
    merged = pandas.merge(an_index, temp, how='inner', on=countby)
    # Add count to an_index
    an_index['count'] = merged['count']

    # --------- 4. Clean Index: null and invalid values --------------------------------------------------
    # print '<><><><><><><><><><><><><> an_index.count()=', an_index.count()
    App.info('	Cleaning... '.ljust(50) + '@' + TimeUtils.current_time_formated())

    used_index_cols = list(an_index.count()[an_index.count() > 0].index)
    for col in used_index_cols:
        # geo
        if col in ['lat', 'lon']: col_type = TypeDetector.GEO_GPS_LATLON
        if col == 'zipcode': col_type = TypeDetector.GEO_ZIP
        if col == 'address': col_type = TypeDetector.GEO_ADDRESS
        if col == 'borough': col_type = TypeDetector.GEO_BOROUGH
        # temp
        if col in ['epoch_secs', 'year', 'month', 'day', 'hour']: col_type = TypeDetector.NUMERIC_INT
        App.info('	   > {0}: {1}'.format(col, col_type).ljust(50) + '@' + TimeUtils.current_time_formated())
        # clean_invalid_values(col_type, col, an_index)
        an_index = an_index[an_index[col].apply(lambda x: PandasUtils.is_valid(x))]

    App.debug('>>>>> an_index (len 20) <<<<<')
    App.debug(an_index[:20])
    App.info('     Partial Index created with {0} rows'.format(len(an_index)))
    # 5. return index to be added to the main index
    return an_index


def clean_invalid_values(type, col_name, index):
    valid_values = TypeDetector.valid_values_of_type(type, index[col_name]).unique()
    index = index[index[col_name].astype(str).apply(lambda x: x in valid_values)]


def add_index_counts(index, db_name, dataset):
    # Add db_name info. will be used to count
    index.db = db_name
    # Discover cols that have index data
    count_by = list(index.count()[index.count() > 0].index)
    # count by these cols
    counted_index = index[count_by].groupby(count_by, as_index=False)['db'].agg({'count': 'count'})
    # Add null cols to complete index
    for empty_col in list(index.count()[index.count() == 0].index):
        counted_index[empty_col] = Constants.MISSING_DATA_SYMBOL

    return counted_index


def prepare_to_save_csv(index, db_name):
    index.db = db_name
    index.address = index.address.astype(str)
    index.address = index.address.apply(lambda x: TextUtils.clean_non_ascii(x))
    index.address = index.address.apply(lambda x: x[:100] if x != 'nan' else numpy.NaN)

    # Clean .0 and nan from numeric cols
    cols = ['zipcode', 'count', 'year', 'month', 'day']
    for col in cols: index[col] = index[col].astype(str).apply(
        lambda x: x.rstrip('.0').rstrip('nan').strip(' ').replace('\n', ''))

    index.zipcode = index.zipcode.astype(str).apply(
        lambda x: x[:Constants.INDEX_COLUMN_MAX_SIZE_ZIPCODE] if PandasUtils.is_valid(x) else x)

    return index


def calculate_geo_bounds(index):
    lat_min = index.lat.dropna().astype(float).min()
    lat_max = index.lat.dropna().astype(float).max()
    long_min = index.lon.dropna().astype(float).min()
    long_max = index.lon.dropna().astype(float).max()

    zipcode_bounds = None
    if ENHANCE_GEO_BOUNDS:
        zipcode_bounds = Enhancer.get_geo_bounds_from_zipcode(index)
    if zipcode_bounds:
        if not PandasUtils.is_valid(lat_min) or zipcode_bounds['lat_min'] < lat_min: lat_min = zipcode_bounds['lat_min']
        if not PandasUtils.is_valid(lat_max) or zipcode_bounds['lat_max'] < lat_max: lat_max = zipcode_bounds['lat_max']
        if not PandasUtils.is_valid(long_min) or zipcode_bounds['long_min'] < long_min: long_min = zipcode_bounds[
            'long_min']
        if not PandasUtils.is_valid(long_max) or zipcode_bounds['long_max'] < long_max: long_max = zipcode_bounds[
            'long_max']

    # Clean values
    if lat_min is float('inf') or None: lat_min = ''
    if lat_max is float('inf') or None: lat_max = ''
    if long_min is float('inf') or None: long_min = ''
    if long_max is float('inf') or None: long_max = ''
    geo_bounds = {'lat_min': lat_min, 'lat_max': lat_max, 'long_min': long_min, 'long_max': long_max}
    return geo_bounds
