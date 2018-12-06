# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 27, 2014 6:52:18 PM$"

import pandas
from urban_profiler.utils import FileUtils
from urban_profiler.utils import MetadataUtils
from urban_profiler.profiler import TypeDetector
import re
import os

COLUMN_INDEXES = 'Column Indexes'
COLUMNS_HEADER = 'Columns Header'


def dataset_name_of(file_name, part):
    ds_name = ''
    ds_name = FileUtils.get_file_name(file_name)
    ds_name = re.sub('\.csv$', '', ds_name)
    ds_name = re.sub('\.json$', '', ds_name)
    if part:
        ds_name = ds_name.split('.part_')[0]
    return ds_name


def init_profiler(file_name, part=False, metadata_file=None, ignore_metadata=False):
    db_name = dataset_name_of(file_name, part)
    file_rows = FileUtils.count_lines(file_name)
    if ignore_metadata:
        metadata = {}
    else:
        metadata = MetadataUtils.metadata_of(db_name, file_name, metadata_file)
    metadata['file_size'] = FileUtils.get_file_size(file_name)
    # Add columns order in file to metadata
    metadata[COLUMN_INDEXES] = get_column_indexes(file_name)
    metadata[COLUMNS_HEADER] = FileUtils.get_cols_from_csv_header(file_name)
    metadata['db_name'] = db_name

    return metadata, file_rows


def get_column_indexes(file_name):
    columns_with_index = {}
    cols = FileUtils.get_cols_from_csv_header(file_name)
    for idx, col in enumerate(cols):
        columns_with_index[col] = idx
    return columns_with_index


def get_types_data_as_DataFrame_with_NULL_last(data_types_string):
    types_percent = data_types_string.strip().replace('\n', ',').replace("'", "\"")
    types_percent_str = '{' + types_percent + '}'

    regex_fix_json = re.compile(r"\b\"s")
    types_percent_str = regex_fix_json.sub('*s', types_percent_str)

    dataFrame = pandas.read_json(types_percent_str).T
    
    # Put NULL on last position
    columns = list(dataFrame.columns)
    if TypeDetector.NULL in dataFrame.columns:
        columns.remove(TypeDetector.NULL)
    else:
        dataFrame[TypeDetector.NULL] = 0
    columns.append(TypeDetector.NULL)
    
    return dataFrame[columns]
    

def columns_to_save_in_csv(dataFrame):
    cols = []

    for col in dataFrame.columns:
        if col != 'Value Counts' and not col.endswith('Profiler'): 
            cols.append(col)
    return list(cols)
    

def read_profiler_file(profiler_file_name):
    profiler_file = open(profiler_file_name,'r')
    lines = profiler_file.readlines()

    sumary = pandas.read_json(lines[0])
    text_profiler = pandas.read_json(lines[1])
    numeric_profiler = pandas.read_json(lines[2])
    geo_profiler = pandas.read_json(lines[3])
    return sumary, text_profiler, numeric_profiler, geo_profiler

def write_profiler_file(profiler_file_name, dataFrame, textual_df, numeric_df, geo_df):
    profiler_file = open(profiler_file_name,'w')
    sumary_cols = columns_to_save_in_csv(dataFrame)
    profiler_file.write('{0}\n'.format(dataFrame[sumary_cols].to_json()))
    profiler_file.write('{0}\n'.format(textual_df.to_json()))
    profiler_file.write('{0}\n'.format(numeric_df.to_json()))
    profiler_file.write('{0}\n'.format(geo_df.to_json()))
    profiler_file.close()
