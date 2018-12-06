# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

# Test multiple databases
# --stop_on_error --verbose  --to_folder=/tmp/profilers --database_refs=../urban_profiler-test/

# Test multiple databases
# --stop_on_error --verbose  --to_folder=/tmp/profilers --database_refs=/home/danielcastellani/Documents/databases/open-data-nyc/open_data_test_list.csv

# Test One database - skip
# --stop_on_error --verbose  --to_folder=/tmp/profilers --file=/home/danielcastellani/Documents/databases/open-data-nyc/2bmn-jq9v

# Test One database - no skip
# --stop_on_error --verbose  --to_folder=/tmp/profilers --file=/home/danielcastellani/Documents/databases/open-data-nyc/NYPD_Motor_Vehicle_Collisions.csv

# Profiler one database with charts
# --stop_on_error --verbose  --to_folder=/tmp/profilers --plot --file=/home/danielcastellani/Documents/databases/open-data-nyc/NYPD_Motor_Vehicle_Collisions.csv

# Profile Fast database list
# --verbose  --to_folder=/tmp/profilers --database_refs=/home/danielcastellani/Documents/databases/open-data-nyc/open_data_test_list_fast.csv

# Profile from metadata (example with SOM datasets)
# python urban_profiler/Main.py --metadata_file=/home/danielcastellani/Documents/databases/SOM/som_metadata.csv --to_folder=/home/danielcastellani/Documents/databases/SOM/ --output_name=SOM_02-05-16 --threads=10 --sources_in_metadata --stop_on_error --verbose

# To make it run on terminal with the package name this is required.
# TODO: check if there is a config that allow to remove this.
import os, sys;
# print('Python %s on %s' % (sys.version, sys.platform))
# print 'sys.path=', sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import pandas
from urban_profiler import ApplicationOptions
from urban_profiler import ApplicationConstants as Constants
from urban_profiler.profiler import Profiler, Indexer
from urban_profiler.utils import PandasUtils
from urban_profiler.utils import ProfilerUtils
from urban_profiler.utils import TimeUtils
from urban_profiler.utils import CLI
from urban_profiler.utils import CuspDW
from multiprocessing import Pool
import os, traceback
from urban_profiler.utils import TerminalColors as tc

__author__ = "danielcastellani"
__date__ = "$May 12, 2014 3:32:21 PM$"

# CONSTANTS
DEMO_FILE = '../NYPD_Motor_Vehicle_Collisions_SAMPLE.csv'
file_name = DEMO_FILE
# Boolean opts
b_opts = {'verbose': False,
          'show_details': False,
          'save_details': False,
          'show_all_info': False,
          'stop_on_error': False,
          'plot': False,
          'silent': False,
          'cusp_dw': False,
          'sources_in_metadata': False,
          'debug': False,
          'part': False,
          'skip_views': False,
          'ignore_index': False,
          'ignore_metadata': False,
          }
# Numeric opts
v_opts = {
    'output_name': None,
    'skip_rows': None,
    'nrows': None,
    'file_refs': None,
    'file': None,
    'to_folder': None,
    'db_ids_file': None,
    'threads': 20,
    'metadata_file': None,
    'types_file': None, # True (the provided one will be used) or path to file
}

opts = None


def process_args():
    options = CLI.process_args(v_opts, b_opts)

    if options['file'] is None:
        options['file'] = DEMO_FILE

    if options['to_folder'] is not None:

        if not options['to_folder'].endswith('/'):
            options['to_folder'] += '/'

    if options['verbose']:
        options['show_details'] = True
        options['show_all_info'] = True
    print 'Considered options:'
    for opt in options:
        print '    - ', opt, '= ', options[opt]
    print '\n\n'

    options['threads'] = int(options['threads'])
    if options['file'] is not None and options['file_refs'] is None and options['db_ids_file'] is None and \
            not options['sources_in_metadata']:
        options['threads'] = 1

    return options


profilers = []
total_databases = 0


def add_profiler(profiler):
    profilers.append(profiler)
    actual = len(profilers)
    msg = ' ________________________________________________________________________ \n'
    msg += '/\n'
    msg += '| Profiled: {0}/{1} ({2:.2f}%) - {3}\n'.format(actual, total_databases, actual * 100.0 / total_databases,
                                                           TimeUtils.current_time_formated())
    msg += '\\________________________________________________________________________\n'
    tc.colored(tc.OKBLUE)
    print msg
    tc.end_colors()


def has_error_on(summaries):
    for s in summaries[Profiler.Profiler.STATUS]:
        if s != Profiler.Profiler.STATUS_SUCCESS: return True
    return False


def process_profiles():
    try:
        global summaries
        global all_gps_rows
        global geo_index_by_dataset
        global all_gps_rows_by_database
        global all_zip_rows
        global gps_db_count
        global zip_db_count
        global profiled_database_types
        profiled_database_types = None
        global profiled_column_metadata
        profiled_column_metadata = None
        summaries = pandas.DataFrame()
        # Count of rows by ZIP and GPS
        all_gps_rows = pandas.DataFrame()
        all_zip_rows = pandas.DataFrame()
        geo_index_by_dataset = pandas.DataFrame()
        all_gps_rows_by_database = pandas.DataFrame()
        # Count of databases that have ZIP and GPS
        gps_db_count = pandas.DataFrame()
        zip_db_count = pandas.DataFrame()

        i = 0;
        for profiler in profilers:
            i += 1
            summaries = pandas.concat([summaries[:], profiler.last_sumary])

            if profiler.last_sumary['ETL-Profiler Status'][0] == 'OK':
                print 'Counting zip and gps data: ', i, '/', len(profilers)
                print '    by Rows'
                all_zip_rows = PandasUtils.merge_series_summing_values(all_zip_rows, profiler.last_zip_rows)
                all_gps_rows = PandasUtils.merge_series_summing_values(all_gps_rows, profiler.last_gps_rows)

                print '    rows by Databases'
                all_gps_rows_by_database = PandasUtils.merge_by_database(all_gps_rows_by_database,
                                                                         profiler.last_gps_rows,
                                                                         profiler.last_sumary.ix[0].Name)
                if not opts['ignore_index']:
                    geo_index_by_dataset = geo_index_by_dataset.append(profiler.last_geo_index, ignore_index=True)

                print '    by Databases'
                # To consider that this database counts only by one, even if it appears more
                temp = pandas.DataFrame(profiler.last_zip_rows, columns=['count']);
                temp['count'] = 1;
                temp = temp['count']
                zip_db_count = PandasUtils.merge_series_summing_values(zip_db_count, temp)

                temp = pandas.DataFrame(profiler.last_gps_rows, columns=['count']);
                temp['count'] = 1;
                temp = temp['count']
                gps_db_count = PandasUtils.merge_series_summing_values(gps_db_count, temp)

                if profiled_database_types is None:
                    profiled_database_types = profiler.types_summary.copy()
                else:
                    profiled_database_types = profiled_database_types.append(profiler.types_summary, ignore_index=True)

                if profiled_column_metadata is None:
                    profiled_column_metadata = profiler.column_metadata.copy()
                else:
                    profiled_column_metadata = profiled_column_metadata.append(profiler.column_metadata,
                                                                               ignore_index=True)
    except:
        if opts['stop_on_error']:
            raise
        ApplicationOptions.error(Exception('Error processing profilers'))

    if 'stop_on_error' in opts and opts['stop_on_error'] and has_error_on(summaries):
        ApplicationOptions.error(Exception('Error on summaries'))


def show_summaries():
    if len(summaries) == 0: raise Exception('No summary to show')

    try:
        print '\n==================='
        print 'ETL-Profiler Summary'
        print '==================='
        print summaries[['ETL-Profiler Status', 'Columns', 'Rows', 'Values Missing Percent',
                         'ETL-Profiler Processing Time (sec)']].to_string()
        print '==================='
    except:
        if opts['stop_on_error']: raise
        print 'Error showing summaries'


def save_files():
    if opts['file_refs'] or opts['db_ids_file'] or opts['to_folder']:
        print 'Saving Summaries file'
        current_time = TimeUtils.current_time_formated().replace(' ', '_').replace(':', '-').replace('/', '-')
        summaries_file = '_etl-profiler-summary-' + current_time
        if opts['output_name']:
            summaries_file = '_etl-profiler-summary-' + opts['output_name'].replace(' ', '_')

        if opts['to_folder'] is not None: summaries_file = opts['to_folder'] + summaries_file

        if profiled_database_types is not None:
            print 'Saving Types Summaries file (Columns)'
            filename = summaries_file + '_columns.csv'
            profiled_database_types.to_csv(filename)
            print 'Saved: ' + filename

        if geo_index_by_dataset is not None and len(geo_index_by_dataset) > 0:
            print 'Saving INDEX rows by database (GEO-TEMP Index)'
            filename = summaries_file + Constants.OUTPUT_FILE_INDEX_SUFFIX
            # print  all_gps_rows_by_database
            geo_index_by_dataset.to_csv(filename, index=False, columns=Indexer.INDEX_COLUMNS_ORDER_IN_CSV)
            print 'Saved: ' + filename

        if profiled_column_metadata is not None:
            print 'Saving Column Metadata file'
            filename = summaries_file + '_columns_metadata.csv'
            profiled_column_metadata.to_csv(filename)
            print 'Saved: ' + filename

        savable_columns = ProfilerUtils.columns_to_save_in_csv(summaries)
        filename = summaries_file + '.csv'
        summaries.to_csv(filename, index_label='Database', cols=savable_columns)
        print 'Saved: ' + filename

    else:
        print 'Dont need to save summaries file. Just one database was profiled.'


STOP_RUNNING = False


def profile_as_job(database_file):
    profiler = Profiler.Profiler()

    global STOP_RUNNING
    if STOP_RUNNING: return

    try:
        pid = str(os.getpid())
        print 'Begin: [' + pid + ']: ' + database_file
        profiler.profile(database_file)
        print 'End: [' + pid + ']: ' + database_file

    except KeyboardInterrupt:
        App.error('KeyboardInterrupt with: ' + database_file)
        STOP_RUNNING = ApplicationOptions.OPTIONS['stop_on_error']

    except:
        msg = '[' + pid + '] ERROR in THREAD:\n'
        msg += '[' + pid + '] -----------------------------------------------------------------\n'
        for line in traceback.format_exc().split('\n'):
            msg += '[' + pid + '] ' + line + '\n'
        msg += '[' + pid + '] -----------------------------------------------------------------'
        # # Will print colored here instead of app.error as facilitates reading error output and debuging
        # print tc.RED + msg + tc.ENDC
        ApplicationOptions.error(msg)
        # raise
    finally:
        return profiler


def profile_databases(database_files):
    global total_databases
    total_databases = len(database_files)

    i = 1
    try:
        pool_size = opts['threads']
        pool = Pool(pool_size)
        print 'Thread Pool created with size: ', pool_size
        for file_name in database_files:
            try:
                # ---------------------> Prepare filename
                if opts['db_ids_file']:
                    print '[Main] Getting file_name in DW for id: ', file_name
                    file_name = CuspDW.get_file_for_id(file_name)

                print '{0}/{1}. Profiling: {2}'.format(i, total_databases, file_name)
                i += 1

                # ---------------------> Profile database
                # profiler = Profiler.Profiler()
                #            profiler.profile(file_name)
                #            add_profiler(profiler)
                #            pool.apply_async(profiler.profile, args=(i,), callback= add_profiler )
                pool.apply_async(profile_as_job, args=(file_name,), callback=add_profiler)
            except(KeyboardInterrupt) as e:
                print '============+> KeyboardInterrupt'
                break
            except:
                print 'Some error: \n', traceback.format_exc()

        print 'All profilers created. Waiting for results...'
        pool.close()
        pool.join()
        print 'All profilers done.'
        return

    except (KeyboardInterrupt, SystemExit) as e:
        print '\n=========================================================' * 3
        print '\nKeyboardInterrupt: Execution interrupted. Saving what is already profiled.\n' + str(e)
        print '=========================================================' * 3
    print '\n\n'


def main():
    print "===> ETL - Profiler <==="

    # ---------------------> Initialize batch processing
    begin_time = TimeUtils.current_time_formated()
    global opts
    opts = process_args()

    # print '1>>>>>>>>>>>>>>>>>>>> ', ApplicationOptions.OPTIONS
    ApplicationOptions.OPTIONS = opts
    # print '2>>>>>>>>>>>>>>>>>>>> ', ApplicationOptions.OPTIONS
    verb = ApplicationOptions.get_option('verbose', default=False)
    print '[verbose]=', verb
    # print '3>>>>>>>>>>>>>>>>>>>> ', ApplicationOptions.OPTIONS

    database_files = []

    if opts['sources_in_metadata']:
        print 'Processing metadata csv to get source files.'
        database_files = pandas.read_csv(opts['metadata_file'], header=0, index_col=None)
        if 'source_file' not in database_files.columns:
            message = 'metadata file should have a source_file column when "sources_in_metadata" option is used.'
            ApplicationOptions.error(message)
            raise Exception(message)

        database_files = database_files['source_file'].tolist()

    elif opts['cusp_dw']:
        print 'Generating file list based on CUSP DW folder.'
        database_files = CuspDW.tabular_ids_in_DW()
        opts['db_ids_file'] = True
        print 'Found ', len(database_files), ' ids.'
        filename = CuspDW.OUTPUT_FILE_NAME
        if opts['to_folder'] is not None: filename = opts['to_folder'] + filename
        CuspDW.save_to_id_file(database_files, filename)
        print 'Saved file with updated ids: ', filename # ApplicationOptions # TODO: why is ApplicationOptions here?
        return

    elif opts['file_refs'] is None and opts['db_ids_file'] is None:
        database_files = [opts['file']]

    elif opts['db_ids_file'] is not None:
        print 'Generation file list based on: db_ids_file.'
        for id in open(opts['db_ids_file']).readlines():
            database_files.append(id.strip())

    else:
        print 'Generation file list based on: file_refs'
        lines = open(opts['file_refs']).readlines()

        for file in lines:
            if file.strip() == '' or file.startswith('#'): continue
            database_files.append(file.rstrip())

        print 'Databases to profile: {0}'.format(len(database_files))

    profile_databases(database_files)

    # ---------------------> Process Profile data
    process_profiles()
    show_summaries()

    end_time = TimeUtils.current_time_formated()

    # ---------------------> Save Data
    save_files()

    print '\nBegin: ', begin_time
    print 'End: ', end_time

    print '\n\n==> The End. <=='


def display_name():
    print tc.OKBLUE, tc.BOLD
    print '                                              ____'
    print '                                |     |       |   \\'
    print '                                |     |       |    |'
    print '                                |     |       |___/'
    print '                                |     |       |'
    print '                                \\_____/RBAN   |     ROFILER', tc.ENDC


def show_code_version():
    print tc.OKBLUE
    print '        ______________________'
    print ' ______/     Version  Info    \\'.ljust(133, '_')
    print '/      \\______________________/'.ljust(132), '\\'
    for line in os.popen('git log -1').read().rstrip().split('\n'): print '|', line.ljust(130), '|'
    print '\\'.ljust(133, '_') + '/'
    print tc.ENDC


if __name__ == "__main__":
    display_name()
    show_code_version()
    main()
