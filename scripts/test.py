# import sys, os
# from multiprocessing import Pool, Lock


# THREADS = 5

# def my_callback(param):
#     msg =  ' ________________________________________________________________________ \n'
#     msg += '/\n'
#     msg += 'param:' + param + '\n'
#     # msg += '| Profiled: {0}/{1} ({2:.2f}%) - {3}\n'.format(actual, total_databases, actual*100.0/total_databases, TimeUtils.current_time_formated())
#     msg +=  '\\________________________________________________________________________\n'
#     print msg

# def run_as_job(param):
#     print 'entered in ', param
#     try:
#         pid = str(os.getpid())
#         print 'Begin: [' + pid + ']: ' + param
#         # profiler.profile(database_file) <-----------------------
#         print os.popen('date').read().rstrip()
#         print 'End: [' + pid + ']: ' + param
    
#     except (KeyboardInterrupt):
#         print 'aaa'
#         # App.error('KeyboardInterrupt with: ' + database_file)
#         # STOP_RUNNING = True and ApplicationOptions.OPTIONS['stop_on_error']
    
#     except:
#         msg = '[' + pid + '] ERROR in THREAD:\n'
#         msg += '['+ pid +'] -----------------------------------------------------------------\n'
#         for line in traceback.format_exc().split('\n'):
#             msg += '[' + pid + '] ' + line + '\n'
#         msg += '[' + pid + '] -----------------------------------------------------------------'
#         ## Will print colored here instead of app.error as facilitates reading error output and debuging
#         # print tc.RED + msg + tc.ENDC
#         ApplicationOptions.error(msg)
#         # raise
#     finally:
#         return param

# if __name__ == "__main__":      
#     print 'INICIO'
#     pool_size = THREADS
#     pool = Pool(pool_size)
#     print 'Thread Pool created with size: ', pool_size
#     for a_param in ['1', '2', '3', '4', '1', '2', '3', ]:
#         pool.apply_async(run_as_job, args=(a_param,), callback= my_callback )

#     pool.close()
#     print 'waiting threads'
#     pool.join()
#     print 'THE END.'


from threading import Thread
import urllib2

downloaded_page = None # global

def download(url):
    """Download ``url`` as a single string"""
    global downloaded_page

    downloaded_page = urllib2.urlopen(url).read()
    print "Downloaded", downloaded_page[:200]


def main_work():
    # do some busy work in parallel
    print "Started main task"
    x = 0
    for i in xrange(100000):
        x += 1
    print "Completed main task"

if __name__ == '__main__':
    # perform the download in the background
    Thread(target=lambda: download("http://www.jython.org")).start()
    Thread(target=lambda: download("http://www.jython.org")).start()
    Thread(target=lambda: download("http://www.jython.org")).start()
    Thread(target=lambda: download("http://www.jython.org")).start()
    Thread(target=lambda: download("http://www.jython.org")).start()
    main_work()