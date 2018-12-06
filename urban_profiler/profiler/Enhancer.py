import pandas
from urban_profiler.utils import ResourceUtils
from urban_profiler.profiler import TypeDetector
from urban_profiler import ApplicationConstants as Constants

GEO_INDEX_COLUMNS = ['address', 'lat', 'lon', 'zipcode', 'borough']
NY_GEO_DATA_FILE = ResourceUtils.resource_path_of('nyc_pluto_prepared.csv')
# bounding boxes of each zipcode according to NYC PLUTO
ZIPCODES_LAT_LON_MIN_MAX = pandas.read_csv(ResourceUtils.resource_path_of('zipcode_lat_lon.csv'), dtype = str)

ZIPCODE_IMPROVEMENTS_WITH_IT = ['zipcode', 'borough']
ADDRESS_IMPROVEMENTS_WITH_IT = ['lat', 'lon', 'address', 'zipcode', 'borough']
GPS_IMPROVEMENTS_WITH_IT = ['lat', 'lon', 'address', 'zipcode', 'borough']

NY_GEO_DATA = None
def get_ny_geo_data():
	global NY_GEO_DATA
	if NY_GEO_DATA is None:
		print '(Loading NYC Pluto Index...)'
		NY_GEO_DATA = pandas.read_csv(NY_GEO_DATA_FILE)[GEO_INDEX_COLUMNS]
		# NY_GEO_DATA['gps'] = NY_GEO_DATA.lat.astype(str) + ',' + NY_GEO_DATA.lon.astype(str)
	return NY_GEO_DATA

def improve_zipcode_data(zipcode_data):
	# 1. get NY data higher than zipcode
	nyc_data = get_ny_geo_data()[ZIPCODE_IMPROVEMENTS_WITH_IT]
	nyc_data = nyc_data[pandas.notnull(nyc_data.zipcode)]
	# 2.Join
	joined = pandas.merge(zipcode_data, nyc_data, on='zipcode', how='left')
	joined = joined.drop_duplicates(cols='zipcode')
	
	# print 'joined:\n', joined
	return joined


def improve_address_data(address_data):
	nyc_data = get_ny_geo_data()[ADDRESS_IMPROVEMENTS_WITH_IT]
	#clean for null lat, lon as it is not desired
	nyc_data = nyc_data[pandas.notnull(nyc_data.lat)]
	nyc_data = nyc_data[pandas.notnull(nyc_data.lon)]

	# print 'before join:\n', address_data[:30]

	joined = pandas.merge(address_data, nyc_data, on=['address'], how='left')
	joined = joined.drop_duplicates(cols='address')
	# print 'joined:\n', joined[:30]

	return joined

def improve_gps_data(gps_data):
	print '***********************************************************************'
	print '************* Not enhancing yet, only preparing ***********************'
	print '***********************************************************************'
	# 1. get NY data higher than zipcode
	nyc_data = get_ny_geo_data()[GPS_IMPROVEMENTS_WITH_IT]
	nyc_data = nyc_data[pandas.notnull(nyc_data.lat)]
	nyc_data = nyc_data[pandas.notnull(nyc_data.lon)]
	
	# print '--------\n', address_data[:30]
	# 3.Join
	joined = pandas.merge(address_data, nyc_data, on=['lat', 'lon'], how='left')
	joined = joined.drop_duplicates()
	# print 'joined:\n', joined[:30]
	
	# print '***********************************************************************'
	stop=1/0
	# print 'joined:\n', joined
	return joined

def get_geo_bounds_from_zipcode(index):
	# geo_bounds = {'lat_min': float('inf'), 'lat_max': float('-inf'), 'long_min': float('inf'), 'long_max': float('-inf')}

	zipcodes = pandas.DataFrame(index.zipcode[index.zipcode != Constants.INDEX_MISSING_DATA_SYMBOL].unique(), columns=['zipcode'])
	if zipcodes.count > 0:
		joined = pandas.merge(zipcodes, ZIPCODES_LAT_LON_MIN_MAX, on='zipcode', how='left')
		geo_bounds = {
						'lat_min': joined.lat_min.astype(float).min(), 
						'lat_max': joined.lat_max.astype(float).max(), 
						'long_min': joined.long_min.astype(float).min(), 
						'long_max': joined.long_max.astype(float).max()
						}		
		return geo_bounds
	else: 
		return None
