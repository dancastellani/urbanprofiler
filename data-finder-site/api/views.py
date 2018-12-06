from django.shortcuts import get_object_or_404
from finder.models import Database
from api.serializers import DatabaseOnlySerializer
from rest_framework.decorators import api_view
from rest_framework import generics
from finder import utils
from datetime import datetime

class DatabaseList(generics.ListCreateAPIView):
    queryset = Database.objects.all()
    serializer_class = DatabaseOnlySerializer

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@api_view(['GET'])
def timeline_data(request):
	dataset_ids = request.GET.get('dataset_ids', None)

	param = request.GET.get('date_range', None)
	start = end = None
	if param:
		start, end = param.split('-')
		if start:
			start = datetime.strptime(start, '%m/%d/%Y')
		if end:
			end = datetime.strptime(end, '%m/%d/%Y')

	query = "select to_char(year, 'FM0000') || '-' || to_char(month, 'FM00') as date, \
	cast(sum(count) as bigint) as value \
	from finder_view_index_temp \
	where year is not null and month is not null and day is not null and year >= 1 "
	if start: query += " and year >= {0} and month >= {1} and day >= {2} ".format(start.year, start.month, start.day)
	if end: query += " and year <= {0} and month <= {1} and day <= {2} ".format(end.year, end.month, end.day)
	if not (start or end): query += " and year > 2000 and year < 3000 "
	if dataset_ids:
		# print 'dataset_ids=', eval(dataset_ids)
		dataset_ids = dataset_ids.replace("u\'", "'").replace(';','').lstrip('[').rstrip(']')
		query += ' and db in ({0}) '.format( dataset_ids )
	query += " group by date order by 1 "
	
	# print 'API:timeline_data - query =', query
	data = utils.execute_query(query, fetch='all')
	previous_month = None;
	# print 'data=', data
	if len(data) > 0: 
		previous_month = datetime.strptime(data[0][0], '%Y-%m').date()
		# print 'first =', previous_month
	i = 1
	size_before = len(data)
	while i < len(data):
		# print 'current: data[{0}]={1}'.format(i, data[i])
		current = data[i]
		current_month = datetime.strptime(current[0], '%Y-%m').date()
		months_since_last_point = (current_month - previous_month).days / 30 -1
		# print '	months_since_last_point=', months_since_last_point
		# print '	previous_month=', previous_month
		if months_since_last_point >= 1: #Add one fake month with count 0 
			month = previous_month.month + 1
			year = previous_month.year
			if month > 12:
				month = 1
				year += 1
			fake_point = ('{0:0>4}-{1:0>2}'.format(year, month), 0)
			#Add fake to correct position
			data = data[:i] + [fake_point] + data[i:]
			previous_month = datetime.strptime(fake_point[0], '%Y-%m').date()
			# print '    Added Fake Point: ', fake_point
			i+=1
		if months_since_last_point > 1: #Add another: one after previous and one before current
			month = current_month.month - 1
			year = current_month.year
			if month < 1:
				month = 12
				year -= 1
			fake_point = ('{0:0>4}-{1:0>2}'.format(year, month), 0)
			#Add fake to correct position
			data = data[:i] + [fake_point] + data[i:]
			previous_month = datetime.strptime(fake_point[0], '%Y-%m').date()
			# print '    Added Fake Point: ', fake_point
			i+=1
		
		previous_month = current_month
		i+=1	#While loop interaction

	return JSONResponse(data)

@api_view(['GET'])
def dataset_gps_points(request, database_id):
	database = get_object_or_404(Database, database_id=database_id)

	query = "select lat, long, sum(count) \
			from finder_gpsdata \
			where lat is not null and long is not null and db = '{0}' \
			group by lat, long".format(database_id)
	
	# print 'API:dataset_gps_points - query =', query
	data = utils.execute_query(query, fetch='all')
	return JSONResponse(data)

@api_view(['GET'])
def dataset_squared_heatmap(request, database_id):
	# print 'API:dataset_squared_heatmap'
	database = get_object_or_404(Database, database_id=database_id)

	data = {}
	bins = int(request.GET.get('bins', 30))
	data['bins'] = bins

	# print 'query'
	gpsdata = database.gpsdata_set.exclude(lat__isnull=True).values('lat', 'long', 'count')
	# print 'process'
	squares_data = utils.squared_heatmap_of(gpsdata, bins=bins)
	data['lat_min'] = squares_data[0]
	data['lat_size'] = squares_data[1]
	data['long_min'] = squares_data[2]
	data['long_size'] = squares_data[3]
	data['squares'] = squares_data[4]

	# print 'return'
	return JSONResponse(data)



