from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect

urlpatterns = patterns('',
	# Examples:
	# url(r'^$', 'data_finder.views.home', name='home'),
	# url(r'^blog/', include('blog.urls')),
	url(r'^', include('finder.urls', namespace="finder")),
	url(r'^api/', include('api.urls', namespace="api")),
	url(r'^admin/', include(admin.site.urls)),
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon.ico')), #google chrome favicon fix
)

