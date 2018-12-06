# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 16, 2014 3:12:46 PM$"

import sys
import os
from urban_profiler.utils import SocrataUtils
from urban_profiler import ApplicationOptions as App
from multiprocessing import Pool
import traceback

BASE_PATH = '/projects/open/NYCOpenData/nycopendata/data/'
OUTPUT_FILE_NAME = 'csv_databases_files'

tabular_ids = []
def add_id_to_list(metadata):
 try:
    if metadata[SocrataUtils.STATUS] <> SocrataUtils.STATUS_SUCCESS:
	App.debug('Metadata not found.')
	return

    id = metadata['Socrata Id']
#    App.debug( 'Begin: [' + str(os.getpid()) + ']: ' + id)
    if metadata[SocrataUtils.DISPLAY_TYPE_KEY] == 'table':
           if SocrataUtils.is_primary(metadata) or App.OPTIONS['process-views']:
                   App.debug('    ', id, ': True')
                   tabular_ids.append(id)
           else:
                   App.debug('    ', id, ': True (Skipped - view)')
    else:
           App.debug('    ', id, ': False')
#    App.debug( 'End: [' + str(os.getpid()) + ']: ' + id)
 except:
    print 'Error: ', traceback.format_exc()

def tabular_ids_in_DW(not_primary_too = True):
    MULTI_THREAD = App.OPTIONS['threads'] > 1
    dir = BASE_PATH
    ids = os.listdir(BASE_PATH)
    App.debug('Verifying if ', len(ids), ' ids are from tabular views: (This may take some time)')
    pool = Pool(App.OPTIONS['threads'])
    index = 0
    for id in ids:
	index+=1
	App.debug(index, '/', len(ids), ' Creating job for or processing id: ', id)
	if MULTI_THREAD:
	    pool.apply_async(SocrataUtils.metadata_of, args=(id,), callback= add_id_to_list )
            metadata = SocrataUtils.metadata_of(id)
	else:
            add_id_to_list( SocrataUtils.metadata_of(id)  )

    if MULTI_THREAD:
        pool.close()
        pool.join()

    App.debug('\n\nFound ', len(tabular_ids), ' tabular ids.')
    App.debug(tabular_ids)
    return tabular_ids
        
def save_to_id_file(ids, filename = 'csv_tabular_ids'):
    output = open(filename, 'w')
    for id in ids:
        output.write(id + '\n')
    output.close()

def get_file_for_id(id):
    dir = BASE_PATH + id 
    
    db_files = []
    for folder in os.listdir(dir):
        filename = dir + '/' + folder + '/' + id
	if os.path.isfile(filename):
		db_files.append(filename)
    if len(db_files) < 1: raise Exception('No file found, db deleted. ')
    db_file = db_files[-1]
    #Check if CSV exists
    if ( os.path.isfile(db_file) is False ):
        print '    Not found CSV: ',  db_file
        #Then it is JSON
        db_file = dir + '/' + id + '.json'
        #Check if JSON exists
        if ( os.path.isfile(db_file) is False ):
            print '    Not found JSON: ', db_file 
            # complain but save to file.
            print '===================> ERROR - Not CSV or JSON in folder. Check with ll ', dir
    return db_file

if __name__ == "__main__":
    
#    metadata_file = sys.argv[1]
#    databases = pandas.read_csv(metadata_file)

    
    if len(sys.argv) > 0:
        ids_file = sys.argv[1]

        database_ids = []
        for id in open(ids_file).readlines():
            database_ids.append(id.rstrip())


        output = open(OUTPUT_FILE_NAME, 'w')
        print len(database_ids)
        i=1
        for id in database_ids[:]:
            print str(i) + ' Id: ' + id
            i+=1

            db_file = get_file_for_id(id)
            print '    Newest: ' + db_file
            output.write(db_file + '\n')
    else:
        output = open('csv_tabular_ids', 'w')
        for id in tabular_ids_in_DW():
            output.write(id + '\n')
        
    output.close()

    print 'Generated: ' + OUTPUT_FILE_NAME
