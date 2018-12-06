#!/usr/bin/python

#imports
import json
import os, sys, traceback, time, resource, re, logging

import pandas as pd
import numpy as np
from urban_profiler.utils import TimeUtils
from urban_profiler.utils import PandasUtils
from urban_profiler.utils import ProfilerUtils
from urban_profiler.utils import MetadataUtils
from urban_profiler.utils import SocrataUtils
import urban_profiler.ApplicationOptions as App
from urban_profiler.profiler import TypeDetector
from urban_profiler.profiler import Indexer
from urban_profiler.ApplicationConstants import MetadataConstants as MetadataConstants

COLUMN_METADATA = 'Column Metadata'


class Profiler:
    
    MSG_SKIP_VIEW = 'SKIP: Socrata View'
    STATUS = 'ETL-Profiler Status'
    STATUS_SUCCESS = 'OK'
    
    SUMMARY_ZIP_ROWS='Zip Values'
    SUMMARY_GPS_ROWS='GPS Values'
    
    TEXT_INFO_SMALL=['Count', 'Missing', 'Unique Values']
    TEMPORAL_INFO_SMALL=['Count', 'Missing', 'Unique Values']
    TEXT_INFO_CSV=['Count', 'Missing', 'Unique Values']
    NUMERIC_INFO_SMALL=['Count', 'Missing', 'Mean', 'Std']
    GEO_INFO_SMALL=['Count', 'Missing', 'Unique Values', 'Most Frequent', 'Top Frequency']
    SUMARY_COLUMNS=['Name', 
                'Rows',
                'Columns',
                'Columns Numeric',
                'Columns Geo',
                'Columns Temporal',
                'Columns Text',
                'Columns Null',
                'Column Names Numeric',
                'Column Names Geo',
                'Column Names Temporal',
                'Column Names Text',
                'Values',
                'Values Missing',
                'Values Missing Percent',
                'ETL-Profiler Processing Time (sec)',
                'ETL-Profiler Time Begin',
                'ETL-Profiler Time End',
                'ETL-Profiler Input File',
                'ETL-Profiler Input File Size (KB)',
                'ETL-Profiler Total Memory (MB)',
                'ETL-Profiler Status',
                'Numeric Profiler',
                'Geo Profiler',
                'Textual Profiler',
                'GPS-Lat-Min',
                'GPS-Lat-Max',
                'GPS-Long-Min',
                'GPS-Long-Max',
                'GPS Values'
                ]
    # MAX_ROWS = 1000000
    MAX_CHUNK_SIZE = 50000
    MAX_BINS = 10
    MAX_TOP_K = 50

#    Plot configuration
#    pd.options.display.mpl_style = 'default'
    pd.set_option('display.height', 1000)
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    def __init__(self, opts=None):
        self.verbose = App.get_option('verbose', default=False, options=opts)
        self.show_details = App.get_option('show_details', default=False, options=opts) and self.verbose
        self.save_output_files = App.get_option('save_details', default=False, options=opts)
        self.show_all_columns = App.get_option('show_all_info', default=False, options=opts)
        self.silent = App.get_option('silent', default=False, options=opts)
        self.to_folder = App.get_option('to_folder', default=None, options=opts)
        self.stop_on_error = App.get_option('stop_on_error', default=False, options=opts)
        self.plot = App.get_option('plot', default=False, options=opts)
        self.skip_views = App.get_option('skip_views', default=False, options=opts)
        self.metadata_file = App.get_option('metadata_file', default=None, options=opts)
        self.part = App.get_option('part', default=False, options=opts)
        self.ignore_index = App.get_option('ignore_index', default=False, options=opts)
        self.ignore_metadata = App.get_option('ignore_metadata', default=False, options=opts)

        if self.to_folder is None: self.to_folder = ''
        
        self.last_zip_rows = self.last_gps_rows = None
        
        type_of_detectors = TypeDetector.data_detectors()[0]
        if type_of_detectors != 'Dynamic':
            App.warn('Type Detectors Not Loaded Dynamically from File. ({0} Detectors) '.format(type_of_detectors))
        
    def save_dataframe_to_csv(self, dataFrame, file_sufix):
        output_file = self.to_folder + self.db_name + file_sufix + '.csv'
        dataFrame[ProfilerUtils.columns_to_save_in_csv(dataFrame)].to_csv(output_file, index_label='Column')
        if self.verbose: print '    ' + output_file
        
        
    def save_last_sumary_to_json(self):
        dataFrame = self.last_sumary
        #Gambiarra para salvar apenas o primeiro
        dataFrame = dataFrame[ProfilerUtils.columns_to_save_in_csv(dataFrame)].T[dataFrame.T.columns[0]]
        output_file = self.to_folder + self.db_name + '_profiled.json'

        dataFrame.to_json(output_file, orient = 'columns')
        if self.verbose: print '    ' + output_file
        
        profiler_file_name = self.to_folder + self.db_name + '_profiled.profiler'
        ProfilerUtils.write_profiler_file(profiler_file_name, 
                                            self.last_sumary,
                                            self.textual_DataFrame,
                                            self.numeric_DataFrame,
                                            self.geo_DataFrame
                                        )
        if self.verbose: print '    ' + profiler_file_name

        
    def printv(self, text, not_verbose_text=''):
        if not self.silent: 
            if self.verbose:
                if text is not None: print text
            else:
                sys.stdout.write(not_verbose_text)
                sys.stdout.flush()

    def create_error_sumary(self, error_message, file_rows, metadata = None):
        error_summary = pd.DataFrame([
            {'Name': self.db_name,
                'Rows': file_rows, 
                'Columns': None,
                'Columns Numeric': None,
                'Columns Geo': None,
                'Column Names Numeric':None,
                'Column Names Geo':None,
                'Column Names Text':None,
                'Columns Text': None,
                'Values': None,
                'Values Missing': None,
                'Values Missing Percent': None,
                'ETL-Profiler Processing Time (sec)': None,
                'ETL-Profiler Time Begin': None,
                'ETL-Profiler Time End': None,
                'ETL-Profiler Input File': None,
                'ETL-Profiler Input File Size (KB)': None,
                'ETL-Profiler Total Memory (MB)': None,
                Profiler.STATUS: error_message
                
            }], 
            columns = Profiler.SUMARY_COLUMNS,
            index = [self.db_name]
            )
        if metadata is not None:
            for k in metadata.keys():
                error_summary[k] = metadata[k].__str__()
        return error_summary


    def check_if_skip_dataset(self, metadata):
        return self.skip_views and MetadataUtils.is_socrata_view(metadata)


    def profile(self, file_name, skip_rows=0, n_rows=None):
        # print '-----------------> file_name:', file_name
        file_rows = None
        metadata = None
        self.db_name = None
        try:
            metadata, file_rows = ProfilerUtils.init_profiler(file_name, part=self.part, metadata_file=self.metadata_file, ignore_metadata=self.ignore_metadata)
            self.db_name = metadata['db_name']
            # This is (a temporary fix) for any uncatched error that can ocour. TODO: Improve this.
            self.last_sumary = self.create_error_sumary('Something went wrong!', file_rows, metadata=metadata)

            self.printv('File rows: {0:n}'.format(file_rows - 1))

            if file_rows == 0:
                self.last_sumary = self.create_error_sumary('Error: Empty file.', None)
                return

            self.printv('Getting metadata.')
            # metadata = SocrataUtils.metadata_of(self.db_name)

            if self.check_if_skip_dataset(metadata):
                App.warn('Skipping database analisys: Not primary Socrata Database')
                self.last_sumary = self.create_error_sumary(Profiler.MSG_SKIP_VIEW, file_rows, metadata)
            
            else:
                self.printv("Loading file: " + file_name)
                database = PandasUtils.load_database(file_name, skiprows=skip_rows, nrows=n_rows)

                self.do_profile(database, file_name, skip_rows, n_rows, metadata)

        except (KeyboardInterrupt, SystemError) as e:
            ex_type, ex, tb = sys.exc_info()
            error_msg =  '\n'.join(traceback.format_tb(tb))
            self.last_sumary = self.create_error_sumary('Interrupted by Keyboard', file_rows, metadata=metadata)
            # logging.exception(e)
            App.error('Interrupted by Keyboard \n' + error_msg)
            raise
        
        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            error_msg =  '\n'.join(traceback.format_tb(tb))
            App.error(error_msg)
            self.last_sumary = self.create_error_sumary('Error: ' + error_msg, file_rows, metadata=metadata)
            if self.stop_on_error: raise
            
        except:
            self.last_sumary = self.create_error_sumary('Unknown Error: {0}'.format(sys.exc_info()), file_rows, metadata=metadata)
            # logging.exception(sys.exc_info())
            App.error(sys.exc_info())
            if self.stop_on_error: raise

    
    def generate_index(self, database):
        index = Indexer.generate_index(self.db_name, self.types_summary, database)

        # Update last summary
        self.last_geo_index = index
        geo_bounds = Indexer.calculate_geo_bounds(index)
        self.last_sumary['GPS-Lat-Min'] = geo_bounds['lat_min']
        self.last_sumary['GPS-Lat-Max'] = geo_bounds['lat_max']
        self.last_sumary['GPS-Long-Min'] = geo_bounds['long_min']
        self.last_sumary['GPS-Long-Max'] = geo_bounds['long_max']
        self.last_sumary['GPS Values'] = index.lat.dropna().count()
        # print '-------------------------'
        # print '--- lat'
        # print '--- --- min=', self.last_sumary['GPS-Lat-Min'][0]
        # print '--- --- max=', self.last_sumary['GPS-Lat-Max'][0]
        # print '--- lon'
        # print '--- --- min=', self.last_sumary['GPS-Long-Min'][0]
        # print '--- --- max=', self.last_sumary['GPS-Long-Max'][0]
        # print '-------------------------'

        dates = index[['year', 'month', 'day']][index.day != '']
        # print '\n\n\n\n\n\n\n\n\n\n\n\n================================================================================'
        # print 'year description', dates.year.astype(int).describe()
        # print 'month description', dates.month.astype(int).describe()
        # print 'day description', dates.day.astype(int).describe()
        # print '================================================================================\n\n\n\n\n\n\n\n\n\n\n\n'
        if len(dates) > 0:
            dates = dates.year.apply(lambda x: x.zfill(4)) + '/' \
                    + dates.month.apply(lambda x: x.zfill(2)) + '/' \
                    + dates.day.apply(lambda x: x.zfill(2))
            dates = dates.apply(lambda x: TimeUtils.date_from_str_date(x)).dropna()

            date_min = dates.min()
            date_max = dates.max()

            self.last_sumary['Date Min'] = date_min
            self.last_sumary['Date Max'] = date_max


    def add_column_metadata(self, column, group, key, value):
        self.column_metadata = self.column_metadata.append({
                'Database-id': self.db_name,
                'Column-name': column, 
                'Group': group, 
                'Key': key, 
                'Value': value
            }, ignore_index=True)

#
    def do_profile(self, database, file_name, skip_rows, n_rows, metadata):
        printv=self.printv
        self.db_name = metadata['db_name']
        self.last_sumary=None  
        self.column_metadata = pd.DataFrame(columns=['Database-id', 'Column-name', 'Group', 'Key', 'Value'])
        
        readable_time_start = TimeUtils.current_time_formated()
        time_start = time.time()

        total_rows = len(database.index)
        total_missing_values = 0

        text_cols = []
        text_cols_names = []
        num_cols = []
        num_cols_names = []
        geo_cols = []
        geo_cols_names = []
        temp_cols = []
        temp_cols_names = []
        null_cols = []
        null_cols_names = []
        self.gps_cols = []
        self.zip_cols = []
        self.types_summary = pd.DataFrame(columns=['database-id', 'column-name', 'socrata-type', 'profiler-type', 'profiler-most-detected'])

        str_cols_types_percent = ''
        str_cols_types_percent_simple = ''

        printv ('\nMetadata Types (Socrata Only): ')
        metadata_types = {}
        if metadata is not None and MetadataConstants.TYPES in metadata.keys():
            metadata_types = metadata[MetadataConstants.TYPES]
        for col in metadata_types.keys():
            printv ('    ' + col + ': ' + metadata_types[col])
        
        SocrataUtils.prepare_location_columns(database, metadata_types)
        col_names = database.dtypes.keys()
        
        printv('\nProfiling {0} columns.'.format(col_names.size))
        # print 'col_names=', col_names
        for i in range(0, col_names.size):
            # reset col description
            unique = counts = vmin = vmax = std = mean = length_min = length_max = length_std = length_mean = missing = None
            col = database[col_names[i]]
            col_name = col_names[i]

            App.debug('Profiling column: ', col_name)
            App.debug('Pandas DType: ', col.dtype)
            
            if col_name in metadata_types: metadata_type = metadata_types[col_name] 
            else: metadata_type = ''
            App.debug('Metadata type: ', metadata_type)
            
            unique_data = pd.DataFrame()
            temp = col.dropna() 
            temp = temp.unique() # <= gives this error probably is a pandas error: TypeError: unhashable type: 'dict'
            unique_data[col_name] = temp 
            unique_data = unique_data[col_name]

            col_types_percent_detailed = TypeDetector.types_of( unique_data )
            App.debug('[var] col_types_percent_detailed: ', col_types_percent_detailed)
            
            processed_col_name = col_name.replace("'", "`")
            str_cols_types_percent += "'{0}': {1}\n".format(processed_col_name, col_types_percent_detailed)
            
            col_types_percent = TypeDetector.simplify(col_types_percent_detailed)
            printv('{0}: {1}'.format(col_name, col_types_percent))
            str_cols_types_percent_simple += "'{0}': {1}\n".format(processed_col_name, col_types_percent)
            
            data_type = TypeDetector.simple_type_of_considering_all(col_types_percent_detailed, metadata_type, col_name)
            
            most_detected, precision = TypeDetector.most_detected(col_types_percent_detailed)

            valid_col_values = TypeDetector.valid_values_of_type(most_detected, col)
            ########## Geographic  ########## 
            if data_type is TypeDetector.GEO:
                printv("Processing Column {0}: {1} - Geo".format(i+1, col_names[i]), str(i+1))
                # printv('    Processing Count', '.')
                count = col.count()
                missing = total_rows - count
                total_missing_values += missing
                # printv('    Processing Value Counts', '.')
                value_counts = valid_col_values.value_counts()
                top = value_counts.first_valid_index()
                freq = 0
                if top is not None:
                    freq = str(value_counts[top])

                # improve readability if is zip code
                if type(top) is not str and isinstance(top, int):
                    top = '%i' % top

                unique = len(value_counts)
                geo_cols_names.append(col_name)
                geo_cols.append({'Count':count,
                    'Missing':       missing,
                    'Unique Values': unique,
                    'Most Frequent': top,
                    'Top Frequency': freq,
                    'Min': col.min(),
                    'Max': col.max(),
                    'Types Percent': str(col_types_percent_detailed)
                })
                if most_detected == TypeDetector.GEO_GPS: self.gps_cols.append(col_name)
                # Save column metadata
                # Only makes sense to save these numeric descriptors if is a lat, lon
                if most_detected == TypeDetector.GEO_GPS_LATLON:
                    self.add_column_metadata(col_name, 'Type Details', 'min', vmin)
                    self.add_column_metadata(col_name, 'Type Details', 'max', vmax)
                    self.add_column_metadata(col_name, 'Type Details', 'std', std)
                    self.add_column_metadata(col_name, 'Type Details', 'mean', mean)

            ########## Numeric  ##########
            elif data_type is TypeDetector.NUMERIC:
                printv("Processing Column {0}: {1} - Numeric".format(i+1, col_names[i]), str(i+1))
                # printv('    Get valid Numeric gps_data', '.')
                col_data_numeric = TypeDetector.get_numeric_data(col)
                printv('    Processing Count', '.')
                count = col_data_numeric.count()
                missing = total_rows - count
                total_missing_values += missing
                if count > 0:
                    # printv('    Processing Mean', '.')
                    mean = np.mean(col_data_numeric)
                    # printv('    Processing Std', '.')
                    std = np.std(col_data_numeric)
                    # printv('    Processing Min', '.')
                    vmin = np.min(col_data_numeric)
                    # printv('    Processing Max', '.')
                    vmax = np.max(col_data_numeric)
                    # printv('    Processing Unique', '.')
                    unique = col_data_numeric.nunique()
                    value_counts = col_data_numeric.value_counts()
                    
                    top = value_counts.keys()[0]
                    freq = value_counts[top]

                    # Histogram Data, default bins=10
                    num_bins = min([Profiler.MAX_BINS, unique])
                    hist_counts, bins = np.histogram(col_data_numeric, bins=num_bins)
                    hist = pd.Series(hist_counts, index=bins[:-1])
                    hist_json = hist.to_json()
                else:
                    printv('    All NaN values')
                    hist_json = mean = std = vmin = vmax = unique = freq = None
                    
                
                num_cols_names.append(col_name)
                num_cols.append({'Count': count, 
                    'Missing': missing, 
                    'Mean':    mean, 
                    'Std':     std, 
                    'Min':     vmin, 
                    'Max':     vmax,
                    'Unique Values': unique,
                    'Most Frequent': top,
                    'Top Frequency': freq,
                    'Types Percent': str(col_types_percent_detailed),
                    'Histogram Data JSON': hist_json,
                })
                # Save column metadata
                self.add_column_metadata(col_name, 'Type Details', 'min', vmin)
                self.add_column_metadata(col_name, 'Type Details', 'max', vmax)
                self.add_column_metadata(col_name, 'Type Details', 'std', std)
                self.add_column_metadata(col_name, 'Type Details', 'mean', mean)
                self.add_column_metadata(col_name, 'Type Details', 'Histogram Data JSON', hist_json)

            ########## Temporal  ########## 
            elif data_type is TypeDetector.TEMPORAL: # data_type is PandasUtils.Temporal:
                printv("Processing Column {0}: {1} - Temporal".format(i+1, col_names[i]), str(i+1))
                # printv('    Processing Info', '.')
                info = col.astype(str).describe()
                temp_cols_names.append(col_name)
                printv('    Processing Count', '.')
                count = info['count']
                missing = total_rows - count
                total_missing_values += missing
                # printv('    Processing Lenght', '.')
                lenghts=col.str.len()
                len_min=lenghts.min()
                len_max=lenghts.max()
                len_mean=lenghts.mean()
                len_std=lenghts.std()
                top = None
                if 'top' in info.keys(): top = info['top'].__repr__().strip()
                freq = None
                if 'freq' in info.keys(): freq = info['freq']
                # printv('    Processing Min', '.')
                vmin = col.min()
                # printv('    Processing Max', '.')
                vmax = col.max()
                unique = info['unique']
                value_counts = valid_col_values.value_counts()
                temp_cols.append({'Count':count, 
                    'Missing':       missing, 
                    'Unique Values': unique, 
                    'Most Frequent': top, 
                    'Top Frequency': freq,
                    'Min': vmin,
                    'Max': vmax,
#                    'Lenght Min':    '{0:.0f}'.format(len_min),
#                    'Lenght Max':    '{0:.0f}'.format(len_max),
#                    'Lenght Mean':   '{0:.2f}'.format(len_mean),
#                    'Lenght Std':    '{0:.2f}'.format(len_std),
                    'Types Percent': str(col_types_percent)
                })
                # Save column metadata
                self.add_column_metadata(col_name, 'Type Details', 'min', vmin)
                self.add_column_metadata(col_name, 'Type Details', 'max', vmax)
                self.add_column_metadata(col_name, 'Type Details', 'std', std)
                self.add_column_metadata(col_name, 'Type Details', 'mean', mean)
#                
            ########## Textual  ########## 
            elif data_type is TypeDetector.TEXTUAL:
                printv("Processing Column {0}: {1} - Text".format(i+1, col_names[i]), str(i+1))
                #printv('    Processing Info', '.')
                info = col.astype(str).describe()
                text_cols_names.append(col_name)
                #printv('    Processing Count', '.')
                count = info['count']
                missing = total_rows - count
                total_missing_values += missing
                #printv('    Processing Lenght', '.')
                lenghts=col.astype(str).str.len()
                length_min=lenghts.min()
                length_max=lenghts.max()
                length_mean=lenghts.mean()
                length_std=lenghts.std()
                App.debug('Counting words...')
                word_counts = col.astype(str).apply(lambda x: len(x.split()) if x is not None else 0)
                word_count_min = word_counts.min()
                word_count_max = word_counts.max()
                word_count_std = word_counts.std()
                word_count_mean = word_counts.mean()
                top = None
                if 'top' in info.keys(): top = info['top'].__repr__().strip()
                freq = None
                if 'freq' in info.keys(): freq = info['freq']
                
                unique = info['unique']
                text_cols.append({'Count':count, 
                    'Missing':       missing, 
                    'Unique Values': unique, 
                    'Most Frequent': top, 
                    'Top Frequency': freq,
                    'Lenght Min':    '{0:.0f}'.format(length_min),
                    'Lenght Max':    '{0:.0f}'.format(length_max),
                    'Lenght Mean':   '{0:.2f}'.format(length_mean),
                    'Lenght Std':    '{0:.2f}'.format(length_std),
                    'Word Count Min':  word_count_min,
                    'Word Count Max':  word_count_max,
                    'Word Count Std':  word_count_std,
                    'Word Count Mean': word_count_mean,
                    'Types Percent': str(col_types_percent_detailed)
                })
                # Save Column Metadata
                self.add_column_metadata(col_name, 'Type Details', 'length-min', length_min)
                self.add_column_metadata(col_name, 'Type Details', 'length-max', length_max)
                self.add_column_metadata(col_name, 'Type Details', 'length-std', length_std)
                self.add_column_metadata(col_name, 'Type Details', 'length-mean', length_mean)
                self.add_column_metadata(col_name, 'Type Details', 'words-min', word_count_min)
                self.add_column_metadata(col_name, 'Type Details', 'words-max', word_count_max)
                self.add_column_metadata(col_name, 'Type Details', 'words-mean', word_count_mean)
                self.add_column_metadata(col_name, 'Type Details', 'words-std', word_count_std)
                value_counts = valid_col_values.value_counts()

            else: # data_type is TypeDetector.NULL:
                printv("Processing Column {0}: {1} - {2}".format(i+1, col_names[i], data_type), str(i+1))
                # printv('    Processing Info', '.')
                info =  col.astype(str).describe()
                null_cols_names.append(col_name)
                # printv('    Processing Count', '.')
                count = info['count']
                missing = len(col) - col.count()
                total_missing_values += missing
                # printv('    Processing Lenght', '.')
                lenghts=col.astype(str).apply(lambda x: len(x))
                length_min=lenghts.min()
                length_max=lenghts.max()
                length_mean=lenghts.mean()
                length_std=lenghts.std()
                top = None
                if 'top' in info.keys(): top = info['top'].__repr__().strip()
                freq = None
                if 'freq' in info.keys(): freq = info['freq']
                
                unique = info['unique']
                null_cols.append({'Count':count, 
                    'Missing':       missing, 
                    'Unique Values': unique, 
                    'Most Frequent': top, 
                    'Top Frequency': freq,
                    'Lenght Min':    '{0:.0f}'.format(length_min),
                    'Lenght Max':    '{0:.0f}'.format(length_max),
                    'Lenght Mean':   '{0:.2f}'.format(length_mean),
                    'Lenght Std':    '{0:.2f}'.format(length_std),
                    'Types Percent': str(col_types_percent_detailed)
                })
                # Save Column Metadata
                self.add_column_metadata(col_name, 'Type Details', 'length-min', length_min)
                self.add_column_metadata(col_name, 'Type Details', 'length-max', length_max)
                self.add_column_metadata(col_name, 'Type Details', 'length-std', length_std)
                self.add_column_metadata(col_name, 'Type Details', 'length-mean', length_mean)
                # print 'valid_col_values[:10]=', valid_col_values[:10]
                # if len(valid_col_values) > 0:
                value_counts = valid_col_values.value_counts()
                # else:
                #     value_counts = {}

            # #Add column info
            column_data = {'database-id': self.db_name, 
                            'column-name':col_name,
                            'socrata-type':metadata_type,
                            'profiler-type':data_type,
                            'profiler-most-detected_%': precision, 
                            'profiler-most-detected': most_detected,
                            'unique': unique,
                            'missing': missing,
                            'values': count,
                        }
            # General
            self.add_column_metadata(col_name, 'General', 'top-value', top)
            self.add_column_metadata(col_name, 'General', 'top-freq', freq)
#            self.add_column_metadata(col_name, 'General', 'profiler-most-detected_%', precision)
#            self.add_column_metadata(col_name, 'General', 'profiler-most-detected', most_detected)

            # Add column index to column metadata
            if ProfilerUtils.COLUMN_INDEXES in metadata and col_name in metadata[ProfilerUtils.COLUMN_INDEXES]:
                self.add_column_metadata(col_name, 'General', 'index', metadata[ProfilerUtils.COLUMN_INDEXES][col_name])

            if value_counts is not None:
                top_k = {}
                unique_values = len(value_counts)
                limit = min(Profiler.MAX_TOP_K, unique_values)
                if self.part:
                        limit = unique_values
                for k in value_counts.keys()[:limit]:
                    # top_k[str(k)] = value_counts[k]
                    top_k[str(k)] = value_counts[k] # TODO: Fix a bug here
                self.add_column_metadata(col_name, 'Type Details', 'top-k', top_k)

            # Simple type info
            for k in col_types_percent.keys():
                self.add_column_metadata(col_name, 'Simple Type', k, col_types_percent[k])
            # Complete type info
            for k in col_types_percent_detailed.keys():
                self.add_column_metadata(col_name, 'Detailed Type', k, col_types_percent_detailed[k])
                
            self.types_summary = self.types_summary.append(column_data, ignore_index=True)
            
        
# ==============================================================================
# ============================ SUMMARYZE gps_data ==================================
# ==============================================================================
        # Sumary DataFrames
        self.numeric_DataFrame = pd.DataFrame(num_cols, index=num_cols_names)
        self.geo_DataFrame = pd.DataFrame(geo_cols, index=geo_cols_names)
        self.textual_DataFrame = pd.DataFrame(text_cols, index=text_cols_names)
        self.null_DataFrame = pd.DataFrame(null_cols, index=null_cols_names)
        self.temporal_DataFrame = pd.DataFrame(temp_cols, index=temp_cols_names)

        time_end = time.time()
        readable_time_end = TimeUtils.current_time_formated()

        # Database Sumary
        total_values=total_rows*col_names.size
        missing_percent=(total_missing_values*100.0)/(total_values)
        missing_percent = '{0:.2f}'.format(missing_percent)
       
        
        processing_time='{0:.2f}'.format(time_end - time_start)
        printv( '\n\n=============== DATABASE SUMARY ===============')
        printv( 'File: {0}'.format(self.db_name))
        printv( 'Rows: {0:n}'.format(total_rows))
        printv( 'Columns: {0:n}'.format(col_names.size))
        printv( '  - Geo: {0:n}'.format(len(geo_cols_names)))
        printv( '  - Temporal: {0:n}'.format(len(temp_cols_names)))
        printv( '  - Numeric: {0:n}'.format(len(num_cols_names)))
        printv( '  - Textual: {0:n}'.format(len(text_cols_names)))
        printv( 'Values')
        printv( '  - Total:   {0:n} (Rows x Columns)'.format(total_values))
        printv( '  - Missing: {0:n} ({1}%)'.format(total_missing_values, missing_percent))
        printv( 'Processing time: {0} sec'.format(processing_time))
       
        used_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        null_cols = col_names.size - len(num_cols_names) - len(geo_cols_names) - len(temp_cols_names) - len(text_cols_names)
        self.last_sumary = pd.DataFrame([
            {'Name': self.db_name, 
                'Rows':total_rows, 
                'Columns':col_names.size,
                'Columns Numeric':len(num_cols_names),
                'Columns Temporal':len(temp_cols_names),
                'Columns Geo':len(geo_cols_names),
                'Columns Text':len(text_cols_names),
                'Columns Null': len(null_cols_names),
                'Column Names Numeric': str(num_cols_names),
                'Column Names Geo': str(geo_cols_names),
                'Column Names Text': str(text_cols_names),
                'Column Names Temporal': str(temp_cols_names),
                'Values':total_values,
                'Values Missing':total_missing_values,
                'Values Missing Percent':missing_percent,
                'ETL-Profiler Processing Time (sec)':processing_time,
                'ETL-Profiler Time Begin':readable_time_start,
                'ETL-Profiler Time End':readable_time_end,
                'ETL-Profiler Input File':file_name,
                'ETL-Profiler Input File Size (KB)': metadata['file_size'],
                'ETL-Profiler Total Memory (MB)': used_memory,
                Profiler.STATUS: Profiler.STATUS_SUCCESS
            }], 
            columns = Profiler.SUMARY_COLUMNS,
            index = [self.db_name]
            )

        if self.ignore_metadata:
                printv( '=============== Metadata Ignored ===============')
        elif metadata is not None and MetadataUtils.has_success(metadata):
            try:
                printv( '=============== PROVIDED METADATA ===============')
                for key in metadata.keys():
                    if key == MetadataConstants.TYPES: continue #Ignore Provided Types in dataset metadata

                    value = metadata[key]
                    App.debug(key, '=', value, ' - type:', type(value))
                    self.last_sumary[key] = value.__str__()
                self.last_sumary[MetadataConstants.PRIMARY] = MetadataUtils.is_primary(metadata)
                printv('')
            except (UnicodeEncodeError) as ex:
                #do nothing
                printv('UnicodeEncodeError with socrata metadata.')
                if self.stop_on_error: raise ex
            
        # ==============================================================================
        # ============================ Process Geo gps_data ====================================
        # ==============================================================================
        if self.ignore_index:
            printv('Ignoring geo-temp index')
        else:
            printv('Processing Geographic gps_data')
            self.generate_index(database)
        
# ==============================================================================
# ============================ SHOW RESULTS ====================================
# ==============================================================================
        if self.show_details:
            if self.show_all_columns:
                numeric_info_to_show = self.numeric_DataFrame.columns.tolist()
                
                text_info_to_show = self.textual_DataFrame.columns.tolist()
                if 'Value Counts' in text_info_to_show: text_info_to_show.remove('Value Counts')

                geo_info_to_show = self.geo_DataFrame.columns.tolist()
                if 'Value Counts' in geo_info_to_show: geo_info_to_show.remove('Value Counts')
                
                temporal_info_to_show = self.temporal_DataFrame.columns.tolist()
                if 'Value Counts' in temporal_info_to_show: temporal_info_to_show.remove('Value Counts')
            else:
                numeric_info_to_show = Profiler.NUMERIC_INFO_SMALL
                text_info_to_show = Profiler.TEXT_INFO_SMALL
                geo_info_to_show = Profiler.GEO_INFO_SMALL
                temporal_info_to_show = Profiler.TEMPORAL_INFO_SMALL
            null_info_to_show = Profiler.TEMPORAL_INFO_SMALL
                
            if len(geo_cols) > 0: 
                print '\n=============== Geo gps_data Sumary:'
#                print self.geo_DataFrame[geo_info_to_show]
#                for count, row in self.geo_DataFrame[geo_info_to_show].iterrows():
#                    print '>>>>>>>>>>>>>>>>>>>>', row
                print self.geo_DataFrame[geo_info_to_show]
            if len(num_cols) > 0: 
                print '=============== Numeric Sumary:'
                print self.numeric_DataFrame[numeric_info_to_show]
            if len(temp_cols) > 0: 
                print '\n=============== Temporal Sumary:'
                print self.temporal_DataFrame[temporal_info_to_show]
            if len(text_cols) > 0: 
                print '\n=============== Textual Sumary:'
                print self.textual_DataFrame[text_info_to_show]
            if len(null_cols_names) > 0: 
                print '\n=============== Null  Sumary:'
                print self.null_DataFrame[null_info_to_show]

            printv( '\n========================================================= Types Information:')
            printv('        --- Complete ---')
            printv( str_cols_types_percent.rstrip('\n') )
            printv('\n        ------------------- Types Summary ------------------- ')
            printv( self.types_summary )
            printv( '===============================================================')
            printv (self.last_sumary.T)
#            printv('\n        ------------------- Column Metadata  ------------------- ')
#            printv( '===============================================================')
#            printv (self.column_metadata)
            
        printv( '===============================================================')

# ==============================================================================
# ================================ SAVE FILES ==================================
# ==============================================================================
        if self.save_output_files:
            print 'Generated Files:'
#            self.save_dataframe_to_csv(self.numeric_DataFrame, '_profiled_numeric')
#            self.save_dataframe_to_csv(self.geo_DataFrame, '_profiled_geo')
#            self.save_dataframe_to_csv(self.textual_DataFrame, '_profiled_textual')
#            self.save_last_sumary_to_json()
#            filename = self.to_folder + self.db_name + '_types.json'
#            self.types_summary.to_csv()
            
            if self.last_zip_rows is None: print ' No Zip file to save.'
            else: 
                filename = self.to_folder + self.db_name + '_zip.csv'
                self.last_zip_rows.to_csv(filename)
                print '    '+filename

            if self.last_gps_rows is None: print ' No GPS file to save.'
            else: 
                filename = self.to_folder + self.db_name + '_gps.csv'
                self.last_gps_rows.to_csv(filename)
                print '    '+filename
                
            if self.geo_index is None: print ' No GEO INDEX file to save.'
            else: 
                filename = self.to_folder + self.db_name + '_index.csv'
                self.geo_index.to_csv(filename)
                print '    '+filename
                
        elif self.verbose:
            print 'CSV files not saved.'
        
        # if self.plot: 
        #     base_name = self.to_folder + self.db_name
        #     Insight.insight_on_single_sumary(base_name, self.last_sumary, self.textual_DataFrame, 
        #                                                 self.numeric_DataFrame, 
        #                                                 self.geo_DataFrame, 
        #                                                 database)
                                                        
        return self



