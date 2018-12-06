# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$Jun 16, 2014 3:46:04 PM$"

import urllib
import json
# import logging
from urban_profiler import ApplicationOptions as App
from time import sleep, strftime
import datetime
from urban_profiler.utils import TextUtils as TextUtils
from urban_profiler.ApplicationConstants import MetadataConstants

NYC_OPENDATA_URL_BASE = 'https://nycopendata.socrata.com'
APP_TOKEN_PARAM = '?$$app_token=KGFvl2Sl8wTtXZvb9Ib8PNcWD'
JSON_EXTENSION = '.json'

PREFIX_NEW_COLUMN = '_@_'

def is_primary(metadata):
    if metadata is None or metadata[MetadataConstants.STATUS] != MetadataConstants.STATUS_SUCCESS: 
        return None
    
#    
    if MetadataConstants.PREFIX + 'Author' not in metadata.keys() or 'Socrata Owner' not in metadata.keys():
        return False
    if metadata[MetadataConstants.PREFIX + 'Author'] == metadata['Socrata Owner']:
        return True
    else:
        return 'Socrata View From' in metadata and metadata[MetadataConstants.PREFIX + 'View From'] is None 


def prepare_location_columns(database, metadata_types):
    
    for col in database.columns:
#        print 'Checking:' + col + ' -type:' + metadata_types[col]

        col_is_string = database[col].dtype == object
        if col_is_string and col in metadata_types.keys() and metadata_types[col].lower() == 'location':
            #is it complex ?
            if True in database[col].astype(str).apply(lambda x: '<br />' in x or '\n' in x).value_counts():
                App.debug('Separating location column: ', col)
                #split in multiple columns

                new_col = col + PREFIX_NEW_COLUMN + 'gps'
                database[new_col] = database[col].apply(lambda x: extract_gps_from_composite_location(x))

    #            new_col = col + PREFIX_NEW_COLUMN + 'latitude'
    #            database[new_col] = database[col].apply(lambda x: x.split('\n')[-1][1:-1].split(',')[0].strip())
    #            new_col = col + PREFIX_NEW_COLUMN + 'longitude'
    #            database[new_col] = database[col].apply(lambda x: x.split('\n')[-1][1:-1].split(',')[1].strip())


def extract_gps_from_composite_location(x):
    if type(x) is str and '\n' in x:
        return x.split('\n')[-1].strip()
    else: 
        return x


def key_as_str(dictionary, key):
    if key in dictionary.keys():
        return TextUtils.reencode_text_if_not_ascii(dictionary[key])
    else:
        return None


def metadata_of(database_id, first=True, portal_url=NYC_OPENDATA_URL_BASE):
    App.debug(' SocrataUtils.metadata_of({0})'.format(database_id))
    
    url = portal_url + '/views/' + database_id + JSON_EXTENSION + APP_TOKEN_PARAM
    # App.debug('url: ', url)
    metadata = {'source':'Socrata'}
    # try:
    if True:
        App.debug('Url to get metadata from: ' + url)
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        
        if 'id' in data and data['id'] == database_id:
            App.debug('    -> Success retrieving metadata!')
            App.debug('Retrieved metadata Keys:\n - ' + '\n - '.join(data.keys() ))
            App.debug('Retrieved metadata:\n' + json.dumps(data, indent=4, sort_keys=True))
            App.debug('==========================================')
            
            if 'rowIdentifierColumnId' in data:
                id_column_id = data['rowIdentifierColumnId']
                for col in data['columns']:
                    if col['id'] == id_column_id: 
                        metadata[MetadataConstants.ID_COLUMN] = col['name']
            else:
                metadata[MetadataConstants.ID_COLUMN] = None
                

            metadata[MetadataConstants.METADATA_SOURCE_URL] = key_as_str(data, url)
            metadata[MetadataConstants.METADATA_SOURCE_NAME] = key_as_str(data, 'Socrata Portal ' + portal_url)
                
            metadata[MetadataConstants.NAME] = key_as_str(data, 'name')
            metadata[MetadataConstants.PREFIX + 'Description'] = key_as_str(data, 'description')
            metadata[MetadataConstants.DISPLAY_TYPE_KEY] = key_as_str(data, 'displayType')
            metadata[MetadataConstants.PREFIX + 'Category'] = key_as_str(data, 'category')
            metadata[MetadataConstants.PREFIX + 'Owner'] = key_as_str(data['owner'], 'displayName')
            metadata[MetadataConstants.PREFIX + 'Download Count'] = key_as_str(data, 'downloadCount')
            metadata[MetadataConstants.PREFIX + 'View Count'] = key_as_str(data, 'viewCount')
            metadata[MetadataConstants.PREFIX + 'Comments'] = key_as_str(data, 'numberOfComments')
            metadata[MetadataConstants.PREFIX + 'Author'] = key_as_str(data['tableAuthor'], 'displayName')
    	    metadata[MetadataConstants.PREFIX + 'Id'] = key_as_str(data, 'id')
    	    metadata[MetadataConstants.PREFIX + 'Attribution'] = key_as_str(data, 'attribution')
            metadata[MetadataConstants.PREFIX + 'View Type'] = key_as_str(data, 'viewType')
            metadata[MetadataConstants.PREFIX + 'Display Type'] = key_as_str(data, 'displayType')
            metadata[MetadataConstants.PREFIX + 'Number of Coments'] = key_as_str(data, 'numberOfComments')
            ##> Discover if this dataset is a view
            if 'modifyingViewUid' not in data: metadata[MetadataConstants.PREFIX + 'View From'] = None
            else: metadata[MetadataConstants.PREFIX + 'View From'] = key_as_str(data,'modifyingViewUid')
            
            timestamp = int(data['createdAt'].__str__())
            metadata[MetadataConstants.PREFIX + 'Created At'] = datetime.datetime.fromtimestamp(timestamp).__str__()
            timestamp = int(data['viewLastModified'].__str__())
            metadata[MetadataConstants.PREFIX + 'Last Modified'] = datetime.datetime.fromtimestamp(timestamp).__str__()
            timestamp = int(data['publicationDate'].__str__())
            metadata[MetadataConstants.PREFIX + 'Publication Date'] = datetime.datetime.fromtimestamp(timestamp).__str__()
            metadata['Tags'] = key_as_str(data, 'tags')
            if metadata['Tags'] == 'None': metadata['Tags'] = None
            
            if 'metadata' in data and 'custom_fields' in data['metadata']:
                custom_fields = data['metadata']['custom_fields']
                if 'Update' in custom_fields and 'Update Frequency' in custom_fields['Update']: 
                    metadata[MetadataConstants.PREFIX + 'Update Frequency'] = custom_fields['Update']['Update Frequency'].__str__()
                if 'Dataset Information' in custom_fields and 'Agency' in custom_fields['Dataset Information']: 
                    metadata[MetadataConstants.PREFIX + 'Agency'] = custom_fields['Dataset Information']['Agency'].__str__()

            types = {}
            columns = data['columns']
            for col in columns:
                col_name = col['name'].strip(' ').encode('ascii','ignore')
                col_type = col['dataTypeName']
                types[col_name] = col_type
            metadata[MetadataConstants.PREFIX + 'Types'] = types

            metadata[MetadataConstants.STATUS] = MetadataConstants.STATUS_SUCCESS
        else:
            if 'Cannot find view with id' in data['message']:
                metadata[MetadataConstants.STATUS] = MetadataConstants.STATUS_ERROR_VIEW_NOT_FOUND 
            else:
                metadata[MetadataConstants.STATUS] = 'Error'
            metadata['message'] = data['message']
    # except e:
    #     raise e
    #      #This means that it is not from socrata
    #      # Or that some other error occurred
    #      #just return None
    #     if first: 
    #         App.debug('Waiting to try again')
    #         sleep(0.5)
    #         return metadata_of(database_id, first=False)
    #     metadata[MetadataConstants.STATUS] = 'Error Exception'
    #     metadata['message'] = 'Error acessing a Socrata Portal with url: {0}'.format(url)
    
    if metadata[MetadataConstants.STATUS] is not MetadataConstants.STATUS_SUCCESS: 
        # logging.warn(metadata[STATUS])
        App.debug('WARNING: ', metadata[MetadataConstants.STATUS])
    
    #before return, turn the Unicodes to normal str
    for k in metadata.keys():
        TextUtils.reencode_text_if_not_ascii(metadata[k])
#         if type(metadata[k]) is unicode: 
# #            print '    Unicode info found on key: ' , k, '=', metadata[k] 
#             metadata[k] = metadata[k].encode('ascii','ignore')

    ##> If there was an error, show url so user can check
    if metadata[MetadataConstants.STATUS] == MetadataConstants.STATUS_ERROR_VIEW_NOT_FOUND: 
        App.info('    Metadata not found on Socrata with url: ' + url)
    
    ##> Show dataset retrieved name to indicate success
    if metadata[MetadataConstants.STATUS] == MetadataConstants.STATUS_SUCCESS: 
        App.info('    OK. Dataset Retrieved Name: ' + metadata[ MetadataConstants.NAME ] )

    App.debug('Retrieved Metadata: \n' + json.dumps(metadata, ensure_ascii=False, indent=4, sort_keys=True) )
    return metadata

def dataset_download_url(id, base_url, dataset_url = None):
    # RESOURCE_PATH = '/resource/'
    RESOURCE_PATH = '/-/-/'
    return baseurl.rstrip('/') + RESOURCE_PATH + id + '.JSON' + APP_TOKEN_PARAM