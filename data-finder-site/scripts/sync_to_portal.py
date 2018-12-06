########################################### To Run ############################################
# python manage.py runscript sync_to_portal --script-args=ckan_key=XXX
############################### ############################### ###############################

import sys, os

sys.path.append(os.getcwd().replace('data-finder-site', '') + 'src')

from finder.models import Database
from integration.connectors import CkanConnector, DkanConnector

## CKAN
PORTAL_URL = 'http://catalog.cusp.nyu.edu'  # CKAN
ckan_key = ''  # urban_profiler
ERROR_MESSAGE_ARGS = 'It must receive the args: ckan_key=XXX'


def run(*args):
    print 'ARGS=', args

    ckan_key = None
    skip = 0
    for arg in args:
        print 'aaaaaaaaaaa', arg
        key, value = arg.split('=')
        if key == 'ckan_key':
            ckan_key = value
        elif key == 'skip':
            skip = int(value)

    if ckan_key is None: raise Exception(ERROR_MESSAGE_ARGS)

    print '----------------------------------'
    print 'skip=', skip
    print 'ckan_key=', ckan_key
    print '----------------------------------'

    print 'Sync to Portal:', PORTAL_URL

    connector = CkanConnector(site_url=PORTAL_URL, api_key=ckan_key)

    org_list = connector.get_organization_list_for_current_user()
    print '\n<> Organizations in which the user can create datasets:'
    for org in org_list:
        print '    -', org['display_name']

    print '\n<> Datasets on Portal:'
    dataset_ids_on_portal = []
    count = 0;
    on_portal = connector.get_dataset_list()
    for ds_name in on_portal:
        count += 1
        if count <= skip: continue
        print ' ({1}/{2}) {0}'.format(ds_name, count, len(on_portal))
        # if ds_name != 'nypd-motor-vehicle-collisions': continue
        ds = connector.get_dataset_details(ds_name)
        dataset_ids_on_portal += ds.database_id
        print '            > ', ds.name, '({})'.format(ds.urban_profiler_status)

    print '\n<> Syncing datasets from Urban Profiler to Portal:'
    datasets = Database.objects.filter(owner__isnull=False)
    # datasets = Database.objects.filter(owner='NYC OpenData')
    count = 0;
    for dataset in datasets:
        if dataset.database_id != 'h9gi-nx95': continue
        count += 1
        print ' ({1}/{2}) {0}'.format(dataset, count, len(datasets))
        status = connector.create_or_update_dataset(dataset)
        print '             [{}]'.format(status)

    print 'Sync done!'
