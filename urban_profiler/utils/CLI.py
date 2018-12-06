# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 22, 2014 4:34:33 PM$"

import sys, os, subprocess
from urban_profiler import ApplicationOptions as App

ARGS = None

def process_args(value_opts={}, boolean_opts={}):
    v_opts = value_opts.copy()
    b_opts = boolean_opts.copy()
    b_opts['debug'] = False
    
    opts = {}
    
    args = ARGS or sys.argv[1:]
    print 'args=', args
    
    for arg in args:
        param = arg.split('=')[0][2:] if '=' in arg else arg[2:]
        value = arg.split('=')[1] if '=' in arg else None
        
        if param == 'help':
            print 'Possible simple params are:'
            for opt in b_opts.keys():
                print '    --' + opt
            print 'And valuable params are:'
            for opt in v_opts.keys():
                print '    --' + opt
            sys.exit (0)
            
        elif value is None:
            if param not in b_opts:
                print 'param: {0}'.format(param)
                raise SystemExit('ERROR: Invalid arg "{0}".\nValid options are: {1} with preceding --.'.format(arg, b_opts.keys()));
            else:
                b_opts[param] = True
            
        elif param in v_opts:
            v_opts[param] = value
                        
        else:
            raise SystemExit('ERROR: Invalid value arg "{0}".\nValid options are: {1} with preceding -- and with numeric values. like --nrows=10.'.format(arg, v_opts.keys()));
            
    opts.update(b_opts)
    opts.update(v_opts)
    
    if opts['debug']:
        App.start_debuging()
        
    if 'debug' in opts and opts['debug']:
        print 'Considered options:'
        for k in opts:
            print '   - {0} = {1}'.format(k, opts[k])

    return opts

def run_bash(bash_command, folder=None):
    cmd = bash_command
    if type(cmd) == str: cmd = cmd.split()
    
    if folder is None:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=folder, stderr=subprocess.STDOUT)

    stdout_data, stderr_data = process.communicate()
    if process.returncode != 0:
        message = "%r failed, status code %s stdout %r stderr %r" % (
                       cmd, process.returncode, stdout_data, stderr_data)
        App.error(message)
        raise RuntimeError(message)
    output = ''
    if stdout_data: output += stdout_data
    if stderr_data: output += stderr_data
    return output