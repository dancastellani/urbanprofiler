import sys, os
sys.path.append(os.getcwd().replace('data-finder-site', '') + 'src')
from urban_profiler.utils import TerminalColors as tc
from urban_profiler.utils import TimeUtils
from urban_profiler.utils import CLI
from urban_profiler import ApplicationOptions
from urban_profiler import ApplicationConstants as Constants

from finder.models import Database, Column, GpsData, Alarm, ColumnData, System, ViewIndexTemporal
from finder import utils

import pandas
import math
import sys, traceback
from multiprocessing import Pool, Lock

from django.core.cache import caches

# PARAMS
STOP_ON_ERROR = True
WORKERS = 10
IGNORE_INDEX = False
IMPORT_ONLY = None

#Not a parameter
COPY_GEO_INDEX = False
CLEAN = False
REFRESH_VIEWS = False
ERRORS = []

def run(*args):
	begin = current_time_formated()

	# if len(args) != 1: raise Exception('Summaries file must be passed as param. Only this param should be used.')

	print '---------- Considered Configuration ------------'
	print 'Args = ', args
	global COPY_GEO_INDEX
	CLEAN = args[0] == 'clean' or (len(args) > 1 and args[1] == 'clean')
	global IMPORT_ONLY
	for arg in args:
		if arg.startswith("import-only="): IMPORT_ONLY = arg.split('=')[1]
	IGNORE_INDEX = 'ignore-index' in args
	REFRESH_VIEWS = 'skip-refresh-views' not in args
	COPY_GEO_INDEX_ONLY = 'copy-index-only' in args
	COPY_GEO_INDEX = 'copy-geo-index' in args or COPY_GEO_INDEX_ONLY

	print 'CLEAN = ', CLEAN
	print 'IGNORE_INDEX = ', IGNORE_INDEX
	print 'COPY_GEO_INDEX = ', COPY_GEO_INDEX
	print 'COPY_GEO_INDEX_ONLY = ', COPY_GEO_INDEX_ONLY
	print 'REFRESH_VIEWS = ', REFRESH_VIEWS
	print 'IMPORT_ONLY dataset = ', IMPORT_ONLY
	print '----------------------\n\n'

	# link_missing_gpsdata()
	# stop=1/0

	if CLEAN:
		print 'Cleaning database before import.'
		ColumnData.objects.all().delete()
		Column.objects.all().delete()
		GpsData.objects.all().delete()
		Database.objects.all().delete()

	summaires_file = args[0]
	column_metadata_file = summaires_file.replace('.csv', '_columns_metadata.csv')
	if not os.path.isfile(column_metadata_file): column_metadata_file = None
	gps_counts_file = summaires_file.replace('.csv', '_index.csv')
	if not os.path.isfile(gps_counts_file): gps_counts_file = None

	if args[0] not in ['update_alarms_only'] and not COPY_GEO_INDEX_ONLY:
		####################### Open files: summaries, columns, geo_index
		print 'Loading summaries...'
		summaries = pandas.read_csv(summaires_file, na_values="", dtype=object)

		print 'Loading columns...'
		types_file = summaires_file.replace('.csv', '_columns.csv')
		types = pandas.read_csv(types_file)
		print '     > ', len(types)

		print 'Loading column data...'
		if column_metadata_file: column_metadata = pandas.read_csv(column_metadata_file)
		print '     > ', len(column_metadata_file)

		gps_counts = None
		if IGNORE_INDEX:
			print 'IGNORING Geo Index...'
		else:
			if COPY_GEO_INDEX: 
				print 'Geo Index will be COPIED and Linked after insert datasets ...'
			else:
				print 'Loading Geo Index...'
				if gps_counts_file: gps_counts = pandas.read_csv(gps_counts_file)
				else: gps_counts = pandas.DataFrame()

		print 'Summaries to import: ', len(summaries), '\n\n'
		columns = summaries.columns

		# pool = Pool(WORKERS)
		# print 'Created pool with size:', WORKERS

		global total_databases
		total_databases = len(summaries)
		for count, row in summaries.iterrows():
			if IMPORT_ONLY and row.Name != IMPORT_ONLY: continue
			# if count < 903: continue
			# if row.Name != 'hh8s-wfy6': continue
			try:
				save_complete_dataset(row, count+1, summaries, types, column_metadata, gps_counts, report_progress=True)
				# print '   + Creating job for ', row.Name
				# pool.apply_async(save_complete_dataset, 
				# 	args=(row, count, summaries, types, column_metadata, gps_counts), 
				# 	callback= report)

			except Exception as e:
				ApplicationOptions.error(e)
				if STOP_ON_ERROR: 
					raise e
				else: 
					ex_type, ex, tb = sys.exc_info()
					ERRORS.append('{0}: {1}\n{2}\n'.format(row.Name ,e, traceback.format_tb(tb) ))
			# break

		# print 'All jobs created. Waiting for results...'
		# pool.close()
		# pool.join()
		# print 'All profilers done.'



		print 'All imported !!!'
		print '=============================='
		print '    Datasets = ', len(summaries)
		print '    Columns = ', len(types)
		print '    Column Data = ', len(column_metadata)
		# print '    GPS Data = ', len(gps_counts)
		print '=============================='
	
	if COPY_GEO_INDEX:
		print 'Copying GEO INDEX. (This can take some minutes)'
		copy_from_geo_index(gps_counts_file, summaries_file=summaires_file)

	print 'Updating alarms. (This can take sometime)'
	update_alarms()
	if REFRESH_VIEWS and gps_counts_file is not None:
		print 'Refreshing Materialized views. (This can take sometime)'
		refresh_materialized_views()
	else: print 'Materialized views were not refreshed.'

	print 'Updating System Control...'
	system = System()
	if args[0] == 'update_alarms_only':
            system.source_file = 'Updated Index Only'
        elif args[0] == 'clean':
            system.source_file = 'Clean DB only'
        else: 
            system.source_file = summaires_file
	system.save()

	print 'Clearing cache so it will be updated on demand.'
	# clear_cache()
	print 'clear cache to update Urban Profiler'

	print ' -----------------------------------< ERRORS >------------------------------------------'
	for e in ERRORS: print ApplicationOptions.error(e)
	print ' ------------------------------------< END >------------------------------------------'

	end = current_time_formated()

	print '\nBegin:', begin
	print 'End:  ', end

	
	print '!!! END OF SCRIPT !!!'

def copy_from_geo_index(filename, summaries_file=None):
	print '--- Importing GPS Data'
	#Drop indexes 
	index_names = utils.execute_query("select indexname from pg_indexes where tablename = 'finder_gpsdata' and indexdef like 'CREATE INDEX%'")
	index_defs = utils.execute_query("select indexdef from pg_indexes where tablename = 'finder_gpsdata' and indexdef like 'CREATE INDEX%'")

	print '---------- Found indexes ----------'
	for index_def in index_defs: print '    - ', index_def
	print '---------- ---------- ----------'

	print 'Droping indexes'
	for index in index_names:
		print ' - Drop index:', index
		utils.execute_query("drop index {}".format(index[0]), fetch=False)
		
	try:
		database_ids = []
		if summaries_file is not None:
			print '----------------------------___>', pandas.read_csv(summaries_file).columns
			database_ids = pandas.read_csv(summaries_file)['Database'].unique()	
		else:
			database_ids = pandas.read_csv(filename)['db'].unique()
		print '-- Removing old Index data from dataset: '
		for db in database_ids:
			print '    -', db
			#utils.execute_query('delete from finder_gpsdata where db = \'{0}\''.format(db), fetch='commit')

		# # 1. copy test (address, borough, count, database, lat, long, zipcode) from '/home/danielcastellani/Documents/databases/etl-profilers/last/last_geo_index.csv' csv header;
		cmd_copy = ['sudo', 'su', 'postgres', '-c']
		cmd_copy.append('\'psql {0} -c "copy finder_gpsdata (lat, long, zipcode, borough, address, db, count, year, month, day) from \'{1}\' csv header;"\''.format(Constants.DATABASE_NAME, filename))
		print 'Copying from Geo index file:', filename
		print 'CMD COPY:', cmd_copy
		#bash_return = CLI.run_bash(cmd_copy)
		#print 'Output:', bash_return
		#if 'ERROR' in bash_return:
		#	raise Exception(bash_return)

		print ' --- Imported INDEX --- '
		print 'GPS Data on database:', GpsData.objects.count()

		print ' --- Linking INDEX to datasets --- '
		link_missing_gpsdata()

	# 2. Update database_id with correct id
	# When inserting the datasets info 

	finally:
		# Recreate indexes
		print 'Re-creating indexes '
		for index_def in index_defs:
			print ' - SQL:', index_def
			utils.execute_query(index_def[0], fetch=False)
			


def save_complete_dataset(row, count, summaries, types, column_metadata, gps_counts, report_progress=False):
	pid = str(os.getpid())
	try:
		db = save_database(row, count, summaries)
		save_columns(db, types, column_metadata)
		if not IGNORE_INDEX:
			if COPY_GEO_INDEX: 
				# link_gps_data(db.database_id, db.id)
				print '         -> GPS Data will be linked to datasets at end of processing.'
			else: save_gps_data(db, gps_counts)
		
		# return db
	except:
		msg = '[' + pid + '] ERROR in THREAD:\n'
		msg += '['+ pid +'] -----------------------------------------------------------------\n'
		msg += '[' + pid + '] ' + traceback.format_exc() + '\n'
		msg += '[' + pid + '] -----------------------------------------------------------------'
		ApplicationOptions.error(msg)
		raise
	if report_progress: report(db)

dbs=[]
total_databases = None
def report(db):
	dbs.append(db)
	actual = len(dbs)
	msg =  ' ________________________________________________________________________ \n'
	msg += '/\n'
	msg += '| Executed: {0}/{1} ({2:.2f}%) - {3}\n'.format(actual, total_databases, actual*100.0/total_databases, TimeUtils.current_time_formated())
	msg +=  '\\________________________________________________________________________\n'
	tc.colored(tc.OKBLUE)
	print msg
	tc.end_colors()

def link_missing_gpsdata():
	print 'Linking all gpsdata which is disconected from database'
	print '   Geting database list'
	databases = utils.execute_query('select distinct db from finder_gpsdata where database_id is null')
	count = 0
	total = len(databases)
	for database_id in databases:
			db_id = utils.execute_query('select id from finder_database where database_id = \'{0}\''.format(database_id[0]))
			print "   {0}/{1}".format(count, total), 'Database:', database_id[0], ' id=', db_id[0][0]
			link_gps_data(database_id[0], db_id[0][0])
			count+=1

def link_gps_data(database_id, id):
	if database_id is not None:
		print '    Linking GPS Data (This can take some time) ...'
		query = "update finder_gpsdata set database_id = {} where db = '{}'".format(id, database_id)
		# print '      -> ', query
		utils.execute_query(query, fetch='commit')
		linked_count = utils.execute_query("select count(*) from finder_gpsdata where db = '{}'".format(database_id), fetch='one')[0]
	else:
		print '    Linking all GPS Data (This can take some minutes) ...'
		utils.execute_query("update finder_gpsdata gps set database_id = db.id \
							 from finder_database db \
							 where db.database_id = gps.db and gps.database_id is null;", fetch='commit')

	print '       > Linked:', linked_count


def save_database(row, count, summaries):
	try:
		db = Database.objects.get(database_id=row.Name)
		print 'Updating - ', row.Name, ' - ', count, '/', len(summaries)
		prepare_database_to_import(row.Name)
	except Database.DoesNotExist:
		db = Database()
		db.database_id = row.Name
		print 'Creating - ', row.Name, ' - ', count, '/', len(summaries)
	
	db.profiler_input_file = get_value(row, 'ETL-Profiler Input File')
	db.profiler_status = str( get_value(row, 'ETL-Profiler Status')[:256] )
	db.profiler_status_short = db.profiler_status.split(':')[0]
	db.profiler_time_begin = get_value(row, 'ETL-Profiler Time Begin')
	db.profiler_time_end = get_value(row, 'ETL-Profiler Time End')
	db.profiler_input_file_size = get_value(row, 'ETL-Profiler Input File Size (KB)', as_type=float, precision=3)
	if db.profiler_input_file_size is not None: 
		db.profiler_input_file_size *= 1000.0
	db.tags = get_value(row, 'Tags')

	db.socrata_status = get_value(row, 'Socrata Status', verbose=False)
	db.name = get_value(row, 'Socrata Name', verbose=False)
	db.metadata_source_name = get_value(row, 'Socrata Source Name', verbose=False)
	db.metadata_source_url = get_value(row, 'Socrata Source URL', verbose=False)

	db.name = get_value(row, 'Socrata Name', verbose=False)
	db.socrata_download_count = get_value(row, 'Socrata Download Count', verbose=False)
	db.socrata_view_count = get_value(row, 'Socrata View Count', verbose=False)
	db.description = get_value(row, 'Socrata Description', verbose=False)
	db.category = get_value(row, 'Socrata Category', verbose=False)
	db.owner = get_value(row, 'Socrata Owner', verbose=False)
	db.access_type = get_value(row, 'Socrata Access Type', verbose=False, default='Open')
	db.hue_status = get_value(row, 'HUE Status', verbose=False, default='Disabled')
	db.author = get_value(row, 'Socrata Author', verbose=False)
	db.socrata_display_type = get_value(row, 'Socrata Display Type', verbose=False)
	db.socrata_view_type = get_value(row, 'Socrata View Type', verbose=False)
	db.socrata_number_of_coments = get_value(row, 'Socrata Number of Coments', verbose=False)
	db.socrata_created_at = get_value(row, 'Socrata Created At', verbose=False)
	db.socrata_last_modified = get_value(row, 'Socrata Last Modified', verbose=False)
	db.socrata_primary = get_value(row, 'Socrata Primary', default=False, verbose=False)
	db.socrata_unique_key = get_value(row, 'Socrata ID Column', verbose=False)
	db.socrata_attribution = get_value(row, 'Socrata Attribution', verbose=False)
	db.socrata_view_from = get_value(row, 'Socrata View From', verbose=False)
	db.source_agency = get_value(row, 'Socrata Agency', verbose=False)
	db.socrata_update_frequency = get_value(row, 'Socrata Update Frequency', verbose=False)

	db.rows = get_value(row, 'Rows', as_type=int)
	db.columns_count = get_value(row, 'Columns', as_type=int)
	db.columns_geo_count = get_value(row, 'Columns Geo', as_type=int)
	db.columns_numeric_count = get_value(row, 'Columns Numeric', as_type=int)
	db.columns_temporal_count = get_value(row, 'Columns Temporal', as_type=int)
	db.columns_text_count = get_value(row, 'Columns Text', as_type=int)
	db.columns_null_count = get_value(row, 'Columns Null', as_type=int, default=0)
	db.values = get_value(row, 'Values', as_type=int)
	db.values_missing = get_value(row, 'Values Missing', as_type=int)

	db.gps_values = get_value(row, 'GPS Values', as_type=int)
	db.lat_min = get_value(row, 'GPS-Lat-Min', as_type=float, precision=10)
	db.lat_max = get_value(row, 'GPS-Lat-Max', as_type=float, precision=10)
	db.long_min = get_value(row, 'GPS-Long-Min', as_type=float, precision=10)
	db.long_max = get_value(row, 'GPS-Long-Max', as_type=float, precision=10)

	db.date_min = get_value(row, 'Date Min', as_type='datetime.date')
	db.date_max = get_value(row, 'Date Max', as_type='datetime.date')

	db.full_clean()
	db.save()
	return db


def prepare_database_to_import(database_id):
	print '    Preparing to import database:', database_id
	for column in Column.objects.filter(database__database_id = database_id).all():
		# print '        Cleaning previous column with its metadata:', column
		ColumnData.objects.filter(column = column).delete()
		column.delete()
	
	#Remove old columns metadatadata
	#Remove old columns

	##TODO: Add database info to database_versions. This will be implemented when we want a historic view.


def save_columns(db, types, column_metadata):
	######################################## import columns
	db_columns = types[types['database-id'] == db.database_id]
	count_cols_real = 0
	print '    Importing columns:', len(db_columns), '...'
	print '    Column metadata:', len(column_metadata[column_metadata['Database-id'] == db.database_id])
	for count_cols, row_col in db_columns.iterrows():
		count_cols_real+=1
		col_name = row_col['column-name']
		# print '        - ', col_name

		try:
			column = Column.objects.get(database__database_id = db.database_id, name = col_name)
			# print '        Updating - ', col_name, ' - ', count_cols_real, '/', len(db_columns)
		except Column.DoesNotExist:
			column = Column()
			column.database = db
			column.name = col_name
			#print '        Creating - ', col_name, ' - ', count_cols_real, '/', len(db_columns)

		column.socrata_type = get_value(row_col, 'socrata-type', default=None)
		column.profiler_type = row_col['profiler-type']
		column.profiler_type_most_detected = row_col['profiler-most-detected']
		column.original = '_@_' not in column.name
		column.profiler_type_most_detected_percent = get_value(row_col, 'profiler-most-detected_%', as_type=float)
		column.values = get_value(row_col, 'values')
		column.missing = get_value(row_col, 'missing')
		column.unique = get_value(row_col, 'unique')

		#Validate and save
		column.full_clean()
		column.save()

		save_column_metadata(db, column, column_metadata)
	# print '        Saved: ', count_cols_real


def save_column_metadata(db, column, column_metadata):
	######################################## import column flexible information
	# print '======================================================================='
	# print 'db.database_id=', db.database_id
	# print 'TYPE=', type(db.database_id)
	data_to_save = column_metadata[column_metadata['Database-id'] == db.database_id]
	data_to_save = data_to_save[data_to_save['Column-name'] == column.name]
	# data_to_save = data_to_save[data_to_save['database-id'] == db.database_id]
	count_real = 0
	# print '        Cleaning previous column metadata...'
	ColumnData.objects.filter(column__name = column.name, column__database__database_id = column.database.database_id).delete()
	
	#print '        [', column.name, '] Importing column metadata... ', '|{0}|'.format(len(data_to_save))
	column_data_list = []
	processed_keys = set()
	for count, row in data_to_save.iterrows():
		#This occours when the column is all Null.
		count_real+=1
		if row['Key'] in processed_keys:
			# print '         > Ignoring repeated key: ', row['Key']
			#Ignore appear twice (NULL) - as Simple and Detailed Type but with same count
			continue
		#print '            ['+ row['Group']+ '] '+ row['Key']+ '=', row['Value'], '(' + str(count_real) +'/' + str(len(data_to_save)) + ')'
			
		column_data = ColumnData()
		column_data.column = column
		column_data.group = row['Group']
		column_data.key = row['Key']
		if 'mean' in column_data.key or 'std' in column_data.key: 
			column_data.value = get_value(row, 'Value', as_type=float, precision=2)
		else:
			column_data.value = row['Value']
			##> Reduce string to fill in value
			if type(column_data.value) is str: 
				column_data.value = row['Value'][:ColumnData.VALUE_MAX_LENGH]

		column_data_list.append(column_data)
		processed_keys.add(row['Key'])

	utils.bulk_save(column_data_list)


def save_gps_data(db, gps_counts):
	#Protect against empty or missing index file
	if gps_counts is None or len(gps_counts) == 0: return 

	SAVE_SIZE = 10000
	# print '======================================================================='
	# print 'db.database_id=', db.database_id
	# print 'TYPE=', type(db.database_id)
	# print 'gps_counts[db]=', gps_counts['db'][0]
	# print 'type=', type(gps_counts['db'][0])
	gps_data = gps_counts[gps_counts['db'].astype(str) == str(db.database_id)]
	if gps_data is not None and len(gps_data) == 0: return
	real_count = 0
	print '    Importing GPS Data:', len(gps_data), '...'
	#Clean old data first
	GpsData.objects.filter(database_id= db.id).delete()

	if len(gps_data) > 50000: print '        GPS Data: ', len(gps_data), ' (This may take some time)'

	#Crete new Records to bulk create
	gpsDataList = []
	for count_gps, row_gps in gps_data.iterrows():
		real_count+=1
		# print db.database_id, '        - ', gps, ' = ', get_value(row_gps, 'Count', as_type=int)

		gps = GpsData()
		gps.database = db
		gps.db = db.database_id
		gps.lat = get_value(row_gps, 'lat')
		gps.long = get_value(row_gps, 'lon')
		gps.address = get_value(row_gps, 'address', max_lenght = GpsData.ADDRESS_MAX_SIZE)
		# if gps.address: gps.address = gps.address.strip()[:500]
		# print ':', str(gps.address)
		gps.borough = get_value(row_gps, 'borough', max_lenght = GpsData.BOROUGH_MAX_SIZE)
		gps.zipcode = get_value(row_gps, 'zipcode', max_lenght = GpsData.ZIPCODE_MAX_SIZE)
		# gps.epoch_secs = get_value(row_gps, 'epoch_secs', as_type=int)
		gps.year = get_value(row_gps, 'year', as_type=int)
		gps.month = get_value(row_gps, 'month', as_type=int)
		gps.day = get_value(row_gps, 'day', as_type=int)
		# gps.hour = get_value(row_gps, 'hour', as_type=int)
		
		gpsDataList.append(gps)

		# Create one part
		if len(gpsDataList) % SAVE_SIZE == 0:
			utils.bulk_save(gpsDataList)		
			gpsDataList = []
			print '          Progress: {:.2f}%\r'.format(count_gps * 100.0 / len(gps_data)), 
			# sys.stdout.write('          Progress: {:.2f}%\r'.format(count_gps * 100.0 / len(gps_data)))
			# sys.stdout.flush()
	
	# Bulk create the rest
	utils.bulk_save(gpsDataList)
	print('          Progress: {:.2f}%\r'.format(count_gps * 100 / len(gps_data)))
	# print '        Saved: ', real_count

def get_value(row, key, default=None, as_type=None, precision = None, max_lenght = None, verbose = True):
	if key not in row.keys():
		if verbose: print key, ' not found in ', row.keys()
		return default

	value = row[key]
	# print '\n', key, '=',value, ' -type:',type(value)
	try:
		if type(value) == float and math.isnan(value):
				# print '   Return default ', default
				return default

		if as_type is not None:
			# print '   Converting value to ', as_type
			# if is an integer, can convert, else just return
			if as_type == int:
				value = int(float(value))
			
			if as_type == float and precision is not None:
				value = as_type(value)
				value = round(value, precision)

			if as_type == 'datetime.date':
				value = TimeUtils.date_from_str_date(value)
				# print 'converted date: ', value

			# print '      Return converted: ', value
			return value
		else:
			# print 'type:', type(value)
			# if type(value) not in [int, float]:
			# 	print 'value:', value
			if type(value) is unicode: 
				# print '   Return value.encode(ascii,ignore): ', value.encode('ascii','ignore')
				return value.encode('ascii','ignore')

			# print '   Return value: ', value
			if max_lenght and value: value = value[:max_lenght]
			return value
	except:	
		# print '   Error, Return default ', default
		return default

def update_alarms():
	alarms = Alarm.objects.all()
	for alarm in alarms:
		alarm.count = alarm.result_count()
		print '    - ', alarm.name, ': ', alarm.count
		alarm.save()

	print len(alarms), ' alarms updated.'

# --------------------------------- From TimeUtils /Begin
import locale; 
import time;
def current_time_formated():
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
# --------------------------------- From TimeUtils /End

if __name__ == "__main__":
	begin = current_time_formated()
	run()
	end = current_time_formated()

	print '\nBegin:', begin
	print 'End:', end

def refresh_materialized_views():
	utils.refresh_materialized_view_model(ViewIndexTemporal)

def clear_cache():
	cache = caches['default']
	cache.clear()
