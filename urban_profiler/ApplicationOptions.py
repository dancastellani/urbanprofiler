# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "danielcastellani"
__date__ = "$Aug 21, 2014 4:32:27 PM$"

# import inspect
from urban_profiler.utils import TerminalColors as colors

OPTIONS = {'not initialized yet': True}


def stop_debuging():
    OPTIONS['debug'] = False


def start_debuging():
    OPTIONS['debug'] = True


def get_option(key, default=None, options=OPTIONS):
    # print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    # print ">>>>>>>>>>>>>>>>>>>>> options=", options
    # print ">>>>>>>>>>>>>>>>>>>>> OPTIONS=", options
    if options is not None and key in options.keys():
        return options[key]
    elif key in OPTIONS.keys():
        return OPTIONS[key]
    else:
        return default


def debug(*messages):
    if 'debug' in OPTIONS.keys() and OPTIONS['debug']:
        print_colored(colors.DIM, '[DEBUG]', messages)


def error(messages, raise_exception=False):
    print_colored(colors.RED, '[ERROR]', messages)
    if raise_exception: raise Exception(prepare_messages(messages))


def warn(messages):
    print_colored(colors.WARNING, '[WARNING]', messages)


def info(message, quiet_message=None):
    if get_option('verbose', default=False):
        print message
    elif quiet_message:
        print quiet_message


def print_colored(color, prefix='', *messages):
    msg = prepare_messages(prefix, messages)
    print color + msg + colors.ENDC


def prepare_messages(prefix='', *messages):
    if type(messages) is not tuple: return prefix + ' ' + messages
    msg = prefix + ' '
    for tup in messages:
        msg += str(tup[0])
    return msg.replace('\\n', '\n')
