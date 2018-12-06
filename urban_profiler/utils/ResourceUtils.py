# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "danielcastellani"
__date__ = "$Jun 26, 2014 2:04:26 PM$"

import os
import socket
from pkg_resources import resource_stream, Requirement

# maybe this ca break outside PyCharm
TEST_RESOURCE_FOLDER = os.getcwd().split('/test')[0].split('/urban_profiler')[0] + '/test/resources/'
MAIN_RESOURCE_FOLDER = (os.getcwd()).split('/test/src')[0] + '/urban_profiler/resources/'
EGG_RESOURCE_FOLDER = 'urban_profiler/resources/'

# Identifies if UrbanProfiler is running on the CUSP Spark Cluster
SPARK_CLUSTER_HOSTNAME = 'cluster.cusp.nyu.edu'
RUNNING_ON_CLUSTER = 'hadoop' in socket.gethostname() or 'cluster' in socket.gethostname()


def get_resource_from_egg(name):
    # TODO: figure out a way to remove the hardcoded version number from here.
#    return resource_stream(Requirement.parse("urbanprofiler"), EGG_RESOURCE_FOLDER + name)
    return name


def get_test_resource_path(name):
    return TEST_RESOURCE_FOLDER + name


def resource_path_of(name):
    global MAIN_RESOURCE_FOLDER
    # tests
    if 'test/urban_profiler' in MAIN_RESOURCE_FOLDER:
        MAIN_RESOURCE_FOLDER = MAIN_RESOURCE_FOLDER.split('/test/urban_profiler')[0] + '/urban_profiler/resources/'

    # spark
    elif RUNNING_ON_CLUSTER:
        return get_resource_from_egg(name)

    # we just admit it is running from the project root dir. Like in development.
    return MAIN_RESOURCE_FOLDER + name
