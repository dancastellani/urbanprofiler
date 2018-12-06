from urban_profiler.spark import SparkProfiler as spark_profile
from urban_profiler.profiler import Profiler
from urban_profiler.utils import FileUtils
from pyspark import SparkConf, SparkContext
from operator import add
import sys, json

from urban_profiler import Main

# TEST_FILE = '/home/danielcastellani/Documents/databases/open-data-nyc/samples/h9gi-nx95.csv'
TEST_FILE = 'hdfs:///user/dancastellani/test/resources/erm2-nwe9'
#TEST_FILE = '/data/share/nycopendata/h9gi-nx95/h9gi-nx95'

APP_NAME = 'UrbanProfilerSpark'

def main(sc, filename):
    print 'BEGIN'
    opts = Main.v_opts.copy()
    opts.update(Main.b_opts)
    opts.update({'verbose': False, 'silent': True})
    print 'Profiling on Spark...'

    profiled_data = spark_profile.profile(filename, sc, options=opts)
    # print 'type:', type(profiled_data)
    print 'Profiler Status:', profiled_data[Profiler.Profiler.STATUS]

    print 'Saving...'
    profiled_data_str = json.dumps(profiled_data, sort_keys=True, indent=4)
    # FileUtils.write_to_hdfs(filename + '_up_result.json', json.dumps(profiled_data, sort_keys=True, indent=4))
    output_file = 'spark-test/' + filename.split('/')[-1] + '-result'
    print 'output_file=', output_file
    # with open(output_file , 'w') as f:
    #     f.write("%s" % profiled_data)
    rdd = sc.parallelize(profiled_data_str)
    #rdd.coalesce(1).saveAsTextFile(output_file)
    rdd.saveAsTextFile(output_file)

    print 'END.'

if __name__ == "__main__":
    # Configure Spark
    conf = SparkConf().setAppName(APP_NAME)
    # conf = conf.setMaster("local[*]")
    sc = SparkContext(conf=conf)
    # filename = sys.argv[1]
    filename = TEST_FILE

    # Execute Main functionality
    main(sc, filename)

    print 'THE END.'
