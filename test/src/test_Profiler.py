# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import unittest
from urban_profiler.utils import ResourceUtils
from urban_profiler.profiler.Profiler import Profiler
from urban_profiler import ApplicationOptions
from mock import MagicMock

DATABASE_h9gi_nx95_SAMPLE_NO_EXTENSION_PATH = ResourceUtils.get_test_resource_path("h9gi-nx95_SAMPLE")
###########################################
## NYPD Vehicle Motor Colision is h9gi-nx95
###########################################

class Profiler_TestCase_NYPD(unittest.TestCase):
    
    summary_h9gi_nx95 = None
    summary_h9gi_nx95_SAMPLE = None
     
    def setUp(self):
        # print '[TEST:', self._testMethodName, ']'
        if Profiler_TestCase_NYPD.summary_h9gi_nx95_SAMPLE is None:
            verbose = False
            ApplicationOptions.OPTIONS = {'silent':not verbose, 'verbose':verbose, 'stop_on_error':True, 'show_details':True}
            self.profiler = Profiler()
            
            self.profiler.profile(DATABASE_h9gi_nx95_SAMPLE_NO_EXTENSION_PATH)
            Profiler_TestCase_NYPD.summary_h9gi_nx95_SAMPLE = self.profiler.last_sumary
            
        self.summary_h9gi_nx95_SAMPLE = Profiler_TestCase_NYPD.summary_h9gi_nx95_SAMPLE.ix[0]
        
    # =========================================================================== NYPD_MVCS
    def test_status_OK(self):
        self.assertEqual('OK', self.summary_h9gi_nx95_SAMPLE['ETL-Profiler Status'])

    def test_run_profiler_of_NYPD_VCS(self):
        self.assertIsNotNone(self.summary_h9gi_nx95_SAMPLE)
        
    def test_Numeric_Columns(self):
        self.assertEqual(9, self.summary_h9gi_nx95_SAMPLE['Columns Numeric'])
        
    def test_Geo_Columns(self):
        print '>>>> self.summary_h9gi_nx95_SAMPLE[Columns Geo]:', self.summary_h9gi_nx95_SAMPLE['Columns Geo']
        self.assertEqual(4, self.summary_h9gi_nx95_SAMPLE['Columns Geo'])

    def test_Textual_Columns(self):
        self.assertEqual(7, self.summary_h9gi_nx95_SAMPLE['Columns Text'])

        self.assertTrue("'ON STREET NAME" in self.summary_h9gi_nx95_SAMPLE['Column Names Text'])
        self.assertTrue("CROSS STREET NAME" in self.summary_h9gi_nx95_SAMPLE['Column Names Text'])


    def test_Temporal_Columns(self):
        self.assertEqual(2, self.summary_h9gi_nx95_SAMPLE['Columns Temporal'])
        
    def test_Geo_Columns_Names_has_the_real_geo_columns(self):
        self.assertTrue("BOROUGH" in self.summary_h9gi_nx95_SAMPLE['Column Names Geo'])
        self.assertTrue("ZIP CODE" in self.summary_h9gi_nx95_SAMPLE['Column Names Geo'])
        self.assertTrue("LATITUDE" in self.summary_h9gi_nx95_SAMPLE['Column Names Geo'])
        self.assertTrue("LONGITUDE" in self.summary_h9gi_nx95_SAMPLE['Column Names Geo'])

    def test_profiler_of_NYPD_VCS_has_Temporal_Columns_Names(self):
        answer = "['DATE', 'TIME']"
        self.assertEqual(answer, self.summary_h9gi_nx95_SAMPLE['Column Names Temporal']) 
    
    # =========================================================================== h9gi_nx95_SAMPLE_NO_EXTENSION_PATH
    def test_run_profiler_of_h9gi_nx95_SAMPLE_NO_EXTENSION_PATH_is_not_none(self):
        self.assertIsNotNone(self.summary_h9gi_nx95_SAMPLE)
        
    def test_run_profiler_of_h9gi_nx95_SAMPLE_NO_EXTENSION_PATH_status_ok(self):
        self.assertEqual('OK', self.summary_h9gi_nx95_SAMPLE['ETL-Profiler Status'])


# =========================================================================== Regression tests with real databases
class Regression_Tests(unittest.TestCase):

    def setUp(self):
        ApplicationOptions.OPTIONS = {'silent': True, 'verbose': False, 'stop_on_error': True}
        self.profiler = Profiler()

    # def test_profile_real_database_with_socrata_metadata_h9gi_nx95(self):
    #     self.profiler.profile(ResourceUtils.get_test_resource_path('h9gi-nx95_SAMPLE.csv'))
    #     self.assertEqual('OK', self.profiler.last_sumary.ix[0]['ETL-Profiler Status'])

    def test_profile_real_database_with_socrata_metadata_vz8c_29aj_csv(self):
        self.profiler.profile(ResourceUtils.get_test_resource_path('vz8c-29aj.csv'))
        self.assertEqual('OK', self.profiler.last_sumary.ix[0]['ETL-Profiler Status'])

    def test_profile_real_database_with_socrata_metadata_vz8c_29aj_csv_has_gps_values(self):
        ApplicationOptions.OPTIONS = {'silent': True, 'verbose': False, 'stop_on_error': True, 'skip_views': True}
        profiler = Profiler()
        profiler.profile(ResourceUtils.get_test_resource_path('vz8c-29aj.csv'))
        summary = profiler.last_sumary.ix[0]
        print 'summary\n', summary
        print 'summary\n', summary['Column Names Geo']

        self.assertEqual(4, summary['Columns Geo'])
        self.assertGreater(summary['GPS Values'], 0)

    def test_profile_real_database_erm2_nwe9_with_skip_should_profile_with_success(self):
        ApplicationOptions.OPTIONS = {'silent': True, 'verbose': False, 'stop_on_error': True, 'skip_views': True}
        profiler = Profiler()
        profiler.check_if_skip_dataset = MagicMock(return_value=True)
        profiler.profile(ResourceUtils.get_test_resource_path('erm2-nwe9'))
        self.assertEqual(profiler.last_sumary.ix[0]['ETL-Profiler Status'], Profiler.MSG_SKIP_VIEW)
    
    # def test_profile_real_database_td5q_ry6d_should_skip_with_success(self):
    #     self.profiler.profile(ResourceUtils.get_test_resource_path('td5q-ry6d'))
    #     self.assertEqual(self.profiler.last_sumary.ix[0]['ETL-Profiler Status'], 'OK')


if __name__ == '__main__':
    unittest.main()