from django.db import connection
import json
from decimal import *
from django.db import transaction
from django.db.models.query import ValuesQuerySet
import re

def refresh_materialized_view_model(model):
	execute_query('refresh materialized view {0} with data'.format(model.VIEW_NAME), fetch=None)

def sql_count_null_or_not_null(column, label_not_null = 'Null', label_null = 'Not Null', zero_as_null = True):
	query = "select '{1}', count(*) from finder_database where {0} is not null and {0} <> 0 union select  '{2}', count(*) from finder_database where {0} is null or {0} = 0 order by 1 desc".format(column, label_not_null, label_null)
	if not zero_as_null: query = query.replace('and {0} <> 0'.format(column))
	if not zero_as_null: query = query.replace('or {0} = 0'.format(column))
	return query

def execute_query(query, fetch='all'):
	cursor = connection.cursor()
	cursor.execute(query)
	if fetch == 'all': return cursor.fetchall()
	if fetch == 'one': return cursor.fetchone()
	if fetch == 'dict': return dictfetchall(cursor)
	if fetch == 'commit': transaction.commit_unless_managed()

def query_result_as_csv(results):
	csv = ''
	for result in results:
		csv += ','.join( map(str, result) ) + '\n'
	return csv

def query_result_as_tsv(results):
	tsv = ''
	for result in results:
		tsv += '\t'.join( map(str, result) ) + '\n'
	return tsv

def dictfetchall(cursor): 
    "Returns all rows from a cursor as a dict" 
    desc = cursor.description 
    return [
            dict(zip([col[0] for col in desc], row)) 
            for row in cursor.fetchall() 
    ]

@transaction.atomic
def bulk_save(object_list):
    for item in object_list:
        item.save()

def dict_to_lists_json(a_dict, transpost=False):
	if type(a_dict) is dict:
		#turn into json list
		if transpost:
			str_lists_json = '[ ['
			#headers
			for k in a_dict.keys():
				str_lists_json += ' "{0}",'.format( k.replace('_', ' ') )
			str_lists_json = str_lists_json[:-1] + '], ['
			#values
			for k in a_dict.keys():
				str_lists_json += ' {0},'.format( a_dict[k] )
			str_lists_json = str_lists_json[:-1] + '] ]'

		else:
			str_lists_json = '['
			for k in a_dict.keys():
				str_lists_json += '["{0}", {1}],'.format(k.replace('_', ' '), a_dict[k])
			str_lists_json = str_lists_json[:-1] + ']'
		
		return str_lists_json
	elif a_dict is not None and a_dict.__class__.__name__ == 'ValuesQuerySet':
		str_values = a_dict.__str__()
		str_values = str_values.replace('{', '[')
		print 'str_values=',str_values
		return str_values

	return json.dumps(a_dict)


def as_json(obj):
	return json.dumps(obj)

def execute_query_as_json(query, sort=True):
	return json.dumps(execute_query(query), sort_keys = sort)

def count_as_json(column, from_model = 'database', include_nulls = False, sort = True, order_by_counts=True, limit=None):
	return json.dumps( count_value(column, from_model, include_nulls, order_by_counts, limit=limit), sort_keys = sort)

def count_value(column, from_model = 'database', include_nulls = False, order_by_counts=True, limit=None, where=None):
	# Select
	sql_query = 'select {0}, count(*) from finder_{1} where {0} is not null'.format(column, from_model)
	if include_nulls is True:
		sql_query = sql_query.replace('where {0} is not null '.format(column), '')
	# Where - More
	if where: 
		if 'where' in sql_query: sql_query += ' and '
		else: sql_query += ' where '
		sql_query += '{0} '.format(where)
	# Group by
	sql_query += ' group by {0} '.format(column)
	# Order by
	if order_by_counts: sql_query += ' order by 2 desc'
	else: sql_query += ' order by 1'
	# Limit
	if limit is not None: sql_query += ' limit {0}'.format(limit)
	# Execute and return
	# print 'query =', sql_query
	return execute_query(sql_query)

# class HeatMapUtils:
DEFAULT_SIZE = 10
def squared_heatmap_of(gps_list, bins = DEFAULT_SIZE):
	#initialize squares
	squares = [ [ 0 for i in range(bins) ] for j in range(bins) ]

	lat_min, long_min, lat_max, long_max = bounds_of(gps_list)

	#find square size
	lat_size = (Decimal(lat_max) - Decimal(lat_min)) / Decimal(bins)
	long_size = (Decimal(long_max) - Decimal(long_min)) / Decimal(bins)

	

	#find correct square for this point and increment count
	for gps in gps_list:
		i = int ( (Decimal(gps['lat']) - Decimal(lat_min)) / lat_size )
		j = int ( (Decimal(gps['long']) - Decimal(long_min)) / long_size )

		if i >= bins: i = bins -1 
		if j >= bins: j = bins -1

		squares[i][j] += gps['count']

	return float(lat_min), float(lat_size), float(long_min), float(long_size), squares

def bounds_of(gps_list):
	# import pdb; pdb.set_trace()
	# print 'gps_list=', gps_list
	if len(gps_list) == 0:
		return None, None, None, None

	lat_min = lat_max =  gps_list[0]['lat']
	long_min = long_max =  gps_list[0]['long']

	for gps in gps_list:
	 	if gps['lat'] < lat_min: lat_min = gps['lat']
	 	if gps['lat'] > lat_max: lat_max = gps['lat']
	 	if gps['long'] < long_min: long_min = gps['long']
	 	if gps['long'] > long_max: long_max = gps['long']

	return lat_min, long_min, lat_max, long_max

# Default Google Charts Color array
#{"#3366cc","#dc3912","#ff9900","#109618","#990099","#0099c6","#dd4477","#66aa00","#b82e2e","#316395","#994499","#22aa99","#aaaa11","#6633cc","#e67300","#8b0707","#651067","#329262","#5574a6","#3b3eac","#b77322","#16d620","#b91383","#f4359e","#9c5935","#a9c413","#2a778d","#668d1c","#bea413","#0c5922","#743411"}
class GoogleChartsColors:
	BLUE = '#3366cc'
	RED = "#dc3912"
	GRAY = 'gray'
	YELLOW = '#EEB211'
	TRANSPARENT = 'transparent'

	PALLETE = ["#3366cc","#dc3912","#ff9900","#109618","#990099","#0099c6","#dd4477","#66aa00","#b82e2e","#316395","#994499","#22aa99","#aaaa11","#6633cc","#e67300","#8b0707","#651067","#329262","#5574a6","#3b3eac","#b77322","#16d620","#b91383","#f4359e","#9c5935","#a9c413","#2a778d","#668d1c","#bea413","#0c5922","#743411"]

class Types:
	GEO = 'Geo'
	NULL = 'Null'
	NUMERIC = 'Numeric'
	TEMPORAL = 'Temporal' 
	TEXTUAL = 'Textual'

	GEO_ADDRESS = "Geo-Adress"	
	GEO_BOROUGH = "Geo-BOROUGH"	
	GEO_GPS = "Geo-GPS"
	GEO_ZIP = "Geo-ZIP"	
	GEO_ZIP_9 = "Geo-ZIP+4"
	NUMERIC_INT = "Numeric-Integer"
	NUMERIC_DOUBLE = "Numeric-Double"	
	TEMPORAL_DATE = "Temporal-Date"	
	TEMPORAL_TIME = "Temporal-Time"	
	TEMPORAL_DATE_TIME = "Temporal-DateTime"	

class TypeColors:

	SIMPLE_TYPE_COLORS = None
	@classmethod
	def simple_type_colors(cls):
		if cls.SIMPLE_TYPE_COLORS is None:
			from profiler.models import SimpleType
			cls.SIMPLE_TYPE_COLORS = []
			for a_type in SimpleType.objects.all().order_by('global_order_presentation'):
				cls.SIMPLE_TYPE_COLORS.append(str(a_type.color))
		return cls.SIMPLE_TYPE_COLORS

	DETAILED_TYPE_COLORS = None
	@classmethod
	def detailed_type_colors(cls):
		if cls.DETAILED_TYPE_COLORS is None:
			from profiler.models import DetailedType
			cls.DETAILED_TYPE_COLORS = []
			for a_type in DetailedType.objects.all().order_by('simple_type__global_order_presentation', 'order_in_type_presentation'):
				cls.DETAILED_TYPE_COLORS.append(str(a_type.color))
		return cls.DETAILED_TYPE_COLORS


class DatabaseSQL:

	REGEX_DB_INVALID_CHARS = re.compile('[^\w]+')

	@classmethod
	def postgres_create_table_for_dataset(cls, dataset):
		table_name = DatabaseSQL.REGEX_DB_INVALID_CHARS.sub('_', dataset.database_id)
		sql = 'create table ' + table_name + ' ('
		for col in dataset.column_set.all():
			col_name = DatabaseSQL.REGEX_DB_INVALID_CHARS.sub('_', col.name)
			col_type = DatabaseSQL.postgres_type_for_column(col)
			sql += ' {0} {1},'.format(col_name, col_type)

		sql = sql[:-1] + ' );'
		return sql

	@classmethod
	def postgres_type_for_column(cls, column):
		# if column.profiler_type in ['']:
		# 	return integer
		return 'character varying(1024)'

	@classmethod
	def postgres_copy(cls, dataset):
		table_name = DatabaseSQL.REGEX_DB_INVALID_CHARS.sub('_', dataset.database_id)
		return "COPY {0} FROM '{1}' DELIMITERS ',' CSV HEADER;".format(table_name, dataset.profiler_input_file)

	