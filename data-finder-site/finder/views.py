from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from django.db.models import Count, Sum, Q

from finder.models import Database, Column, Alarm, System
from profiler.models import SimpleType, DetailedType
import utils
from utils import GoogleChartsColors as GColors
from utils import TypeColors
import math
from datetime import datetime
import ast

# from django.views.decorators.cache import cache_page

def setup_filter_options(context, object_list = None):
	where_column = where = None
	ids = None
	BASE_SQL_COUNT = 'select {0}, count(distinct database_id) from finder_column where {0} is not null group by {0} order by 1'
	if object_list:
		ids = []
		# get ids from 
		for ds in object_list:
			ids.append('{0}'.format(ds.id))
		ids = ','.join(ids)
		where = 'finder_database.id in ({0})'.format( ids )
		where_column = ' database_id in ({0})'.format( ids )
		BASE_SQL_COUNT = 'select {0}, count(distinct database_id) from finder_column where {0} is not null and database_id in ({1}) group by {0} order by 1'

	context['options_category'] = utils.count_value('category', where=where)
	context['options_profiler_status'] = utils.count_value('profiler_status_short', include_nulls=False, where=where)
	context['options_source_agency'] = utils.count_value('source_agency', include_nulls=False, where=where, order_by_counts=False)
	context['options_socrata_status'] = utils.count_value('socrata_status', include_nulls=False, where=where, order_by_counts=False)
	context['simple_types'] = utils.execute_query(BASE_SQL_COUNT.format('profiler_type', ids))
	context['detailed_types'] = utils.execute_query(BASE_SQL_COUNT.format('profiler_type_most_detected', ids))
	context['options_socrata_type'] = utils.execute_query(BASE_SQL_COUNT.format('socrata_type', ids))
	context['options_update_frequency'] = utils.count_value('socrata_update_frequency', where=where, order_by_counts=False)



def filter_datasets_with_params(request, context, queryset=None):
	if queryset is None: queryset = Database.objects.all()

	# Category
	param = request.GET.get('category', None)
	if param is not None: 
		if param == 'None': queryset = queryset.filter(category__isnull=True)
		else: queryset = queryset.filter(category=param)
	
	# Source/Agency
	param = request.GET.get('agency', None)
	if param is not None: 
		if param == 'None': queryset = queryset.filter(source_agency__isnull=True)
		else: queryset = queryset.filter(source_agency=param)

	# Update Frequency
	param = request.GET.get('update_frequency', None)
	if param is not None: 
		if param == 'None': queryset = queryset.filter(socrata_update_frequency__isnull=True)
		else: queryset = queryset.filter(socrata_update_frequency=param)

	# Profiler Status
	param = request.GET.get('profiler_status', 'OK')
	# print 'profiler status= "'+ param + '"'
	if param is not None: 
		param = param.split('\n')[0]
		queryset = queryset.filter( Q(profiler_status_short=param) | Q(profiler_status__like=param+'%') )

	# Socrata Primary
	param = request.GET.get('primary', None)
	if param is not None: queryset = queryset.filter(socrata_primary=param=='True')

	# Original Column
	param = request.GET.get('column_original', None)
	if param is not None: queryset = queryset.filter(socrata_primary=param=='True')


	# Column Type = Simple or Detailed
	param = request.GET.get('column_type', None)
	if param == 'Geo-ZIP 4': param = 'Geo-ZIP+4' ##TODO: Fix this on the right way.
	if param is not None: queryset = queryset.filter(
													Q(column__profiler_type=param) |  
													Q(column__profiler_type_most_detected=param)
													)
	
	# Provided Type
	param = request.GET.get('provided_type', None)
	if param is not None: queryset = queryset.filter( Q(column__socrata_type=param) )

	# Socrata Status
	DEFAULT = -1
	param = request.GET.get('metadata_retrieval_status', DEFAULT)
	if param != DEFAULT and param is not None: queryset = queryset.filter(socrata_status__isnull=False, socrata_status=param )
	elif param is None: queryset = queryset.filter( socrata_status__isnull=True )

	# Text filter: Database Id, Name, tags, description, etc...
	param = request.GET.get('search_text', None)
	if param: 
		#split param and gerate or statements
		param_list = param.split(' ')
		text_search_filters = None
		
		for a_param in param_list:
			one_filter = Q(database_id__icontains=a_param) | Q(name__icontains=a_param) | \
							Q(description__icontains=a_param) | Q(category__icontains=a_param) | \
							Q(tags__icontains=a_param) | Q(source_agency__icontains=a_param) | \
							Q(column__name__icontains=a_param) 

			if text_search_filters is None: text_search_filters = one_filter
			else: text_search_filters |= one_filter
		queryset = queryset.filter(text_search_filters)

	# geo_zipcode
	param = request.GET.get('zipcode', None)
	if param is not None: queryset = queryset.filter(gpsdata__zipcode=param)

	# date_range
	param = request.GET.get('date_range', None)
	# print 'param=', param
	if param is not None: 
		start, end = param.split('-')
		if start:
			start = datetime.strptime(start, '%m/%d/%Y')
			queryset = queryset.filter(date_max__gte=start)
		if end:
			end = datetime.strptime(end, '%m/%d/%Y')
			queryset = queryset.filter(date_min__lte=end)
		
	date_range = param or '-'

	# print '>>> queryset.query=', queryset.query

	#Order by download counts
	queryset = queryset.order_by('-socrata_download_count', 'name', 'database_id')
	queryset = queryset.extra(select={'socrata_download_count_null':'socrata_download_count is null'})
	queryset = queryset.extra(order_by = ['socrata_download_count_null'])
	
	results = queryset.distinct()
	ds_ids = []
	for ds in results:
		ds_ids.append(ds.database_id)
	
	#Setup the timeline api query params
	if context is not None: 
		api_timeline_query = ''
		if date_range: api_timeline_query += '?date_range={0}'.format(date_range)
		if len(ds_ids) > 0: api_timeline_query += '&dataset_ids={0}'.format(ds_ids)
		context['api_timeline_query'] = api_timeline_query
	return results


def seach_map(request):
	context = {}
	queryset = Database.objects.exclude(lat_min = None, lat_max = None, long_min = None, long_max = None).order_by('lat_min', '-lat_max','database_id')
	queryset = filter_datasets_with_params(request, context, queryset)
	datasets = queryset.all()
	context['databaseBoundingBoxes'] = datasets
	setup_filter_options(context, datasets)

	#Display map style
	map_type = request.GET.get('map_style', 'boxes')
	if map_type is not None:
		if map_type == 'borough':
			areas = utils.execute_query("select boroname, ST_AsGeoJSON(geom) from nyc_boroughs")
			named_areas = []
		
			for area in areas:
				named_areas.append({'title': area[0].encode('ascii','ignore'),
									'geojson': ast.literal_eval(area[1])})
			context['named_areas'] = named_areas
			context['map_center'] = 'NYC'
		elif map_type == 'single-heatmap':
			# ids = Database.objects.filter(category='Education').values_list('id', flat=True).order_by('id')
			ids = queryset.values_list('id', flat=True).order_by('id')
			gps_data = utils.execute_query('select lat::float, long::float, sum(count)::int from finder_gpsdata where lat is not null and database_id in ({0}) group by lat, long '.format( str(ids[:10])[1:-1] ))
			
			context['gps_data'] = gps_data
			print 'dbs=', len(ids)
			print 'gps_data=', len(gps_data)


	context['map_style'] = map_type

	return render(request, 'finder/search-map.html', context)


class DatabaseListView(generic.ListView):	
	model = Database
	template_name = 'finder/list.html'
	context_object_name = 'databases'
	paginate_by = 50

	def get_queryset(self):
		queryset = filter_datasets_with_params(self.request, None)
		self.total = queryset.count()

		return queryset

	def get_context_data(self, **kwargs):
		context = super(DatabaseListView, self).get_context_data(**kwargs)

		context['query_result_count'] = self.total
		object_list = context['object_list']
		setup_filter_options(context, object_list=self.object_list)

		return context

	# def dispatch(self, request, *args, **kwargs):
	# 	queryset = self.get_queryset()
	# 	if queryset.count() == 1:
	# 		return redirect('detail-database', database_id=queryset.only('id')[0])
	# 	else:
	# 		return super(DatabaseListView, self).dispatch(request, *args, **kwargs)

	
# @cache_page(60 * 15) #Cache for 15 minutes
def catalog_overview(request):
	context = {}

	if Database.objects.count() > 0: context['chart_list'] = [
				 	{ 'title':'Dataset Categories', 
						'data': utils.count_as_json('category', order_by_counts=False),
						'colors':GColors.PALLETE},
					{ 'title':'Rows by Category', 
						'data': utils.execute_query_as_json('select category, sum(rows) from finder_database where profiler_status = \'OK\' and category is not null group by category order by 1'),
						'colors':GColors.PALLETE},
					{ 'title':'Datasets w/ Geo Data', 
						'data': utils.execute_query_as_json( utils.sql_count_null_or_not_null('columns_geo_count', label_not_null='Have', label_null='Don`t Have'), sort=False),
						'colors': [GColors.BLUE,  GColors.RED] },
					{ 'title':'Datasets with GPS', 
						'data': utils.execute_query_as_json( utils.sql_count_null_or_not_null('gps_values', label_not_null='Have', label_null='Don`t Have'), sort=False),
						'colors': [GColors.BLUE,  GColors.RED] },
					{ 'title':'Datasets w/ Temp. Data', 
						'data': utils.execute_query_as_json( utils.sql_count_null_or_not_null('columns_temporal_count', label_not_null='Have', label_null='Don`t Have'), sort=False),
						'colors': [GColors.BLUE,  GColors.RED] },
					{ 'title':'Datasets w/ Num. Data', 
						'data': utils.execute_query_as_json( utils.sql_count_null_or_not_null('columns_numeric_count', label_not_null='Have', label_null='Don`t Have'), sort=False),
						'colors': [GColors.BLUE,  GColors.RED] },
					{ 'title':'Datasets w/ Text. Data', 
						'data': utils.execute_query_as_json( utils.sql_count_null_or_not_null('columns_text_count', label_not_null='Have', label_null='Don`t Have'), sort=False),
						'colors': [GColors.BLUE,  GColors.RED],
					},
					{ 'title':'Socrata Status', 
						'data': utils.count_as_json('socrata_status', include_nulls=True),
						'colors': [GColors.BLUE,  GColors.RED],
					},
					{ 'title':'Top 5 Dataset Owners', 
						'data': utils.count_as_json('owner', limit=5),
						'full_data': utils.count_as_json('owner'),
						'colors':GColors.PALLETE
					},
					{ 'title':'Top 5 Dataset Authors', 
						'data': utils.count_as_json('author', limit=5),
						'full_data': utils.count_as_json('author'),
						'colors':GColors.PALLETE
					},
					{ 'title':'Provided Types', 
						'data': utils.count_as_json('socrata_type', from_model='Column', limit=5),
						'full_data': utils.count_as_json('socrata_type', from_model='Column'),
						'colors':GColors.PALLETE
					},
					{ 'title':'Dataset Rows Histogram (k)', #log(2, rows)::int
						'data': utils.execute_query_as_json('select rows/1000 from finder_database where rows is not null and rows != 0 order by 1'),
						# 'data': utils.execute_query_as_json('select ln(rows) from finder_database where rows is not null and rows != 0 order by 1'),
						'type': 'histogram',
						# 'colors': [GColors.BLUE],
					},
					{ 'title':'Dataset Columns Histogram', 
						'data': utils.execute_query_as_json('select columns_count from finder_database where columns_count is not null order by 1'),
						'type': 'histogram',
						# 'colors': [GColors.BLUE],
					},
					{ 'title':'Geo Columns Histogram', 
						'data': utils.execute_query_as_json('select columns_geo_count from finder_database where columns_geo_count is not null order by 1'),
						'type': 'histogram',
						'colors': [str(SimpleType.objects.get(name='Geo').color)],
					},
					{ 'title':'Temporal Columns Histogram', 
						'data': utils.execute_query_as_json('select columns_temporal_count from finder_database where columns_temporal_count is not null order by 1'),
						'type': 'histogram',
						'colors': [str(SimpleType.objects.get(name='Temporal').color)],
					},
					{ 'title':'Numeric Columns Histogram', 
						'data': utils.execute_query_as_json('select columns_numeric_count from finder_database where columns_numeric_count is not null order by 1'),
						'type': 'histogram',
						'colors': [str(SimpleType.objects.get(name='Numeric').color)],
					},
					{ 'title':'Textual Columns Histogram', 
						'data': utils.execute_query_as_json('select columns_text_count from finder_database where columns_text_count is not null order by 1'),
						'type': 'histogram',
						'colors': [str(SimpleType.objects.get(name='Textual').color)],
					},
#					{ 'title':'Geo Index', 
#						'data': utils.execute_query_as_json("(select 'Address', count(*) from finder_gpsdata where address is not null) union \
#															(select 'Borough', count(*) from finder_gpsdata where borough is not null) union \
#															(select 'GPS', count(*) from finder_gpsdata where lat is not null) union \
#															(select 'Zipcode', count(*) from finder_gpsdata where zipcode is not null) union \
#															(select 'Total', count(*) from finder_gpsdata) ", sort=False),
#						'type': 'column',
#						'colors':GColors.PALLETE,
#					},
	]
	
	data = utils.execute_query_as_json('select columns_null_count from finder_database where columns_null_count is not null order by 1')
	
	# if data and len(data) > 0 and (type(data) == str and data != '[]'):
	# 	context['chart_list'].append({ 'title':'Null Columns Histogram', 
	# 					'data': data,
	# 					'type': 'histogram',
	# 					'colors': [str(SimpleType.objects.get(name='Null').color)],
	# 				})
	context['chart_profiler_status'] = {'data': utils.count_as_json('profiler_status_short', order_by_counts=False), 
						 'colors': [GColors.RED, GColors.BLUE, GColors.GRAY]
						}
	context['errors'] = utils.execute_query('select profiler_status, count(*) from finder_database where profiler_status like \'Error:%\' group by profiler_status having count(*) > 1 order by 2 desc limit 6')
	
	context['column_type_counts'] = { 'data':utils.count_as_json('profiler_type', from_model='column', order_by_counts=False),
										'colors': TypeColors.simple_type_colors()}
	data = utils.count_value('profiler_type_most_detected', from_model='column', order_by_counts=False)
	# print 'data= ', data
	SQL_COUNT_DETAILED_TYPES_ON_COLUMNS = "\
							select dt.name as type, \
								(select count(*) \
								 from finder_column c \
								 where (dt.name = st.name and dt.name = c.profiler_type_most_detected) \
									or (dt.name <> st.name and st.name || '-' || dt.name = c.profiler_type_most_detected) \
								) as count \
							from profiler_simpletype st \
								join profiler_detailedtype dt on dt.simple_type_id = st.id \
							order by st.global_order_presentation, dt.order_in_type_presentation;"
	context['column_type_detailed_counts'] = {"data": utils.execute_query_as_json(SQL_COUNT_DETAILED_TYPES_ON_COLUMNS),
												'colors': TypeColors.detailed_type_colors()}

	context['datasets_total'] = Database.objects.count()
	context['datasets_total_size'] = Database.objects.filter(profiler_status='OK').aggregate(sum=Sum('profiler_input_file_size'))['sum']
	context['datasets_total_size'] = round(float(context['datasets_total_size']) / 1000000.0, 1) if type(context['datasets_total_size']) is float else 0 #Giga
	context['datasets_success'] = Database.objects.filter(profiler_status='OK').count()
	context['datasets_success_percent'] = round(context['datasets_success'] * 100.0 / context['datasets_total'], 2) if context['datasets_total'] > 0  else 0
	context['columns_total'] = Column.objects.count()
	context['columns_names_distinct'] = Column.objects.values('name').distinct().count()
	context['columns_names_distinct_percent'] = round(context['columns_names_distinct'] * 100.0 / context['columns_total'], 2) if context['columns_total'] > 0  else 0
	context['records_total'] = Database.objects.filter(profiler_status='OK').aggregate(sum=Sum('rows'))['sum']
	context['values_total'] = Database.objects.filter(profiler_status='OK').aggregate(sum=Sum('values'))['sum']
	context['values_missing'] = Database.objects.filter(profiler_status='OK').aggregate(sum=Sum('values_missing'))['sum']
	context['values_missing_percent'] = round(context['values_missing'] * 100.0 / context['values_total'], 2)  if context['values_total'] > 0  else 0
	try: 
		context['system'] = System.objects.latest('update_time')
	except (System.DoesNotExist) as e:
		context['system'] = 'No system data. Make sure to import something first.'
		# print 'System info not found.'

	return render(request, 'finder/profiler_info.html', context)


def init_detail_dataset(request, database_id):
	database = get_object_or_404(Database, database_id=database_id)
	# tab = request.GET.get('tab', '')
	# if tab not in ['data', 'map', 'charts', 'columns']: tab = 'data'
	context = {'db': database}
	context['columns_count'] = database.columns_count

	if database.profiler_status != 'OK' or database.socrata_status != 'OK': 
		if database.profiler_status != 'OK' and database.socrata_status != 'OK':
			error_message = "There was an error retrieving metadata and also profiling this dataset."
		elif database.profiler_status != 'OK':
			error_message = 'There was an error profiling this dataset. \
							 But you can still check the provided metadata.'
		elif database.socrata_status != 'OK':
			error_message = "There was an error retrieving metadata for this dataset. \
							But you can check the profiled metadata."
		context['error_message'] = error_message

	return context, database

def detail_database(request, database_id):
	return detail_database_data(request, database_id)

def detail_database_data(request, database_id):
	context, database = init_detail_dataset(request, database_id)
	context['tab'] = 'data'
	# context['gps_data_count'] = database.gpsdata_set.aggregate(Sum('count'))['count__sum']

	return render(request, 'finder/detail.html', context)

def detail_database_charts(request, database_id):
	context, database = init_detail_dataset(request, database_id)
	context['tab'] = 'charts'
	#
	context['column_type_counts'] = { 
		'data': [['Geo', database.columns_geo_count],
				['Null', database.columns_null_count],
				['Numeric', database.columns_numeric_count],
				['Temporal', database.columns_temporal_count],
				['Text', database.columns_text_count]],
		'colors': TypeColors.simple_type_colors()
		}
	detailed_type_counts_data = []
	types= DetailedType.objects.order_by('simple_type__global_order_presentation', 'order_in_type_presentation').all()
	for detailed_type in types:
		count = database.column_set.filter(profiler_type_most_detected=detailed_type.full_name).count()
		if count is None: count = 0
		detailed_type_counts_data.append([ str(detailed_type.full_name()), count])
	context['column_detailed_type_counts'] = { 	
				'data': detailed_type_counts_data,
				'colors': TypeColors.detailed_type_colors()
	}
	context['missing_relation'] = { 
				'data': [['Values', database.values],
						['Missing', database.values_missing]],
				'colors': [GColors.BLUE, GColors.RED]
	}
	context['columns_unique_percent'] = {
		'data': utils.execute_query_as_json('select "name", "values", "unique" from finder_column where database_id = {0} order by 1'.format(database.id)),
		'colors': [GColors.BLUE, GColors.YELLOW]
		}
	context['columns_missing_values'] = {'data': utils.execute_query_as_json('select "name", "values", "missing" from finder_column where database_id = {0} order by 1'.format(database.id))}
	
	return render(request, 'finder/detail.html', context)

def detail_dataset_help(request, database_id):
	context, database = init_detail_dataset(request, database_id)
	context['tab'] = 'dataset-help'
	
	return render(request, 'finder/detail.html', context)

def init_detail_columns(request, database_id):
	context, database = init_detail_dataset(request, database_id)
	context['tab'] = 'columns'
	context['columns'] = database.column_set.all()
	return context

def detail_database_columns(request, database_id):
	context = init_detail_columns(request, database_id)
	return render(request, 'finder/detail.html', context)

def detail_database_column(request, database_id, column_name):
	context = init_detail_columns(request, database_id)
	column = Column.objects.get(database_id = context['db'].id, name = column_name)
	context['column'] = column
	context['simple_types_to_pie_chart'] = column.simple_types_to_pie_chart()
	context['color_types_simple'] = TypeColors.simple_type_colors()
	context['detailed_types_to_pie_chart'] = column.detailed_types_to_pie_chart()
	context['color_types_detailed'] = TypeColors.detailed_type_colors()

	#Column details
	context['top_value'] = column.data('top-value')
	context['top_freq'] = column.data('top-freq')
	context['top_freq_percent'] = round( float(context['top_freq']) * 100 / column.values, 2)
	context['value_min'] = column.data('min')
	context['value_max'] = column.data('max')
	context['value_mean'] = column.data('mean')
	context['value_std'] = column.data('std')
	context['value_length_min'] = column.data('length-min')
	context['value_length_max'] = column.data('length-max')
	context['value_length_mean'] = column.data('length-mean')
	context['value_length_std'] = column.data('length-std')

	if request.GET.get('debug', False):
		context['full_column_data'] = column.columndata_set.all()

	# detailed_type_name = column.profiler_type_most_detected
	# if '-' in detailed_type_name: detailed_type_name = detailed_type_name.split('-')[1]
	# context['chart_colors'] = [DetailedType.objects.get(name=detailed_type_name).color]
	# print 'color:', context['chart_colors']

	if column.data('Histogram Data JSON'):
		temp = column.data('Histogram Data JSON').replace('{', '[[').replace('}', ']]')
		temp = temp.replace(',', '], [').replace(':', ',').replace('"', '')
		temp = eval(temp)
		hist = []
		last = temp[0]
		for e in temp[1:]:
			hist += [['{}-{}'.format(last[0], e[0]), last[1]]]
			last = e
		val_max = column.data('max')
		hist += [['{}-{}'.format(last[0], val_max), last[1]]]
		context['column_histogram'] = hist

	if column.data('top-k'):
		context['column_top_k'] = column.data('top-k').replace('{', '[[').replace('}', ']]').replace(',', '], [').replace(':', ',')#.replace('"', '')

	return render(request, 'finder/detail.html', context)

def detail_dataset_related(request, database_id):
	context, dataset = init_detail_dataset(request, database_id)
	context['tab'] = 'related-datasets'

	# datasets_with_same_tag = []
	# for tag in dataset.tags.split(' '):
		# datasets_with_same_tag += Database.objects.filter(tags__icontains=tag)
	# context['datasets_with_same_tag'] = datasets_with_same_tag

	context['datasets_with_same_category'] =  Database.objects.filter(category=dataset.category).distinct()
	column_names = []
	for col in dataset.column_set.all(): column_names.append(col.name)
	print 'column_names=', column_names
	context['datasets_with_same_column_name'] = \
			Column.objects.filter(name__in=column_names).exclude(database_id=dataset.id) \
			.order_by( 'database__name', 'name') \
			.distinct()

	return render(request, 'finder/detail.html', context)

def detail_database_map(request, database_id):
	context, database = init_detail_dataset(request, database_id)
	context['tab'] = 'map'
	#
	context['type'] = 'heatmap'
	context['api_timeline_query'] = "?dataset_ids='{0}'".format(database_id)

	return render(request, 'finder/detail.html', context)

def alarms(request):
	context = {'alarms': Alarm.objects.all()}
	context['columns_count'] = Column.objects.count()

	alarm_id = request.GET.get('detail', None)
	if alarm_id:
		alarm = get_object_or_404(Alarm, id=alarm_id)
		context['alarm'] = alarm
		context['results'] = alarm.results()

	return render(request, 'finder/alarms.html', context)
