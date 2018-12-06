from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = patterns('',
	 # url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
	 url(r'^datasets/$', views.DatabaseList.as_view()),
	 url(r'^datasets/timeline-data/$', views.timeline_data, name='timeline-data'),
	 url(r'^dataset/(?P<database_id>.+)/gps-points$', views.dataset_gps_points, name='dataset-gps-points'),
	 url(r'^dataset/(?P<database_id>.+)/squared-heatmap-data$', views.dataset_squared_heatmap, name='dataset-squared-heatmap-data'),
)

urlpatterns = format_suffix_patterns(urlpatterns)