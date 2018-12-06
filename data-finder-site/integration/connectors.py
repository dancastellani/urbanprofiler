import sys, os

sys.path.append(os.getcwd().replace('data-finder-site', '') + 'src')

import re
from finder.models import Database
import locale;
import time;


def current_time_formated():
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())


# ########################################################################################################
# ######################################### --- CKAN --- #################################################
# ########################################################################################################
## https://github.com/ckan/ckanapi
import ckanapi
class CkanConnector:
    INVALID_CHARS_REGEX = re.compile('[^\w\s\-]+')

    #######
    @classmethod
    def prepare_tag_from_text(cls, text):
        return CkanConnector.INVALID_CHARS_REGEX.sub('', text)

    #######
    @classmethod
    def prepare_name_from_text(cls, text):
        return CkanConnector.prepare_tag_from_text(text.lower())

    #######
    def dataset_to_dict(self, dataset, current_dict=None):
        prepared_tags = []
        for tag in eval(dataset.tags):
            prepared_tag = CkanConnector.prepare_tag_from_text(tag)
            # prepared_tag = prepared_tag.encode('ascii','ignore') #Remove non ascii chars
            prepared_tags += [{'display_name': prepared_tag, 'name': prepared_tag}]

        if dataset.owner is None: raise 'Dataset organization can`t be null.'
        org = self.get_or_create_organization(dataset.organization)
        organization_name = org['name']

        as_dict = {
            'name': CkanConnector.prepare_name_from_text(dataset.database_id),
            'author': dataset.author,
            'maintainer': dataset.owner,
            'title': dataset.title(),
            # 'notes': dataset.description,
            'private': False,
            'download_url': dataset.download_url(),
            'tags': prepared_tags,
            'owner_org': organization_name,
            'extras': [
                {'key': 'Category', 'value': dataset.category},
                {'key': 'Cusp Id', 'value': dataset.database_id},
                {'key': 'Update Frequency', 'value': dataset.socrata_update_frequency},
                {'key': 'urban_profiler__status', 'value': 'OK'},
                # Urban Profiler Metadata - Quality
                {'key': 'Urban Profiler: Updated At', 'value': current_time_formated()},
                {'key': 'Urban Profiler: Number of Columns', 'value': dataset.columns_count},
                {'key': 'Urban Profiler: Number of Rows', 'value': dataset.rows},
                {'key': 'Urban Profiler: Missing Data (%)', 'value': dataset.missing_percent()},
                {'key': 'Urban Profiler: Update Frequency', 'value': dataset.socrata_update_frequency},
                {'key': 'Urban Profiler: Source/Agency', 'value': dataset.source_agency},
            ],
            'resources': [
                {'state': 'active',
                 'name': 'Urban Profiler',
                 'description': 'Explore this dataset on Urban Profiler Web',
                 'format': 'App',
                 'url': "http://urbanprofiler.cloudapp.net/dataset/" + dataset.database_id,
                 },
                {'state': 'active',
                 'name': 'Hue',
                 'description': 'Explore this dataset on Hue',
                 'format': 'App',
                 'url': dataset.hue_url(),
                 },
            ]
        }
        if dataset.organization == 'NYC OpenData':
            as_dict['resources'].append(
                {'state': 'active',
                 'name': dataset.database_id + ' CSV',
                 'description': 'CSV from NYC Open Data API',
                 'format': 'CSV',
                 'url': "https://data.cityofnewyork.us/resource/{0}.csv".format(dataset.database_id),
                 }
            )

        if dataset.has_bounding_box():
            polygon = '[[[{0},{1}], [{2},{1}], [{2},{3}], [{0}, {3}], [{0}, {1}]]]'.format(dataset.long_min,
                                                                                           dataset.lat_min,
                                                                                           dataset.long_max,
                                                                                           dataset.lat_max)
            spatial = '{"type":"Polygon", "coordinates":' + polygon + '}'
            as_dict['extras'].append({'key': 'spatial', 'value': spatial})

        return as_dict

    #######
    def merge_lists_on_keys(self, current_list, updated_values):
        merged_as_dict = {}

        # 1. Add current values to merged
        # print '    Current values:'
        for current in current_list:
            # print '    - [{0}] = {1}'.format(current['key'], current['value'])
            merged_as_dict[current['key']] = current

        # 2. Update with new values
        # print '    Updating values:'
        for updated in updated_values:
            # print '    - [{0}] = {1}'.format(updated['key'], updated['value'])
            merged_as_dict[updated['key']] = updated

        # print '    Updated values:'
        # for value in merged_as_dict.values(): print '    - [{0}] = {1}'.format(value['key'], value['value'])

        # Return values from dict
        return merged_as_dict.values()

    #######
    def dict_to_dataset(self, dataset_data):
        dataset = Database()
        dataset.name = dataset_data['title']
        dataset.description = dataset_data['notes']
        dataset.author = dataset_data['author']
        dataset.owner = dataset_data['organization']['title']
        if dataset_data['extras'] is not None:
            extras = {}
            for e in dataset_data['extras']:
                extras[e['key']] = e['value']
            dataset.database_id = self.get_from_dict(extras, 'Cusp Id')
            dataset.socrata_update_frequency = self.get_from_dict(extras, 'Update Frequency')
            dataset.category = self.get_from_dict(extras, 'Category')
            dataset.urban_profiler_status = self.get_from_dict(extras, 'urban_profiler__status')

        if dataset.database_id is None: dataset.database_id = dataset_data['id']
        return dataset

    #######
    def get_from_dict(self, a_dict, key, default=None):
        if key in a_dict:
            return a_dict[key]
        else:
            return default

    #######
    def __init__(self, site_url, api_key, username=None, password=None):
        self.organization_cache = {}
        self.username = username
        self.password = password
        self.api_key = api_key
        self.site_url = site_url.rstrip('/')

        # initiate CkanClient
        self.ckan = ckanapi.RemoteCKAN(self.site_url,
                                       apikey=self.api_key,
                                       user_agent='ckanapiexample/1.0 (+http://example.com/my/website)')

    #######
    def call_action(self, action, params=None):
        kwargs = {'auth':(self.username, self.password)}
        result = self.ckan.call_action(action, params, requests_kwargs=kwargs)
        return result

    #######
    def get_dataset_list(self):
        package_list = self.call_action('package_list')
        return package_list

    #######
    def get_organization_list_for_current_user(self, permission='create_dataset'):
        return self.call_action('organization_list_for_user', {'permission': permission})

    #######
    def get_dataset_details(self, dataset_name, as_dataset=True):
        # Get the details of a package.
        package_entity = self.call_action('package_show', {'id': dataset_name})
        if as_dataset: package_entity = self.dict_to_dataset(package_entity)
        return package_entity

    #######
    def create_dataset(self, dataset, dataset_is_prepared=False):
        if dataset_is_prepared:
            dataset_data = dataset
        else:
            dataset_data = self.dataset_to_dict(dataset)

        package_entity = self.call_action('package_create', dataset_data)
        # print package_entity
        return package_entity

    #######
    def update_dataset(self, dataset, current_dict, dataset_is_prepared=False):
        if dataset_is_prepared:
            dataset_data = dataset
        else:
            dataset_data = self.dataset_to_dict(dataset, current_dict=current_dict)

        # Merge dataset and current_dict to really update dataset
        if current_dict is not None:
            merged_dict = current_dict.copy()
            for key in dataset_data.keys():
                if key == 'extras':
                    # print ' >> UPDATING EXTRAS'
                    merged_dict['extras'] = self.merge_lists_on_keys(current_dict['extras'], dataset_data['extras'])

                else:
                    merged_dict[key] = dataset_data[key]
            dataset_data = merged_dict
        ####

        dataset_data['id'] = dataset_data['name']
        package_entity = self.call_action('package_update', dataset_data)
        return package_entity

    #######
    def create_or_update_dataset(self, dataset, dataset_is_prepared=False):
        try:
            if dataset_is_prepared:
                dataset_name = dataset['name']
            else:
                dataset_name = CkanConnector.INVALID_CHARS_REGEX.sub('', dataset.database_id).lower()

            current_dataset_data = self.get_dataset_details(dataset_name, as_dataset=False)
            self.update_dataset(dataset, current_dataset_data, dataset_is_prepared)
            return 'updated'
        except ckanapi.errors.NotFound:
            self.create_dataset(dataset, dataset_is_prepared)
            return 'created'
        except:
            raise

        #######

    def get_organization_by_name(self, query_name):
        return self.call_action('organization_autocomplete', {'q': query_name})

    #######
    def create_organization(self, name):
        org_data = {
            'name': CkanConnector.INVALID_CHARS_REGEX.sub('', name).replace(' ', '-').lower(),
            'title': name,
            # 'return_id_only': True,
        }
        org_id = self.call_action('organization_create', org_data)

        print ' ---=== Created Organization {} ===---'.format(name)
        return org_id

    #######
    def get_or_create_organization(self, name):
        if name in self.organization_cache.keys():
            return self.organization_cache[name]

        org_list = self.get_organization_by_name(name)
        if len(org_list) == 0:
            org = self.create_organization(name)
        else:
            org = org_list[0]

        self.organization_cache[name] = org
        return org


#########################################################################################################
########################################## --- DKAN --- #################################################
#########################################################################################################
import urllib, json


class DkanConnector:
    INVALID_CHARS_REGEX = re.compile('[^\w\s\-]+')
    ACTION_DATASET_SHOW = 'api/3/action/package_show'
    ACTION_DATASET_LIST = 'api/3/action/package_list'
    ACTION_DATASET_LIST_WITH_RESOURCES = 'api/3/action/current_package_list_with_resources'

    def dataset_to_dict(self, dataset):
        prepared_tags = []
        for tag in eval(dataset.tags):
            prepared_tag = CkanConnector.INVALID_CHARS_REGEX.sub('', tag)
            # prepared_tag = prepared_tag.encode('ascii','ignore') #Remove non ascii chars
            prepared_tags += [{'display_name': prepared_tag, 'name': prepared_tag}]

        if dataset.owner is None: raise 'Dataset organization can`t be null.'
        org = self.get_or_create_organization(dataset.organization)
        organization_name = org['name']

        as_dict = {
            'name': CkanConnector.INVALID_CHARS_REGEX.sub('', dataset.database_id).lower(),
            'author': dataset.author,
            'maintainer': dataset.owner,
            'title': dataset.title(),
            'notes': dataset.description,
            'private': False,
            'download_url': dataset.download_url(),
            'tags': prepared_tags,
            'owner_org': organization_name,
            'extras': [
                {'key': 'Category', 'value': dataset.category},
                {'key': 'Cusp Id', 'value': dataset.database_id},
                {'key': 'Update Frequency', 'value': dataset.socrata_update_frequency},
                {'key': 'urban_profiler_status', 'value': 'OK'},
            ],
        }
        return as_dict

    def dict_to_dataset(self, dataset_data):
        dataset = Database()
        dataset.name = dataset_data['title']
        if 'extras' in dataset_data and dataset_data['extras'] is not None:
            extras = {}
            for e in dataset_data['extras']:
                extras[e['key']] = e['value']
            if 'CUSP Id' in extras: dataset.database_id = extras['CUSP Id']
            if 'Update Frequency' in extras: dataset.socrata_update_frequency = extras['Update Frequency']
            if 'Category' in extras: dataset.category = extras['Category']
            if 'Owner' in extras: dataset.owner = extras['Owner']
            if 'Author' in extras: dataset.author = extras['Author']
            if 'Urban Profiler Status' in extras:
                dataset.urban_profiler_status = extras['Urban Profiler Status']
            else:
                dataset.urban_profiler_status = 'Waiting'

        return dataset

    def __init__(self, site_url, api_key):
        self.organization_cache = {}
        self.api_key = api_key
        self.site_url = site_url.rstrip('/') + '/' + '?q='

    def call_action(self, action, params=None):
        url = self.site_url + action
        if params is not None: url += '&' + params

        # print 'calling action from url:', url
        response = urllib.urlopen(url)
        data = json.loads(response.read())

        if 'error' in data:
            raise 'Error requesting from URL "{0}":"{1}"'.format(url, data['error'])
        return data['result']

    def get_dataset_list(self):
        package_list = self.call_action(DkanConnector.ACTION_DATASET_LIST)
        return package_list

    def get_organization_list_for_current_user(self, permission='create_dataset'):
        return self.call_action('organization_list_for_user', {'permission': permission})

    def get_dataset_details(self, dataset_name, as_dataset=True):
        # Get the details of a package.
        package_entity = self.call_action(DkanConnector.ACTION_DATASET_SHOW, 'id={0}'.format(dataset_name))
        if as_dataset: package_entity = self.dict_to_dataset(package_entity)
        return package_entity

    def create_dataset(self, dataset):
        dataset_data = self.dataset_to_dict(dataset)
        package_entity = self.call_action('package_create', dataset_data)
        # print package_entity
        return package_entity

    def update_dataset(self, dataset):
        dataset_data = self.dataset_to_dict(dataset)
        dataset_data['id'] = dataset_data['name']
        package_entity = self.call_action('package_update', dataset_data)
        return package_entity

    def create_or_update_dataset(self, dataset):
        try:
            dataset_name = CkanConnector.INVALID_CHARS_REGEX.sub('', dataset.database_id).lower()
            self.get_dataset_details(dataset_name, as_dataset=False)
            self.update_dataset(dataset)
            return 'updated'
        except ckanapi.errors.NotFound:
            self.create_dataset(dataset)
            return 'created'
        except:
            raise

    def get_organization_by_name(self, query_name):
        return self.call_action('organization_autocomplete', {'q': query_name})

    def create_organization(self, name):
        org_data = {
            'name': CkanConnector.INVALID_CHARS_REGEX.sub('', name).replace(' ', '-').lower(),
            'title': name,
            # 'return_id_only': True,
        }
        org_id = self.call_action('organization_create', org_data)

        print ' ---=== Created Organization {} ===---'.format(name)
        return org_id

    def get_or_create_organization(self, name):
        if name in self.organization_cache.keys():
            return self.organization_cache[name]

        org_list = self.get_organization_by_name(name)
        if len(org_list) == 0:
            org = self.create_organization(name)
        else:
            org = org_list[0]

        self.organization_cache[name] = org
        return org
