# Urban Profiler: Urban Data Profiler + Data Finder.

__Why 2 projects on the same repository?__

This facilitate to manage their versions as the Data Finder depends so much on the Urban Profiler.
Also it is almost two parts of a single application: 
one offline that profiles datasets and another online which 
the end-users can use to find and explore datasets.

## Collaborators
* Daniel Castellani
* Huy Vo
* Juliana freire
* Claudio Silva


## Publications
* Daniel Castellani Ribeiro, Huy T. Vo, Juliana Freire, and Cláudio T. Silva. 2015. An Urban Data Profiler. In Proceedings of the 24th International Conference on World Wide Web (WWW '15 Companion). ACM, New York, NY, USA, 1389-1394. DOI: http://dx.doi.org/10.1145/2740908.2742135

# Urban (Data) Profiler

This is the offline part that profiles the datasets and extract metadata about them.
Design details can be found on the paper _An Urban Data Profiler_.

## Requirements:
* Run on Linux or Mac (not Windows)
* Python 2.7

## Install:
* run `./configure`
* run `make install`
* To make sure it is running properly, run `make test`

__Note:__

The `configure` is prepared to run on Ubuntu (=> 14.04). Adjustments are needed to run on CentOS or another OS.

## CLI Usage 
To extract metadata from a dataset file run `python urban_profiler.py --file=<your_file> --to_folder=<desired_output_folder>`.

### CLI arguments
Bellow are the expected CLI arguments with the default values.
`    
    -  show_all_info =  False
    -  verbose =  False
    -  skip_rows =  None
    -  to_folder =  None
    -  cusp_dw =  False
    -  show_details =  False
    -  types_file =  None
    -  nrows =  None
    -  ignore_index =  False
    -  threads =  20
    -  metadata_file =  None
    -  file =  ../NYPD_Motor_Vehicle_Collisions_SAMPLE.csv
    -  save_details =  False
    -  plot =  False
    -  silent =  False
    -  database_refs =  None
    -  stop_on_error =  False
    -  skip_views =  False
    -  part =  False
    -  sources_in_metadata =  False
    -  debug =  False
    -  output_name =  None
    -  db_ids_file =  None
`
## Example
Usage examples can be found on the Wiki.

# Data Finder
AKA: Urban Profiler Web

## Requirements
* Django
* Postgres


## Install
* run `./configure` 
* run `make install`
