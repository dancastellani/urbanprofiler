#!/usr/bin/env python

# ## imports
import os
import urllib

import numpy
import pandas
import wget

# ## app imports
# from utils import SocrataUtils

# > Constants
TYPE_TABULAR = "<div class='typeBlist'><div class=\"viewTypeCell\">Tabular</div></div>"
# > PARAMS
# Do not use https as it can cause SSL errors with python wget.
# Instead use only HTTP. As it is all open data there is no problem.
APP_TOKEN_PARAM = '?$$app_token=KGFvl2Sl8wTtXZvb9Ib8PNcWD'
BASE_PORTAL_URL = 'https://data.sfgov.org/'
ORGANIZATION = 'SF OpenData'
SOCRATA_CATALOG_ID = 'y8fp-fbf5'

OUTPUT_DIRECTORY = '/Files/dancastellani/Documents/databases/SFopendata/'
# Name the profiler input file to be created by the portal name
PROFILER_INPUT_FILE = OUTPUT_DIRECTORY + BASE_PORTAL_URL.split('://')[1].strip('/') + '_profiler-input.csv'
# extension to download and name the files
DESIRED_EXTENSION = 'csv'

# NYC OpenData and other Socrata Portals
CATALOG_COLUMN_DATASET_NAME = 'Dataset Name'
CATALOG_COLUMN_DATASET_ID = 'Dataset ID'

# SF OpenData
CATALOG_COLUMN_DATASET_NAME = 'Dataset Name'
CATALOG_COLUMN_DATASET_ID = 'Dataset ID'

# CONTROL PARAMS
CHECK_SIZE = False
DOWNLOAD_DATASETS = True
CREATE_URBAN_PROFILER_INPUT = True
DOWNLOAD_ONLY_TABULAR = False
SKIP_DATASETS_WITH_NULL_ID = True


def download_url_of(dataset_id, extension='csv'):
    # ie. https://data.kcmo.org/api/views/5hi7-csas/rows.csv?accessType=DOWNLOAD
    return BASE_PORTAL_URL.rstrip('/') + '/api/views/' + dataset_id + '/rows.csv' + APP_TOKEN_PARAM


def get_id(dataset):
    # works for NYC OpenData and some other socrata portals
    # dataset_id = dataset.Uid
    # works for SF OpenData
    dataset_id = dataset[CATALOG_COLUMN_DATASET_ID]
    return dataset_id


def delete_file_if_exists(PROFILER_INPUT_FILE):
    try:
        os.remove(PROFILER_INPUT_FILE)
    except OSError:
        pass

def main():
    # #> 1. Connect to portal and get list of tabular datasets
    catalog_url = download_url_of(SOCRATA_CATALOG_ID)
    print 'Fetchind datasets from catalog url:', catalog_url
    catalog = pandas.read_csv(catalog_url)
    total = len(catalog)
    print 'All Catalog: ', total

    # #> Filter only tabular
    if DOWNLOAD_ONLY_TABULAR:
        catalog = catalog[catalog.Type == TYPE_TABULAR]
    else:
        print 'Not filtering only Tabular Datasets...'
    if SKIP_DATASETS_WITH_NULL_ID:
        print 'Filtering entries with null ID...'
        catalog = catalog[pandas.notnull(catalog[CATALOG_COLUMN_DATASET_ID])]

    print 'Datasets to process: ', len(catalog), '({}%)'.format(len(catalog) * 100.0 / total)
    print  # output formating
    total = len(catalog)

    # #> 2. Display Datasets information
    total_size = 0
    print 'Calculating file sizes...'
    index = 0
    if CHECK_SIZE:
        for row_id, dataset in catalog.iterrows():
            index += 1
            dataset_id = get_id(dataset)
            # if index < 80: continue
            download_url = download_url_of(dataset_id)
            site = urllib.urlopen(download_url)
            print '    - ({}/{})'.format(index, total), dataset_id, '->', download_url
            lenght = site.info().getheaders("Content-Length")
            # #> protection agains urllib error (don`t know why, but sometmies it does not recorver the size)
            size = 0
            # print '----------->', lenght, ' | Status code:', site.code
            if len(lenght) > 0: size = int(lenght[0])

            print '       = ', sizeof_fmt(size)
            total_size += size
        # if index > 100: break
        print 'Total size required on DISK:', sizeof_fmt(total_size)
    else:
        print 'Required size not verified. \n\n'

    # #> 3. Create Urban Profiler input metadata file
    if CREATE_URBAN_PROFILER_INPUT:
        cols = ['title', 'external_id', 'source', 'socrata_portal_url', 'source_file', 'organization']
        profiler_input = pandas.DataFrame(columns=cols)
        index = 0
        print 'Generating Profiler Input from datasets...'
        for row_id, dataset in catalog.iterrows():
            dataset_id = get_id(dataset)
            index += 1
            print '      - ({}/{})'.format(index, total), dataset_id
            ds_entry = {'title': dataset[CATALOG_COLUMN_DATASET_NAME], 'external_id': dataset_id,
                        'source': 'Socrata', 'socrata_portal_url': BASE_PORTAL_URL,
                        'organization': ORGANIZATION,
                        'source_file': OUTPUT_DIRECTORY + dataset_id + '.' + DESIRED_EXTENSION}
            profiler_input = profiler_input.append(ds_entry, ignore_index=True)
        # save to file
        print 'Saving file:', PROFILER_INPUT_FILE
        delete_file_if_exists(PROFILER_INPUT_FILE)
        profiler_input.to_csv(PROFILER_INPUT_FILE)

    # #> 4. Download all datasets as csv to
    if DOWNLOAD_DATASETS:
        index = 0
        for row_id, dataset in catalog.iterrows():
            index += 1
            dataset_id = get_id(dataset)
            print '\n\n======================================== {}/{} ({:.2f}%)'.format(index, total,
                                                                                        index * 100.0 / total)
            print '{} - {}'.format(dataset_id, dataset[CATALOG_COLUMN_DATASET_NAME])
            download_url = download_url_of(dataset_id, extension=DESIRED_EXTENSION)
            output_file = OUTPUT_DIRECTORY + dataset_id + '.' + DESIRED_EXTENSION
            # #> Remove old file to save new
            if os.path.exists(output_file): os.remove(output_file)
            print '     - Download from:', download_url
            print '     - Download to  :', output_file
            filename = wget.download(download_url, out=output_file)
    else:
        print 'Datasets not downloaded.'

    print 'The End.'


# # Copied from: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


if __name__ == '__main__':
    main()
