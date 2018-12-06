import pandas, sys, os, datetime, traceback, numpy
from dateutil import parser
from multiprocessing import Pool, Lock

INPUT_GEO_TEMP_DATASETS = 'geotempdata.csv'
#INPUT_GEO_TEMP_DATASETS = 'geotempdata_test.csv'
# INPUT_GEO_TEMP_DATASETS = 'geotempdata_filtered.csv'

OUTPUT_FOLDER = '/scratch/share/dancastellani/nycopendata_processed_time_geo_first/'
#OUTPUT_FOLDER = '/tmp/'

SUFIX_TIME_FROM_EPOCH = '@SFE'
MISSING_DATA_SYMBOL = None

SUFIX_HEADER_FILE = '_header'
SUFIX_DATA_FILE = '_data'

REPEAT_DATASET = False

ERRORS = []
DEBUG = False 

WORKERS = 20

def epoch_from_str_date(string_date):
	if string_date is None or string_date == numpy.nan or string_date == 'nan': return MISSING_DATA_SYMBOL
#	print '>>>', string_date, ' type:', type(string_date)
	epoch = datetime.datetime(1970,1,1)
	parsed_date = parser.parse(string_date, fuzzy=True, default=epoch)
	#This is not a proper date
	if parsed_date == epoch: MISSING_DATA_SYMBOL

	return (parsed_date - epoch).total_seconds()

#	if '/' not in string_date or len(string_date.split('/')) != 3:
#		return MISSING_DATA_SYMBOL
#	
#	month, day, year = string_date.split('/')
#	return (datetime.datetime(int(year), int(month), int(day),0,0) - datetime.datetime(1970,1,1)).total_seconds()

def split_gps(string, pos=0):
	if ',' in string: return string.split[','][pos] 
	else: return MISSING_DATA_SYMBOL 

def gps_columns_from(dataset, geo_col):
	latlon_cols = []
	gps_col = None
	latcol=None
	longcol=None
	for column in dataset.columns:
		if any(valid in column.upper() for valid in ['LATITUDE']):
			latlon_cols.append(column)
			latcol=column

		elif any(valid in column.upper() for valid in ['LONGITUDE']):
			latlon_cols.append(column)
			longcol = column

		if len(latlon_cols) == 2: break
	#print 'latlon cols:', latlon_cols
        if latcol and longcol: return [latcol, longcol]

	#Column name is not latitude or longitude
	print 'GPS col -> ', column
	#print dataset[column][:5]
	newcol = column + '@lat'
	dataset[newcol] = dataset[column].astype(str).apply(lambda x: split_gps(x, 0))
	latlon_cols.append(newcol)
	newcol = column + '@lon'
	dataset[newcol] = dataset[column].astype(str).apply(lambda x: split_gps(x, 1))
	latlon_cols.append(newcol)
	return latlon_cols

def process_dataset(row, index, total):
	try:
		dataset = row['database_id']
		temp_col = row['date_col']
		geo_col = row['geo_col']
		geo_type = row['geo_type']
		filename = row['filename']
		print '\n', '[{0}/{1}] {2} (temp:{3}, geo:{4}) <{5}>'.format(index+1, total, dataset, temp_col, geo_col, geo_type)
		print '            File:', filename
		
		ds = pandas.read_csv(filename, low_memory=False)
		#Process date to get seconds from epoch
		secs_from_epoch_col = temp_col + SUFIX_TIME_FROM_EPOCH
		ds[secs_from_epoch_col] = ds[temp_col].astype(str).apply(lambda x: epoch_from_str_date(x))
		columns_in_order = [secs_from_epoch_col]

		# Process Geo data
		if geo_type == 'Geo-GPS':
			columns_in_order.extend( gps_columns_from(ds, geo_col)  )
		
		elif geo_type == 'Geo-ZIP':
			columns_in_order.append(geo_col)
		
		elif geo_type == 'Geo-Borough':
			columns_in_order.append(geo_col)
		
		print '         -> Columns:', columns_in_order, ' + {0} others.'.format(len(ds.columns)-len(columns_in_order))
		#Place columns ins correct order
		columns_in_order.extend( [col for col in ds.columns if col not in columns_in_order] )
		#if DEBUG: print 'Processed data:\n', ds[columns_in_order][:3]
		if DEBUG: print 'columns_in_order:', columns_in_order
		
		# Save files
		output_filename = OUTPUT_FOLDER + dataset + SUFIX_HEADER_FILE
		ds[:0].to_csv(output_filename, index=False, columns= columns_in_order)
		print '            Saved:', output_filename
		output_filename = OUTPUT_FOLDER + dataset + SUFIX_DATA_FILE
		ds.to_csv(output_filename, index=False, header=False, columns= columns_in_order)
		print '            Saved:', output_filename

	except Exception as e:
		print '            [ERROR]' , e
		if DEBUG: 
			traceback.print_exc()
			print '\n'
			raise e
		else:
			ex_type, ex, tb = sys.exc_info()
			ERRORS.append('{0}: {1}\n{2}\n'.format(dataset ,e, '\n'.join(traceback.format_tb(tb)) ))

def main():
	global INPUT_GEO_TEMP_DATASETS
	if len(sys.argv) > 1 and sys.argv[1] is not None: INPUT_GEO_TEMP_DATASETS = sys.argv[1]
	print ' ------------------------------------< RUN >------------------------------------------'
	print 'Processing files datasets:', INPUT_GEO_TEMP_DATASETS
	datasets = pandas.read_csv(INPUT_GEO_TEMP_DATASETS)

	## To jump following row because is processing latitude and next is longitude
	jump_next = False
	total = len(datasets)

	last_dataset = None
	processed = 0

	pool = Pool(WORKERS)
	print 'Created pool with size:', WORKERS
	print 'Processing datasets:', len(datasets)

	for index, row in datasets.iterrows():
		dataset = row['database_id']
	#	if index < 11: continue
	#	if dataset != '3tz3-gyhq': continue
	#	if geo_type != 'Geo-GPS': continue

		if last_dataset == dataset and not REPEAT_DATASET: continue
		else: processed += 1

		# process_dataset(row, index, total)
		pool.apply_async(process_dataset, args=(row, index, total))

	#	break
		last_dataset = dataset

	print 'All jobs created. Waiting for results...'
	pool.close()
	pool.join()
	print 'All profilers done.'

	print ' -----------------------------------< ERRORS >------------------------------------------'
	for e in ERRORS: print e, '\n'
	print 'Errors: ', len(ERRORS)
	print ' ------------------------------------< END >------------------------------------------'
	print 'Processed:', processed
	


if __name__ == "__main__":	
	main()

#"2928-i3dn","GRADE DATE","ZIPCODE","Temporal-Date","Geo-ZIP","LES_Dirty","2928-i3dn"
