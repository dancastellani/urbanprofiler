from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from django.views import generic


from finder import views

urlpatterns = patterns('',
	# url(r'^$', views.index, name='index'),
	url(r'^$', RedirectView.as_view(url='/datasets'), name='index'),
	url(r'^overview$', views.catalog_overview, name='catalog_overview'),
	url(r'^alarms$', views.alarms, name='alarms'),
	url(r'^datasets$', views.DatabaseListView.as_view(), name='list'),
	url(r'^dataset/(?P<database_id>.+)/$', views.detail_database, name='detail-database'),
	url(r'^dataset/(?P<database_id>.+)/map$', views.detail_database_map, name='detail-database-map'),
	url(r'^dataset/(?P<database_id>.+)/data$', views.detail_database_data, name='detail-database-data'),
	url(r'^dataset/(?P<database_id>.+)/columns$', views.detail_database_columns, name='detail-database-columns'),
	url(r'^dataset/(?P<database_id>.+)/column/(?P<column_name>.+)$', views.detail_database_column, name='detail-database-column'),
	url(r'^dataset/(?P<database_id>.+)/charts$', views.detail_database_charts, name='detail-database-charts'),
	url(r'^dataset/(?P<database_id>.+)/related-datasets$', views.detail_dataset_related, name='detail-related-datasets'),
	url(r'^dataset/(?P<database_id>.+)/help$', views.detail_dataset_help, name='detail-dataset-help'),
	url(r'^dataset/(?P<database_id>.+)/(?P<tab>.+)$', views.detail_database, name='detail-database-tab'),
	url(r'^search-map/$', views.seach_map, name='search-map'),
)