__author__ = 'dancastellani'
__date__ = '5/9/16'

import json

import pandas

from urban_profiler import ApplicationOptions as App
from urban_profiler.utils import TextUtils

from urban_profiler.profiler import Profiler
from urban_profiler.utils import ProfilerUtils
from urban_profiler.utils import PandasUtils

from pyspark import SparkConf, SparkContext
# APP_NAME = 'UrbanProfilerSpark'
current_sc = None
# def getSparkContext():
#     global SC
#     if SC is not None:
#         return SC
#     else:
#         # Configure Spark
#         conf = SparkConf().setAppName(APP_NAME)
#         conf = conf.setMaster("local[*]")
#         sc = SparkContext(conf=conf)
#         SC = getSparkContext()
#         return sc

# -----------------------------------------------------------------------------------------------
# --------------------- Overwriting Urban Profiler methods to work with Spark -------------------
# -----------------------------------------------------------------------------------------------
# urban_profiler/utils/FileUtils.py
from urban_profiler.utils import FileUtils

def spark_get_cols_from_csv_header(filepath):
    rdd = current_sc.textFile(filepath)
    return rdd.first().strip('\n').split(',')
FileUtils.get_cols_from_csv_header = spark_get_cols_from_csv_header

def spark_count_lines(file_path):
    try:
        current_sc.textFile(file_path).count()
    except:
        return None
FileUtils.count_lines = spark_count_lines

def spark_get_file_size(file_name):
    # return os.path.getsize(file_name) / 1024.
    return None
FileUtils.get_file_size = spark_get_file_size

# -----------------------------------------------------------------------------------------------

def complete_summary_as_json_string(profiler):
    """
    Return a complete summary of Urban Profiler in JSON format

    :param profiler: the profiler to get the complete JSON summary
    :return: the complete JSON summary
    """
    complete_summary = json.loads(profiler.last_sumary.ix[0].to_json())
    # The column Database-id and index are being removed from this output. to make it look like a list
    complete_summary[Profiler.COLUMN_METADATA] = json.loads(profiler.column_metadata.to_json())
    # complete_summary['Geo-Temp Index'] = json.loads(profiler.last_geo_index.to_json())

    # print " --------------------------------------- "
    # print 'complete_summary=', json.dumps(complete_summary, indent=4, sort_keys=False)
    # print " --------------------------------------- "

    return [complete_summary,]


def reduce_summaries(first, second):
    """
    This method joins two profile summaries in one that has information from both.
    If more than two summaries should be joined, join two by two.

    This method relies on naming convention for the variables to know how to join their values.
    For example, if the variable is count, then is just sum both counts.
    However if the variable is unique, then to join we need to consider the sets of values.
    Other examples are: sum, std, min, max.

    :param first: a summary to be joined
    :param second: another summary to be joined
    :return: a joined summary
    """
    # Init
    reprocess_column_types = False
    # print '\n\n------------------------------------------- reduce -------------------------------------------'
    # print '1st =>', first
    # print '\n2nd =>', second

    # return '(' + first + ' <_> ' + second + ')'

    # Verify if structure is the same and dataset too
    if first['Name'] != second['Name']:
        raise Exception('Summaries are not from the same dataset.')
    elif first['Columns'] != second['Columns']:
        raise Exception('Number of columns is not the same.')

    joined = {}
    # we'll assume both summaries have the same keys
    # TODO: Protect to when both don't have the same keys
    all_keys = first.keys()
    # all_keys = [TextUtils.reencode_if_not_ascii(k) for k in first.keys()]

    # Join values based on key convention names or specific keys
    App.info('Processing all keys: %s' % all_keys)
    for key in all_keys:
        App.debug('- kEY: %s' % key)
        if key.lower().endswith('min') or key.lower().endswith('begin'):
            joined[key] = min(first[key], second[key])

        elif key.lower().endswith('max') or key.lower().endswith('end'):
            joined[key] = max(first[key], second[key])

        # if the keys are not max, min, std, mean or unique just use first -- we`re assuming both are the same
        # After we join the dataset metadata we still have to join the column metadata
        elif key == Profiler.COLUMN_METADATA:
            joined['Column Metadata'] = reduce_column_metadata(first, second)

        # TODO: join geo-temp index
        # elif key == 'Geo-Temp Index':

        elif key in ['Rows', 'Values', 'Values Missing', 'ETL-Profiler Processing Time (sec)',
                     'ETL-Profiler Total Memory (MB)', 'GPS Values']:
            joined[key] = first[key] + second[key]

        elif key in ['Values Missing Percent']:
            total = int(first['Rows']) + int(second['Rows'])
            temp = (float(first[key]) * int(first['Rows']) + float(second[key]) * int(second['Rows'])) / total
            joined[key] = round(temp, 2)

        elif key in ['Column Names Geo', 'Column Names Numeric', 'Column Names Temporal', 'Column Names Text',
                     'Columns Names Null']:
            if first[key] == second[key]:
                joined[key] = first[key]
            else:
                # TODO: should be processed later based on column types
                reprocess_column_types = True
        else:
            App.debug('    first["%s"]= %s' % (key, first[key]))
            if first[key]:
                joined[key] = first[key]
            else:
                App.debug('    -> Ignoring null Value')

    return joined


def reduce_column_metadata(first, second):
    """
    Join column metadata in the same way as the dataset metadata, considering the conventions.
    * Simple and Detailed Types => weighted average
    * min and max => min and max
    * mean => weighed mean of first and second
    * std => ?

    :param first: a set of column metadata
    :param second: another set of column metadata
    :return: the joined column metadata
    """
    # Init vars
    group_by = ['Column-name', 'Database-id', 'Group', 'Key']
    result_columns = group_by + ['Value']
    # joined column metadata
    joined_cm = pandas.DataFrame(columns=result_columns)

    # Prepare the columns metadata with weight
    first_weight = first['Rows']
    second_weight = first['Rows']
    first_columns_metadata = pandas.read_json(json.dumps(first[Profiler.COLUMN_METADATA]))
    first_columns_metadata['weight'] = first_weight
    second_columns_metadata = pandas.read_json(json.dumps(second[Profiler.COLUMN_METADATA]))
    second_columns_metadata['weight'] = second_weight

    all_columns_metadata = first_columns_metadata.append(second_columns_metadata, ignore_index=True)
    # print 'Sample:\n', first_columns_metadata[:30]

    # for col in all_columns_metadata.columns:
    #     if col.endswith(('min', 'max', 'mean', 'lenght-min', 'lenght-max', 'words-min', 'lenght-mean', 'words-max', 'words-mean')):
    #         joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, col, group_by, result_columns)

    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'min', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'mean', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'max', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'lenght-min', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'lenght-mean', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'lenght-max', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'words-min', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'words-mean', group_by, result_columns)
    joined_cm = apply_on_column_metadata(all_columns_metadata, joined_cm, 'words-max', group_by, result_columns)

    return json.loads(joined_cm.T.to_json())


def apply_on_column_metadata(target, joined, key, group_by, result_columns, ):
    """
    This method apply a given function on a Pandas DataFrame grouping by certain keys and return the result.
    It does not return the weight.

    :param result_columns: list of columns to use to filter result
    :param group_by: list of columns to use to group
    :param target: DataFrame to apply the function
    :param joined: DataFrame to append the result
    :param key: key to filter values
    :return: result
    """
    temp = pandas.DataFrame()
    if key.lower().endswith('min'):
        temp = target[target.Key == key].dropna().groupby(group_by).min().reset_index()
    elif key.lower().endswith('max'):
        temp = target[target.Key == key].dropna().groupby(group_by).max().reset_index()
    elif key.lower().endswith('mean'):
        # total = int(first['Rows']) + int(second['Rows'])
        # a_temp = (float(first[key]) * int(first['Rows']) + float(second[key]) * int(second['Rows'])) / total
        # joined[key] = round(temp, 2)
        temp = target[target.Key == 'mean'].dropna()
        temp['temp'] = temp.Value.astype(float) * temp.weight.astype(int)
        temp = temp.groupby(group_by).sum().reset_index()
        # At this point, temp.weight.astype(int) = total weight as it is a sum of all weights
        temp['Value'] = temp.temp.astype(float) / temp.weight.astype(int)

    if len(temp) > 0:
        joined = joined.append(temp[result_columns], ignore_index=True)
    # print 'JOINED: ', joined.sort()

    return joined


def profile_part(part_dataframe, options, filename, metadata):
    """
    This method profile one part of a splited dataset file.

    :param metadata: initial metadata from dataset, such as provided metadata
    :param filename:
    :param part_dataframe: All dataset file parts should have a header in the first line and then the data lines.
    :param options: options to be used to configure the profiler
    :return: a JSON summary of all profiled metadata
    """
    # transform the Spark RDD to a pandas DataFrame as it`s what Profiler expects.
    # print '-------------------------------> Cols =', metadata[ProfilerUtils.COLUMNS_HEADER]
    pdf_as_list = list(part_dataframe)
    cols = metadata[ProfilerUtils.COLUMNS_HEADER]
    types = PandasUtils.prepare_dtypes_for_loading(cols)
    # print 'types=', types
    pandas_dataframe = pandas.DataFrame(pdf_as_list, columns=cols)  # , dtype=types)

    profiler = Profiler.Profiler(options)
    profiler.do_profile(pandas_dataframe, file_name=filename, skip_rows=0, n_rows=0, metadata=metadata)
    summary_to_return = complete_summary_as_json_string(profiler)

    return summary_to_return


# # def profile_partitions(partitions, options, filename, metadata):
# def profile_partitions(partitions):
#     final_iterator = []
#     for part in partitions:
#         # final_iterator.append(profile_part(part, options, filename, metadata))
#         final_iterator.append(count(part))
#     return iter(final_iterator)


def profile(dataset_file, spark_context, options={}):
    """
    Profiles a dataset CSV using UrbanProfiler.
    * pyspark must be called with : --packages com.databricks:spark-csv_2.11:1.4.0

    :param options: options dict for Profiler
    :param dataset_file: path to the dataset file
    :return:
    """
    from pyspark.sql import SQLContext
    sqlContext = SQLContext(spark_context)
    global current_sc
    current_sc = spark_context

    # File on hdfs: /data/share/nycopendata/h9gi-nx95/h9gi-nx95
    # dataset_file = '/data/share/nycopendata/h9gi-nx95/h9gi-nx95'
    # dataset_file = 'test/resources/h9gi-nx95.csv'

    # 0. Init profiler metadata
    # TODO: change this to read from options
    metadata_file = None
    metadata, file_rows = ProfilerUtils.init_profiler(dataset_file, metadata_file=metadata_file, part=options['part'])

    # 1. load csv
    # lines = sc.textFile(dataset_file)
    headers = len(metadata[ProfilerUtils.COLUMNS_HEADER]) > 0
    spark_dataframe = sqlContext.read.format('com.databricks.spark.csv').options(header=headers,
                                                                                 inferschema='true').load(dataset_file)
    print 'Size of dataset=', spark_dataframe.count()
    # spark_dataframe = spark_dataframe.coalesce(1)
    print 'RDD partitions=', spark_dataframe.rdd.getNumPartitions()

    # Just to be sure, add the part option
    # This indicates to profiler to generate all required metadata so multiple parts can be joined later.
    options['part'] = True


    # 2. call map on profile_parts
    profiled_parts = spark_dataframe.rdd.mapPartitions(lambda x: profile_part(x, options, dataset_file, metadata))

    # 3. call reduce on reduce_summaries
    reduced = profiled_parts.reduce(reduce_summaries)

    # print '\n\nResult:\n', reduced

    # 4. save product
    return reduced
