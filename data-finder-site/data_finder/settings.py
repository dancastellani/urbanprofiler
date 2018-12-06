PRODUCTION = 'PRODUCTION'
STAGING = 'STAGING'
DEVELOPMENT = 'DEVELOPMENT'

import os
ENV = os.environ.get('URBAN_PROFILER_ENVORINMENT')
# Default ENV
if not ENV: ENV = DEVELOPMENT

print 'Running Urban Profiler on ENV:', ENV


#Update settings to staging env.
if ENV == STAGING: 
    print '   Loading staging config...'
    from settings_staging import *
else:
    #Use default Settings
    from settings_base import *
