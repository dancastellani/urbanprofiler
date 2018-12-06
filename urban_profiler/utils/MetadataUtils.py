#!/usr/bin/python

import os, sys
from urban_profiler import ApplicationOptions as App
from urban_profiler.ApplicationConstants import MetadataConstants as MetadataConstants
from urban_profiler.utils import SocrataUtils as SocrataUtils
import pandas
import json

METADATA_FILE_ORGANIZATION = 'organization'
METADATA_FILE_CATALOG_DATASET_ID = 'catalog_dataset_id'
METADATA_FILE_CATEGORY = 'category'
METADATA_FILE_SOURCE_FILE = 'source_file'
METADATA_FILE_TAGS = 'tags'
METADATA_FILE_CUSP_COLOR = 'cusp_color'
METADATA_FILE_UPDATE_FREQUENCY = 'update_frequency'
METADATA_FILE_AUTHOR = 'author'
METADATA_FILE_MAINTAINER = 'maintainer'
METADATA_FILE_ACCESS_TYPE = 'access_type'
SOURCE = 'source'
SOURCE_URL = 'socrata_portal_url'

def metadata_source_is_socrata(source):
	return source is not None and type(source) is str and source.lower() == 'socrata'

def metadata_of(database_name, file_name, metadata_file = None):
	if metadata_file is None:
		metadata = SocrataUtils.metadata_of(database_name)
	else:
		metadata = get_metadata_from_file(database_name, file_name, metadata_file)
		if metadata_source_is_socrata(metadata[SOURCE]):
			print '   Metadata file references Socrata Portal:', metadata[MetadataConstants.SOURCE_URL]
			metadata = SocrataUtils.metadata_of(database_name, portal_url = metadata[MetadataConstants.SOURCE_URL])
			metadata = metadata

	App.debug( json.dumps(metadata, ensure_ascii=False, indent=4, sort_keys=True) )
	return metadata


def get_metadata_from_file(database_name, file_name, metadata_file):
	#Read metadata from File
	metadata = {}
	App.info("Reading metadata from file.")

	metadata_from_file = pandas.read_csv(metadata_file)
	ds_metadata = metadata_from_file.loc[metadata_from_file[METADATA_FILE_SOURCE_FILE] == file_name]
	# print '=============================================\n'
	# print 'ds_metadata\n', ds_metadata.T
	# print '=============================================\n'
	if len(ds_metadata) == 0:
		metadata[MetadataConstants.STATUS] = MetadataConstants.STATUS_ERROR_METADATA_NOT_FOUND
		return metadata

	ds_metadata = ds_metadata.iloc[0]

	metadata[MetadataConstants.ORGANIZATION] = ds_metadata[METADATA_FILE_ORGANIZATION]
	##> Load SOURCE info and check if shoudl continue or return
	metadata[SOURCE] = ds_metadata[SOURCE]
	# print '=========metadata[SOURCE]=================>', metadata[SOURCE]
	if metadata_source_is_socrata(metadata[SOURCE]):
		metadata[MetadataConstants.SOURCE_URL] = ds_metadata[SOURCE_URL]
		return metadata

	metadata[MetadataConstants.AGENCY] = ds_metadata[METADATA_FILE_ORGANIZATION]
	metadata[MetadataConstants.CATEGORY] = ds_metadata[METADATA_FILE_CATEGORY]
	metadata[MetadataConstants.OWNER] = ds_metadata[METADATA_FILE_ORGANIZATION]
	metadata[MetadataConstants.AUTHOR] = ds_metadata[METADATA_FILE_MAINTAINER]
	metadata[MetadataConstants.UPDATE_FREQUENCY] = ds_metadata[METADATA_FILE_UPDATE_FREQUENCY]
	metadata[MetadataConstants.TAGS] = ds_metadata[METADATA_FILE_TAGS]

	metadata[MetadataConstants.ACCESS_TYPE] = ds_metadata[METADATA_FILE_ACCESS_TYPE]
	metadata[MetadataConstants.ACCESS_TYPE] += ' - ' + ds_metadata[METADATA_FILE_CUSP_COLOR]

	metadata[MetadataConstants.DISPLAY_TYPE] = 'Table'
	metadata[MetadataConstants.VIEW_TYPE] = 'Tabular'

	# print '-------------__> metadata:', metadata
	metadata[MetadataConstants.STATUS] = MetadataConstants.STATUS_SUCCESS

	return metadata

def is_socrata_view(metadata):
	return metadata[SOURCE] == 'Socrata' and \
		metadata[MetadataConstants.STATUS] is MetadataConstants.STATUS_SUCCESS and \
		not SocrataUtils.is_primary(metadata)

def is_primary(metadata):
	if metadata[SOURCE] == 'Socrata': SocrataUtils.is_primary(metadata)
	else: return True

def has_success(metadata):
	return metadata[MetadataConstants.STATUS] is MetadataConstants.STATUS_SUCCESS