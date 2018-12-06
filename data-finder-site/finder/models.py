from django.db import models, connection
from django.db.models.signals import post_init
from utils import Types
from utils import DatabaseSQL

from profiler.models import SimpleType, DetailedType

DECIMAL_CASES = 6 # 0,1 meters of precision

# Create your models here.
class Database(models.Model):

	database_id = models.CharField(max_length=256)
	name = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)

	description = models.TextField(blank=True, null=True, db_index=True)
	category = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	owner = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	author = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	source_agency = models.CharField(max_length=256, blank=True, null=True)
	## Socrata keywords
	tags = models.CharField(max_length=3000, blank=True, null=True, db_index=True)
	organization = models.CharField(max_length=100, blank=True, null=True)
	access_type = models.CharField(max_length=20, blank=True, null=True, default='Open')
	hue_status = models.CharField(max_length=20, blank=True, null=True, default='enable')
	
	profiler_input_file = models.CharField(max_length=256, blank=True, null=True)
	profiler_input_file_size = models.DecimalField(max_digits = DECIMAL_CASES + 10, decimal_places = DECIMAL_CASES, blank=True, null=True, default=None)
	profiler_status = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	profiler_status_short = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	profiler_time_begin = models.CharField(max_length=256, blank=True, null=True)
	profiler_time_end = models.CharField(max_length=256, blank=True, null=True)

	metadata_source_url = models.CharField(max_length=256, blank=True, null=True)
	metadata_source_name = models.CharField(max_length=256, blank=True, null=True)

	socrata_status = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	socrata_primary = models.BooleanField(default=False, db_index=True)
	socrata_download_count = models.IntegerField(blank=True, null=True)
	socrata_view_count = models.IntegerField(blank=True, null=True)
	socrata_view_type = models.CharField(max_length=256, blank=True, null=True)
	socrata_display_type = models.CharField(max_length=256, blank=True, null=True)
	socrata_number_of_coments = models.IntegerField(blank=True, null=True, default=0)
	socrata_created_at = models.CharField(max_length=256, blank=True, null=True, db_index=True)
	socrata_last_modified = models.CharField(max_length=256, blank=True, null=True)
	socrata_unique_key = models.CharField(max_length=256, blank=True, null=True)
	socrata_attribution = models.CharField(max_length=256, blank=True, null=True)
	socrata_publication_date = models.CharField(max_length=256, blank=True, null=True)
	socrata_update_frequency = models.CharField(max_length=256, blank=True, null=True)
	socrata_view_from = models.CharField(max_length=20, null=True, blank=True)

	rows = models.IntegerField(blank=True, null=True, default=None)
	columns_count = models.IntegerField(blank=True, null=True, default=None)
	columns_geo_count = models.IntegerField(blank=True, null=True, default=None)
	columns_numeric_count = models.IntegerField(blank=True, null=True, default=None)
	columns_temporal_count = models.IntegerField(blank=True, null=True, default=None)
	columns_text_count = models.IntegerField(blank=True, null=True, default=None)
	columns_null_count = models.IntegerField(blank=True, null=True, default=None)
	values = models.IntegerField(blank=True, null=True, default=None)
	values_missing = models.IntegerField(blank=True, null=True, default=None)

	gps_values = models.IntegerField(blank=True, null=True, default=None, db_index=True)
	# gps_records_count = models.IntegerField(blank=True, null=True, default=None, db_index=True)
	lat_min = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES, blank=True, null=True, default=None)
	lat_max = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES, blank=True, null=True, default=None)
	long_min = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES,blank=True, null=True, default=None)
	long_max = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES, blank=True, null=True, default=None)
	#temporal index reference
	date_min = models.DateField(blank=True, null=True, default=None)	
	date_max = models.DateField(blank=True, null=True, default=None)	

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.database_id

	class Meta:
	 	ordering = ['database_id']

	HUE_BASE_URL = 'https://data.cusp.nyu.edu/metastore/table/'
	HUE_NYC_OPENDATA_URL = HUE_BASE_URL+'nycopendata/'
	HUE_CUSP_URL = HUE_BASE_URL+'cusp_open/'

	def hue_url(self):
		if self.access_type != 'Open' or self.hue_status != 'enabled': return None

		if self.database_id is None: return None
		
		if len(self.database_id) == 9:
			return Database.HUE_NYC_OPENDATA_URL + self.database_id.replace('-', '_')
		else:
			return Database.HUE_CUSP_URL + self.database_id.replace('-', '_')


	def show_input_file(self):
		return self.access_type == 'Open'


	def sql_postgres_copy(self):
		return DatabaseSQL.postgres_copy(self)
	

	def sql_postgres_create(self):
		return DatabaseSQL.postgres_create_table_for_dataset(self)
		

	def download_url(self):
		return 'https://nycopendata.socrata.com/api/views/' + self.database_id + '/rows.csv?accessType=DOWNLOAD'

	def socrata_status_error(self):
		return self.socrata_status is None or self.socrata_status != 'OK'
	
	def profiler_status_error(self):
		return self.profiler_status is None or self.profiler_status != 'OK'

	def title(self):
		if self.name: 	return self.name
		else: 			return self.database_id

	def short_profiler_status(self):
		return self.profiler_status.split(':')[0]

	def missing_percent(self):
		if self.values is None or self.values_missing is None or self.values is 0: return 'N/A'
		else: return round(self.values_missing * 100.0 / self.values, 3)

	def has_bounding_box(self):
		return self.lat_min is not None and self.lat_max is not None and \
			self.long_min is not None and self.long_max is not None

	def bounding_box(self):
		if self.has_bounding_box():
			return '({0}, {1}), ({2}, {3})'.format(self.lat_min, self.long_min, self.lat_max, self.long_max)
		else:
			return ''

	def lat_center(self):
		if self.lat_max is None or self.lat_min is None: return None
		return (self.lat_max + self.lat_min)/2
	
	def long_center(self):
		if self.long_max is None or self.long_min is None: return None
		return (self.long_max + self.long_min)/2

	def metadata_source_url_link(self):
		if self.metadata_source_url is None and \
			self.metadata_source_name is None or self.metadata_source_name is 'NYC OpenData': 
			return 'https://nycopendata.socrata.com/views/' + self.database_id
		else:
			return self.metadata_source_url
	
class Column(models.Model):

	database = models.ForeignKey(Database)
	name = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)

	original = models.BooleanField(default=True)

	profiler_type = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)
	socrata_type = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)
	
	profiler_type_most_detected = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)
	profiler_type_most_detected_percent = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES, blank=True, null=True, default=None)
	
	value_min = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)
	value_max = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)
	value_std = models.CharField(max_length=256, blank=True, null=True, default=None)
	value_mean = models.CharField(max_length=256, blank=True, null=True, default=None)
	#__ for strings
	value_length_min = models.CharField(max_length=256, blank=True, null=True, default=None)
	value_length_max = models.CharField(max_length=256, blank=True, null=True, default=None)
	value_length_mean = models.CharField(max_length=256, blank=True, null=True, default=None)
	value_length_std = models.CharField(max_length=256, blank=True, null=True, default=None)

	values = models.IntegerField(blank=True, null=True, default=None)
	unique = models.IntegerField(blank=True, null=True, default=None)
	missing = models.IntegerField(blank=True, null=True, default=None)
	top_value = models.CharField(max_length=3000, blank=True, null=True, default=None)
	top_freq = models.IntegerField(blank=True, null=True, default=None)
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
	 	ordering = ['database', 'name']

	def __str__(self):
	 	return self.database.database_id + '.' + self.name

	def based_on(self):
		return self.name.split('_@_')[0]

	def unique_percent(self):
		if self.unique is not None and self.values is not None: 
			return self.unique * 100.0 / self.values
		else: return None	

	def missing_percent(self):
		if self.missing is not None and self.values is not None: 
			return self.missing * 100.0 / (self.missing + self.values)
		else: return None	

	def top_freq_percent(self):
		if self.top_freq is None or self.values is None: return None
		return round(self.top_freq * 100.0 / self.values, 2)

	def data(self, key, default=None):
		try:
			return self.columndata_set.get(key=key).value
		except ColumnData.DoesNotExist:
			return default

	def simple_types_to_pie_chart(self):
		types = []
		for a_type in SimpleType.objects.all().order_by('global_order_presentation'):
			types.append( [str(a_type.name), float(self.data(a_type.name))] )

		return types

	def detailed_types_to_pie_chart(self):
		types = []
		for a_type in DetailedType.objects.all().order_by('simple_type__global_order_presentation', 'order_in_type_presentation'):
			# print 'a_type=', a_type
			# print 'a_type.full_name=', a_type.full_name()
			# print 'self.data(a_type.full_name)=', self.data(a_type.full_name(), default=0)
			types.append( [str(a_type.name), float(self.data(a_type.full_name(), default=0))] )
		return types

def post_init_column(**kwargs):
	kwargs.get('instance').column_data = None

post_init.connect(post_init_column, Column)

class ColumnData(models.Model):
	VALUE_MAX_LENGH = 5000

	column = models.ForeignKey(Column)
	group = models.CharField(max_length=256, blank=False, null=False, default=None)
	key = models.CharField(max_length=256, blank=False, null=False, db_index=True)
	value = models.CharField(max_length=VALUE_MAX_LENGH)
	
	class Meta:
	 	ordering = ['column', 'group', 'key']

	def __str__(self):
	 	return self.group + '[' + self.key + ']= ' + self.value



class GpsData(models.Model):
	BOROUGH_MAX_SIZE = 20
	ZIPCODE_MAX_SIZE = 21
	ADDRESS_MAX_SIZE = 500

	database = models.ForeignKey(Database)
	
	lat = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES, blank=True, null=True)
	long = models.DecimalField(max_digits = DECIMAL_CASES + 3, decimal_places = DECIMAL_CASES,blank=True, null=True)

	count  = models.IntegerField(blank=True, null=True, default=1)

	borough = models.CharField(max_length=BOROUGH_MAX_SIZE, blank=True, null=True)
	zipcode = models.CharField(max_length=ZIPCODE_MAX_SIZE, blank=True, null=True, db_index=True)
	address = models.CharField(max_length=ADDRESS_MAX_SIZE, blank=True, null=True)
	
	closest_bbl = models.IntegerField(blank=True, null=True)

	db = models.CharField(max_length=300, blank=True, null=True, db_index=False)

	# epoch_secs  = models.IntegerField(blank=True, null=True, default=1, db_index=True)
	year  = models.IntegerField(blank=True, null=True, default=1)
	month  = models.IntegerField(blank=True, null=True, default=1)
	day  = models.IntegerField(blank=True, null=True, default=1)
	# hour  = models.IntegerField(blank=True, null=True, default=1, db_index=True)

	class Meta:
	 	ordering = ['database__id', 'lat', 'long']
		index_together = [
			("lat", "long"),
			# ("year", "month", 'day'),
		]

	def lat_as_float(self):
		return float(self.lat)

	def long_as_float(self):
		return float(self.long)

	def __str__(self):
	 	return '{0} - ({1}, {2}) :: {3}'.format(self.database.database_id, self.lat, self.long, self.count)

class Alarm(models.Model):
	name = models.CharField(max_length=256, default=None, unique=True)
	query = models.CharField(max_length=1000, default=None)
	count  = models.IntegerField(blank=True, null=True)

	SEVERITY_HIGH='1'
	SEVERITY_NORMAL='2'
	SEVERITY_LOW='3'
	SEVERITY_CHOICES = (
		(SEVERITY_HIGH, 'High'),
		(SEVERITY_NORMAL, 'Normal'),
		(SEVERITY_LOW, 'Low'),
	)
	severity  = models.CharField(max_length=256, choices=SEVERITY_CHOICES, default=SEVERITY_NORMAL)
	
	TARGET_COLUMN='finder_column'
	TARGET_DATABASE='finder_database'
	TARGET_CHOICES = (
		(TARGET_COLUMN, 'Column'),
		(TARGET_DATABASE, 'Dataset'),
	)
	target  = models.CharField(max_length=256, choices=TARGET_CHOICES, default=TARGET_COLUMN)

	class Meta:
	 	ordering = ['severity', '-count', 'name']

	def __str__(self):
		return self.name

	def result_count(self):
		cursor = connection.cursor();
		cursor.execute(self.query.replace('select *', 'select count(*)')); 
		count = cursor.fetchone()
		if count: 
			return int(count[0])
		else:
			return 0

	def results(self):
		results = Column.objects.raw(self.query.replace('%', '%%'))
		if results:
			return results[:]

		else:
			return None


class System(models.Model):
	update_time = models.DateTimeField(auto_now_add=True)
	source_file = models.CharField(max_length=256, blank=False, null=False, default=None)

	def source_file_only(self):
		return self.source_file.split('/')[-1]

	class Meta:
		get_latest_by = "update_time"
		ordering = ['-update_time']




########### --------------------------------------- Materialized Views -------------------------------
# class MaterializedViewModel(models.Model):
# 	SQL_CREATE = None
# 	VIEW_NAME = None
# 	managed = False

class ViewIndexTemporal(models.Model):
	VIEW_NAME = 'finder_view_index_temp'
	SQL_CREATE = 'create materialized view finder_view_index_temp as \
					SELECT db, year, month, day, sum(count) AS count \
					FROM finder_gpsdata \
					WHERE year IS NOT NULL AND db IS NOT NULL \
					GROUP BY db, year, month, day;'

	year  = models.IntegerField()
	month  = models.IntegerField()
	day  = models.IntegerField()
	count  = models.IntegerField()

	class Meta:
		db_table = 'view_index_temp'
		managed = False
		ordering = ['year', 'month', 'day']
