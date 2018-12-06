# # To change this license header, choose License Headers in Project Properties.
# # To change this template file, choose Tools | Templates
# # and open the template in the editor.
# import json
# import unittest
#
# import findspark
# findspark.init(edit_profile = True)
# from pyspark.context import SparkContext
# from pyspark.sql import SQLContext
#
# from profiler.Profiler import Profiler
# from spark import SparkProfiler
# from urban_profiler import ApplicationOptions
# from utils import ResourceUtils, PandasUtils, ProfilerUtils
#
#
# class SparkProfilerTestCase(unittest.TestCase):
#
#     def setUp(self):
# 		self.sc = SparkContext('local[4]')
#         # quiet_logs(self.sc)
#
#
#     def tearDown(self):
#         self.sc.stop()
#
#
#     def test_spark_context(self):
#         # start by creating a mockup dataset
#         l = [(1, 'hello'), (2, 'world'), (3, 'world')]
#         # and create a RDD out of it
#         rdd = self.sc.parallelize(l)
#         self.assertIsNotNone(rdd)
#
#
#     def test_profile_dataset_part1(self):
#         dataset_file = ResourceUtils.get_test_resource_path('erm2-nwe9.part_1')
#         options = {"parts": True,
#                    "verbose": False,
#                    "stop_on_error": True,
#                    }
#
#         sqlContext = SQLContext(self.sc)
#         part_dataframe = sqlContext.read.format('com.databricks.spark.csv')\
#                                             .options(header=True, inferschema='true').load(dataset_file)
#
#         metadata, file_rows = \
#             ProfilerUtils.init_profiler(dataset_file, metadata_file=None, part=True)
#         print 'metadata[ProfilerUtils.COLUMNS_HEADER]=', metadata[ProfilerUtils.COLUMNS_HEADER]
#
#         profiled_metadata = SparkProfiler.profile_part(part_dataframe, options, dataset_file, metadata)
#
#         self.assertTrue(Profiler.STATUS in profiled_metadata.keys())
#         self.assertEquals(profiled_metadata[Profiler.STATUS], Profiler.STATUS_SUCCESS)
#
#         self.assertEquals(profiled_metadata["Columns"], 52)
#         self.assertEquals(profiled_metadata["Columns Geo"], 13)
#         self.assertEquals(profiled_metadata["Columns Temporal"], 4)
#         self.assertEquals(profiled_metadata["Columns Numeric"], 3)
#         self.assertEquals(profiled_metadata["Columns Text"], 20)
#         self.assertEquals(profiled_metadata["Rows"], 49)
#         self.assertEquals(profiled_metadata["GPS Values"], 121)
#         self.assertEquals(profiled_metadata["GPS-Lat-Max"], 40.8733129392)
#         self.assertEquals(profiled_metadata["GPS-Lat-Min"], 40.5817444882)
#         self.assertEquals(profiled_metadata["GPS-Long-Max"], -73.7797616655)
#         self.assertEquals(profiled_metadata["GPS-Long-Min"], -74.0842877473)
#         # print 'Profiled Metadata:\n', json.dumps(profiled_metadata, indent=4, sort_keys=True)
#
#     # def test_profile_dataset_par2(self):
#     #     dataset_file = ResourceUtils.get_test_resource_path('erm2-nwe9.part_2')
#     #     options = {"parts": True,
#     #                "verbose": False,
#     #                "stop_on_error": True,
#     #                }
#     #
#     #     part_dataframe = PandasUtils.load_database(dataset_file)
#     #     metadata, file_rows = \
#     #         ProfilerUtils.init_profiler(dataset_file, metadata_file=None, part=True)
#     #     profiled_metadata = SparkProfiler.profile_part(part_dataframe, options, dataset_file, metadata)
#     #
#     #     self.assertTrue(Profiler.STATUS in profiled_metadata.keys())
#     #     self.assertEquals(profiled_metadata[Profiler.STATUS], Profiler.STATUS_SUCCESS)
#     #
#     #     self.assertEquals(profiled_metadata["Columns"], 52)
#     #     self.assertEquals(profiled_metadata["Columns Geo"], 14)
#     #     self.assertEquals(profiled_metadata["Columns Temporal"], 4)
#     #     self.assertEquals(profiled_metadata["Columns Numeric"], 3)
#     #     self.assertEquals(profiled_metadata["Columns Text"], 21)
#     #     self.assertEquals(profiled_metadata["Rows"], 50)
#     #     self.assertEquals(profiled_metadata["GPS Values"], 140)
#     #     self.assertEquals(profiled_metadata["GPS-Lat-Max"], 40.8811999316)
#     #     self.assertEquals(profiled_metadata["GPS-Lat-Min"], 40.5792868671)
#     #     self.assertEquals(profiled_metadata["GPS-Long-Max"], -73.7871083038)
#     #     self.assertEquals(profiled_metadata["GPS-Long-Min"], -74.1182671587)
#     #     # print 'Profiled Metadata:\n', json.dumps(profiled_metadata, indent=4, sort_keys=True)
#     #
#     # def test_profile_dataset_join(self):
#     #     ApplicationOptions.OPTIONS = {"verbose": False}
#     #     # ApplicationOptions.start_debuging()
#     #
#     #     profiled_metadata_file = ResourceUtils.get_test_resource_path('erm2-nwe9_profiled_metadata.part_1.json')
#     #     with open(profiled_metadata_file, 'rb') as json_file:
#     #         json_part1 = json.loads(json_file.read())
#     #     profiled_metadata_file = ResourceUtils.get_test_resource_path('erm2-nwe9_profiled_metadata.part_2.json')
#     #     with open(profiled_metadata_file, 'rb') as json_file:
#     #         json_part2 = json.loads(json_file.read())
#     #
#     #     joined = SparkProfiler.reduce_summaries(json_part1, json_part2)
#     #
#     #     # print 'Joined Metadata:\n', json.dumps(joined, indent=4, sort_keys=True)
#     #
#     #     self.assertEquals(round(joined["GPS-Lat-Min"], 5), 40.57929)
#     #     self.assertEquals(round(joined["GPS-Lat-Max"], 4), 40.8812)
#     #     self.assertEquals(joined["GPS-Long-Min"], -74.1182671587)
#     #
#     #     # TODO: Check this later to make sure the time is right.
#     #     # self.assertEquals(joined["Date Min"], '2014-08-13')
#     #     # self.assertEquals(joined["Date Max"], '2014-09-13')
#     #
#     #     self.assertEquals(joined["Columns"], 52)
#     #     self.assertEquals(joined["Rows"], 99)
#     #     self.assertEquals(joined["Values"], 5148)
#     #     self.assertEquals(joined["Values Missing"], 1438) # TODO: this is different from the original (1335). why?
#     #     self.assertEquals(joined["GPS Values"], 261)
#     #     self.assertEquals(joined["Socrata Category"], 'Social Services')
#     #     self.assertEquals(round(joined["GPS-Lat-Max"], 4), 40.8812)
#     #     self.assertEquals(round(joined["GPS-Lat-Min"], 5), 40.57929)
#     #     self.assertEquals(round(joined["GPS-Long-Max"], 5), -73.77976)
#     #     self.assertEquals(round(joined["GPS-Long-Min"], 5), -74.11827)
#     #     # self.assertEquals(profiled_metadata["Columns Geo"], 14)
#     #     # self.assertEquals(profiled_metadata["Columns Temporal"], 4)
#     #     # self.assertEquals(profiled_metadata["Columns Numeric"], 3)
#     #     # self.assertEquals(profiled_metadata["Columns Text"], 21)
#     #     # self.assertEquals(profiled_metadata["GPS Values"], 140)
#
# if __name__ == '__main__':
#     unittest.main()
