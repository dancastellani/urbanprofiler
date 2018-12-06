#!/bin/bash

rm -f /home/cusp/dancastellani/projects/etl-output/log.txt

#####################> FAST
#script -c " python /home/cusp/dancastellani/projects/auto-etl/src/Main.py --db_ids_file=/home/cusp/dancastellani/projects/auto-etl/src/resources/cusp/database_ids_with_lat_long --to_folder=/home/cusp/dancastellani/projects/etl-output/ --verbose --threads=30" | tee /home/cusp/dancastellani/projects/etl-output/log.txt
#FILE=/home/cusp/dancastellani/databases/CCW_2015_other_datasets.csv
FILE='ids_tabular_only_2015-08-18'
#FILE='ids_tabular_only_2015-04-22'

#FILE='ids_tabular_only_2015-04-22_SAMPLE'
#FILE='ids_tabular_view_2015-03-30.csv'
#FILE='ids_view_2015-03-30.csv'
echo file=$FILE
WORKERS=40
#####################> COMPLETE
script -c " python /home/cusp/dancastellani/projects/auto-etl/src/Main.py --db_ids_file=/home/cusp/dancastellani/projects/auto-etl/src/resources/cusp/$FILE --to_folder=/home/cusp/dancastellani/projects/etl-output/ --verbose --threads=$WORKERS " | tee /home/cusp/dancastellani/projects/etl-output/log.txt
