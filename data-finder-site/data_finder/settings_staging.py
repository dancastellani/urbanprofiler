########## SETTINGS FOR STAGING ENVIRONMENT ##########

# Import all conf from settings_base and then update what is needed.
from settings_base import *

# Must Change to False
DEBUG = False
TEMPLATE_DEBUG = DEBUG

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

STATIC_ROOT = '/files/webapps/urbanprofiler/site/static'
STATIC_URL = '/static/'
MEDIA_ROOT = '/files/webapps/urbanprofiler/site/media'
MEDIA_URL = '/media/'

SECRE_KEY = '!!$yd9iq%p00lp7(dbtk%_m27+&h&i8-8ufj^43r=yl+mpgcas'

ALLOWED_HOSTS = ['localhost',
                 'urbanprofiler.cloudapp.net',
                 ]

CACHES = {
        'default': {
            'TIMEOUT': None, # One dayDo not expire cache pages. Import script must clear cache after system update.
            # File
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/files/webapps/urbanprofiler/site/urbanprofiler_cache',    
                                }
            }
# 'django.middleware.cache.UpdateCacheMiddleware', #Cache, must be first of list
# 'django.middleware.cache.FetchFromCacheMiddleware', #Cache, must be last of list # Comment to disable cache
MIDDLEWARE_CLASSES = ('django.middleware.cache.UpdateCacheMiddleware',) + MIDDLEWARE_CLASSES + ('django.middleware.cache.FetchFromCacheMiddleware',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'urbanprofiler',
        'HOST': 'localhost',
        'USER': 'urban_profiler',
        'PASSWORD': 'urban_profiler_123',
        'CONN_MAX_AGE': 60,
    }
}



############## Collect and Serve static files  ##############
#from fabric.api import run
#from fabric.contrib import project

## Where the static files get collected locally. Your STATIC_ROOT setting.
#env.local_static_root = '/tmp/static'

## Where the static files should go remotely
#env.remote_static_root = '/files/webapps/urbanprofiler/site/static/'

## Hosts to deploy onto
#env.hosts = ['urbanprofiler.clouadpp.net']

## Where your project code lives on the server
#env.project_root = '/files/webapps/urbanprofiler/auto-etl/data-finder-site'

#@roles('static')
#def deploy_static():
#    local('./manage.py collectstatic')
#    project.rsync_project(
#        remote_dir = env.remote_static_root,
#        local_dir = env.local_static_root,
#        delete = True
#    )

