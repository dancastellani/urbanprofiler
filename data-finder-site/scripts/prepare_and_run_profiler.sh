#generate the file
python manage.py runscript generate_types_to_detect --script-args=/tmp/types_to_detect.csv

#scp to shell
scp /tmp/types_to_detect.csv dancastellani@shell.cusp.nyu.edu:~/types_to_detect.csv

#ssh shell and update project
ssh dancastellani@shell.cusp.nyu.edu 'cd ~/projects/auto-etl/ && git pull'

#ssh to shell->compute and run profiler
 ssh dancastellani@shell.cusp.nyu.edu \
 	"ssh compute 'cd ~/projects/auto-etl; ./scripts/runProfiler_multi_thread.sh &'"
