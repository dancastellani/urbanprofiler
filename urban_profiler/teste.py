from multiprocessing import Pool, Lock
import os
import time
from random import randint
import pandas

def info(title):
#        print '                                 .', (os.getpid())
        module =  'Module name:' + __name__
        parent = '. parent process:' + str(os.getppid())
        pid = '. process id:' + str(os.getpid())
        time.sleep( randint(0,3) )
        output =  module + parent + pid + ' => ' + str(title)

        c=0
        for i in range(1000):
                c+i
        return output

list = []

def my_print(x):
        list.append(x)
        print '[', len(list), '] (', os.getpid(), ') ', x

if __name__ ==  '__main__':
        args = range(10)

        print '------- Race Begin'

        p = Pool (3)

        for i in args:
                result = p.apply_async(info, args=(i,), callback= my_print )
        p.close()
        p.join()


#       for i in result.get():
#               print i  

        #it =  p.imap(info, args)
        #while it:
        #       print it.next()

        print '------ Race Ends!'
        print 'list:\n', list