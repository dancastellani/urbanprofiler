# """
# WSGI config for data_finder project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
# """

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_finder.settings")

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()


import newrelic.agent
newrelic.agent.initialize()

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_finder.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
application = newrelic.agent.wsgi_application()(application)