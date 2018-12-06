import sys, os
sys.path.append(os.getcwd().replace('scripts', '') + '/urban_profiler')

from multiprocessing import Pool, Lock
import traceback
from utils import CLI
import ApplicationOptions 

b_opts = {
	'headers': False,
}
v_opts = {
	'workers': 1,
	'file': None,
	'arg_file_name': None,
	'args': None,
	'target': None
}

FOLDER = '/tmp/x'

def validate_opts(opts):
	if opts['file'] is None: raise Exception('file can not be None')
	if opts['workers'] is None: raise Exception('workers can not be None')
	# if opts['arg_file_name'] is None: raise Exception('workers can not be None')
	if opts['target'] is None: raise Exception('target can not be None')

def split_input_file(filename, parts, headers):
	lines_in_file = sum(1 for line in open(filename))
	if parts > lines_in_file: 
		parts = lines_in_file
	lines_per_part = lines_in_file/parts

	print 'split', filename, 'in', str(parts), 'with', lines_per_part, 'lines each'

	split_param_a = len(str(parts))
	print CLI.run_bash('split -a {0} -dl {1} {2}'.format(split_param_a, lines_per_part, filename), folder='/tmp')

	files = []
	for i in range(0, parts):
		files.append(FOLDER + str(i).rjust(split_param_a, '0'))

	if headers:
		header = CLI.run_bash('head -n 1 ' + filename)
		print 'header=', header

	return files

def run_parallel(filename, opts):
	pid = str(os.getpid())
	try:
		cmd = opts['target'] + ' '
		if opts['arg_file_name']: cmd+= '--' + opts['arg_file_name']
		cmd+= filename
		if opts['args'] is not None: cmd += ' ' + opts['args']
		print '[{0}:BEGIN]'.format(pid), cmd
		print CLI.run_bash(cmd)
		print '[{0}:END]'.format(pid), cmd

	except:
		msg = 'THREAD: [' + pid + ']\n'
		msg +=  traceback.format_exc() + '\n'
		ApplicationOptions.error(msg)

def main():
	opts = CLI.process_args(value_opts=v_opts, boolean_opts=b_opts)
	validate_opts(opts)

	files = split_input_file(opts['file'], int(opts['workers']), opts['headers'])

	pool = Pool(int(opts['workers']))
	print 'Created pool with size:', opts['workers']
	for f in files:
		print 'Creating job for file ', f
		pool.apply_async(run_parallel, args=(f,opts))

	print 'All jobs created. Waiting for results...'
	pool.close()
	pool.join()
	print 'All profilers done.'

if __name__ == "__main__":
	main()