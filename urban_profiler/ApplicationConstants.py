GPS_PRECISION = 6
ENHANCER_INDEX = False

GPS_SEPARATOR = ', '
MISSING_DATA_SYMBOL = None

OUTPUT_FILE_INDEX_SUFFIX = '_index.csv'

DATABASE_NAME = 'urbanprofiler'

INDEX_COLUMN_MAX_SIZE_ZIPCODE = 20
INDEX_MISSING_DATA_SYMBOL = ''


##################################################################
## Metadata
##################################################################
class MetadataConstants:
	PREFIX = 'Socrata '
	DISPLAY_TYPE_KEY = PREFIX + 'Display Type'
	ID_COLUMN = PREFIX + 'ID Column'
	IS_PRIMARY = 'Socrata_is_Primary'
	STATUS = PREFIX + 'Status'
	#Status
	STATUS_SUCCESS = 'OK'
	STATUS_ERROR_VIEW_NOT_FOUND = 'View Not found.'
	STATUS_ERROR_METADATA_NOT_FOUND = 'Metadata Not found.'

	SOURCE = 'Source'
	SOURCE_URL = 'Source URL'
	ACCESS_TYPE = PREFIX + "Access Type"
	
	AGENCY = PREFIX + "Agency"
	TAGS = "Tags"
	ATTRIBUTION = PREFIX + "Attribution"
	AUTHOR = PREFIX + "Author"
	CATEGORY = PREFIX + "Category"
	CREATED_AT = PREFIX + "Created At"
	DESCRIPTION = PREFIX + "Description"
	ID_COLUMN = PREFIX + "ID Column"
	ID = PREFIX + "Id"
	LAST_MODIFIED = PREFIX + "Last Modified"
	NAME = PREFIX + "Name"
	OWNER = PREFIX + "Owner"
	ORGANIZATION = PREFIX + "Organization"

	#================== For Socrata Datasets
	COMMENTS = PREFIX + "Comments"
	METADATA_SOURCE_URL = PREFIX + "Source URL"
	METADATA_SOURCE_NAME = PREFIX + "Source Name"
	DISPLAY_TYPE = PREFIX + "Display Type"
	DOWNLOAD_COUNT = PREFIX + "Download Count"
	NUMBER_OF_COMMENTS = PREFIX + "Number of Coments"
	PRIMARY = PREFIX + "Primary"
	PUBLICATION_DATE = PREFIX + "Publication Date"
	TYPES = PREFIX + "Types"
	UPDATE_FREQUENCY = PREFIX + "Update Frequency"
	VIEW_COUNT = PREFIX + "View Count"
	VIEW_FROM = PREFIX + "View From"
	VIEW_TYPE = PREFIX + "View Type"


##################################################################
## Metadata
##################################################################
class MessageConstants:
	ERROR_METADATA_FILE_CANNOT_BE_NULL = 'Metadata file cannot be null.'