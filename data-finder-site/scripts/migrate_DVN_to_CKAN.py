########################################### To Run ############################################
# python manage.py runscript migrate_DVN_to_CKAN --script-args=ckan_key=XXX dvn_metadata_file=YYY
# python migrate_DVN_to_CKAN.py ckan_key=XXX dvn_metadata_file=YYY
############################### ############################### ###############################

import sys, os

sys.path.append(os.getcwd().replace('data-finder-site', '') + 'src')

import pandas, numpy
from integration.connectors import CkanConnector

## CKAN
PORTAL_URL = 'http://catalog.cusp.nyu.edu'  # CKAN @ workstation`s VM

ERROR_MESSAGE_ARGS = 'It must receive 2 args: ckan_key=XXX and dvn_metadata_file=YYY'
NOT_EXTRA_METADATA = set(['Title', 'Authors', 'Description', 'Keywords', 'GlobalID', 'Data Access Place'])


def dataframe_to_ckan_dataset_dict(dataset_df):
    dataset_df = dataset_df.dropna()
    ds = {}
    columns = dataset_df.keys()
    print 'Dataset Source\n', dataset_df
    # ### ID
    # ds['name'] = CkanConnector.prepare_name_from_text(dataset_df['GlobalID'].replace(':', '-').replace('/', '-'))
    ds['name'] = CkanConnector.prepare_name_from_text(dataset_df['GlobalID'])

    # ## Basic
    ds['title'] = dataset_df['Title']
    if 'NYC OpenData: ' in ds['title']: ds['title'] = ds['title'].lstrip('NYC OpenData: ')
    if 'Authors' in columns: ds['author'] = dataset_df['Authors']
    if 'Description' in columns: ds['notes'] = dataset_df['Description']
    ds['license_title'] = 'Other (Not Open)'
    ds['owner_org'] = 'cusp'
    ds['version'] = dataset_df['Data Citation'].split('[Distributor]')[1].split(' ')[0][1:]

    ds['tags'] = []
    if 'Keywords' in columns and dataset_df['Keywords'] is not numpy.NaN:
        for keyword in dataset_df['Keywords'].split(';'):
            tag = CkanConnector.prepare_tag_from_text(keyword)
            ds['tags'] += [{'display_name': tag, 'name': tag}]

    # ## If from NYC Open Data, Use NYCOpenData id and other Stuff
    if 'Other ID' in columns and dataset_df['Other ID'] is not numpy.NaN and 'NYC OpenData' in dataset_df['Other ID']:
        ds['name'] = CkanConnector.prepare_name_from_text(dataset_df['Other ID'].lstrip('NYC OpenData: '))
        ds['license_title'] = 'Other (Open)'
        ds['source'] = 'https://nycopendata.socrata.com/-/-/' + ds['name']
    # ds['maintainer'] = 'nyc-opendata'
    # ds['organization'] = dataset_df['NYC OpenData']

    # ## Add the rest as Extras
    ds['extras'] = []
    for column in columns:
        key = column
        value = dataset_df[column]
        if column == 'Contact' and 'Rosemary Ashton' in value: continue
        if column == 'Contact' and 'Data Steward' in value:
            key = 'Data Steward'
            value = value.lstrip('Data Steward: ')

        if column not in NOT_EXTRA_METADATA:
            ds['extras'] += [{'key': key, 'value': value}]

    # # Data Fields from Description as Extra
    if 'notes' in ds and 'Data Fields:' in ds['notes']:
        # Remove from Description
        ds['notes'], data_fields = ds['notes'].split('Data Fields:')
        # and add to extra
        ds['extras'] += [{'key': 'Data Fields', 'value': data_fields.strip('\n')}]

    ds['extras'] += [{'key': 'DOI', 'value': ds['name']}]

    # ## Add spatial to show on map - spatial plugin
    if 'Geographic Bounding' in columns:
        import re
        values = re.compile("\d\ ").split(dataset_df['Geographic Bounding'])
        long_min = lat_min = long_max = lat_max = None
        for v in values:
            if 'West Bounding Longitude' in v: long_min = v.lstrip('West Bounding Longitude: ')
            if 'East Bounding Longitude' in v: long_max = v.lstrip('East Bounding Longitude: ')
            if 'North Bounding Latitude' in v: lat_max = v.lstrip('North Bounding Latitude: ')
            if 'South Bounding Latitude' in v: lat_min = v.lstrip('South Bounding Latitude: ')
        if long_min and lat_min and long_max and lat_max:
            polygon = '[[[{0},{1}], [{2},{1}], [{2},{3}], [{0}, {3}], [{0}, {1}]]]'.format(long_min, lat_min, long_max,
                                                                                           lat_max)
            spatial = '{"type":"Polygon", "coordinates":' + polygon + '}'
            ds['extras'] += [{'key': 'spatial', 'value': spatial}]

    return ds


def run(*args):
    print 'ARGS=', args

    if len(args) != 2:
        raise Exception(ERROR_MESSAGE_ARGS)

    ckan_key = None
    dvn_metadata_file = None
    for arg in args:
        key, value = arg.split('=')
        if key == 'ckan_key':
            ckan_key = value
        elif key == 'dvn_metadata_file':
            dvn_metadata_file = value

    if ckan_key is None or dvn_metadata_file is None: raise Exception(ERROR_MESSAGE_ARGS)

    print '----------------------------------'
    print 'PORTAL_URL=', PORTAL_URL
    print 'ckan_key=', ckan_key
    print 'dvn_metadata_file=', dvn_metadata_file
    print '----------------------------------'

    print 'Sync to Portal:', PORTAL_URL

    connector = CkanConnector(site_url=PORTAL_URL, api_key=ckan_key)

    org_list = connector.get_organization_list_for_current_user()
    print '\n<> Organizations in which the user can create datasets:'
    for org in org_list:
        print '    -', org['display_name']

    print '\n<> Syncing datasets from DVN metadata file:'

    datasets = pandas.read_csv(dvn_metadata_file)
    datasets = datasets[pandas.notnull(datasets['GlobalID'])]
    # print "datasets['Access State']=", datasets['Access State'].unique()
    datasets = datasets[datasets['Access State'] == 'Accessible']
    print 'Datasets to import:', len(datasets)
    # print '   Columns:', datasets.columns

    count = 0
    for row_number, row in datasets.iterrows():
        count += 1
        # if row['Study Global ID'] != 'hdl:CUSP/10284': continue
        print '\n\n'
        # if count < 146: continue
        pd_dataset = row
        dataset = dataframe_to_ckan_dataset_dict(pd_dataset)
        # print dataset

        status = connector.create_or_update_dataset(dataset, dataset_is_prepared=True)
        print '\========> ({1}/{2}) {0} [{3}]'.format(dataset['name'], count, len(datasets), status)

    # break
    print 'Sync done!'
