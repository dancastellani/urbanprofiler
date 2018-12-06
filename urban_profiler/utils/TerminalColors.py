# Terminal Color: http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
# http://misc.flogisoft.com/bash/tip_colors_and_formatting

# class TerminalColors:
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
DIM = '\033[2m'
RED = '\033[31m'

def colored(option):
	print option
	
def end_colors():
		print ENDC