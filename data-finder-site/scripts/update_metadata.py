# This is a standalone file to work with ckan

# ########################################## To Run ############################################
# python manage.py runscript update_metadata --script-args='ckan_key=XXX username=YYY password=ZZZ'
# ############################## ############################### ###############################

import sys
import os
sys.path.append(os.getcwd().replace('data-finder-site', '') + 'src')
from integration.connectors import CkanConnector


## CKAN
PORTAL_URL = 'http://catalog.cusp.nyu.edu'  # CKAN
ckan_key = ''  # urban_profiler
ERROR_MESSAGE_ARGS = 'It must receive the args: ckan_key=XXX username=YYY password=ZZZ'


def run(*args):
    print 'ARGS=', args

    ckan_key = None
    cusp_username = None
    cusp_password = None
    for arg in args:
        key, value = arg.split('=')
        if key == 'ckan_key': ckan_key = value
        if key == 'username': cusp_username = value
        if key == 'password': cusp_password = value

    if None in [ckan_key, cusp_username, cusp_password]: raise Exception(ERROR_MESSAGE_ARGS)

    print '----------------------------------'
    print 'ckan_key=', ckan_key
    print 'CUSP Username=', cusp_username
    print '----------------------------------'

    print 'CKAN Portal:', PORTAL_URL

    ckan = CkanConnector(site_url=PORTAL_URL, api_key=ckan_key, username=cusp_username, password=cusp_password)

    print '\n<> Organizations in which the user can manage datasets:'
    org_list = ckan.get_organization_list_for_current_user()
    for org in org_list:
        print '    -', org['display_name']

    print '\n<> Datasets on CKAN Portal:'
    count = 0;
    on_portal = ckan.get_dataset_list()
    for ds_name in on_portal:
        count += 1
        print ' ({1}/{2}) {0}'.format(ds_name, count, len(on_portal))
        # if ds_name != 'nypd-motor-vehicle-collisions': continue
        ds = ckan.get_dataset_details(ds_name)
        print '            > ', ds.name, '({})'.format(ds.urban_profiler_status)

    print 'Sync done!'
