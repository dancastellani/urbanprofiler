# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 15, 2014 3:39:06 PM$"

import os, sys

def write_to_hdfs(filename, content):
    os.system('echo "%s" | hadoop fs -put - %s' % (content, filename))


def get_cols_from_csv_header(filepath):
    with open(filepath, 'r') as f: first_line = f.readline()
    cols = first_line.strip('\n').split(',')
    return cols


def count_lines(file_path):
    if os.path.isfile(file_path):
        num_lines = sum(1 for line in open(file_path))
        if num_lines is None:
            raise Exception('File "{}" does not exists.'.format(file_name))
        return num_lines
    else:
        return None


def get_file_name(file_path):
    return file_path.split('/')[-1]

def get_file_size(file_name):
    return os.path.getsize(file_name) / 1024.

def folder_of(file_path):
    return file_path[:len(get_file_name(file_path))]


def all_files(folder, with_extension=None, recursive=True):
    dir = os.path.abspath(folder)
    
    sub_files = []
    local_files = []
    for file_or_folder in os.listdir(dir):
        if file_or_folder not in [".","..",".git"]:
            full_path = dir + '/' + file_or_folder 
            
            if recursive and os.path.isdir(full_path):
                sub_files += all_files(full_path, with_extension, recursive) 
    
            else:
                if with_extension is None or file_or_folder.endswith(with_extension):
                    local_files.append( full_path )
                    
    total_files = sub_files + local_files
#    print '{0} > (local + sub = total) :: {1} + {2} = {3}'.format(folder, len(local_files), len(sub_files), len(total_files))
    return total_files

if __name__ == "__main__":
    files = all_files(sys.argv[1], sys.argv[2], sys.argv[3])

    counts_extension = {}
    counts_type = {}
    print '==================\nFiles:'
    for file in files:
#        print file
        
        fileName, fileExtension = os.path.splitext(file)
        if fileExtension in counts_extension:
            counts_extension[fileExtension] = counts_extension[fileExtension] + 1
        else:
            counts_extension[fileExtension] = 1
        
        fileType = os.popen("file -i '{0}'".format(file)).read().rstrip().split(':')[1].rstrip()
        if fileType in counts_type:
            counts_type[fileType] = counts_type[fileType] + 1
        else:
            counts_type[fileType] = 1
    
    print '==================\nCount by extension:'
    for extension in counts_extension.keys():
        print extension + ': ' + str(counts_extension[extension])

    print '==================\nCount by type:'
#    for type in counts_type.keys():
#        print str(counts_type[type]) + ' x ' + type
    
    import operator
    counts_type = sorted(counts_type.iteritems(), key=operator.itemgetter(1), reverse=True)
    for type in counts_type: print type
    
    print 'Total: {0}'.format(len(files))
