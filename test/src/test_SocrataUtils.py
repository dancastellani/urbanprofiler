# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import unittest
from urban_profiler.ApplicationConstants import MetadataConstants
from urban_profiler.utils import SocrataUtils
from urban_profiler.utils import ResourceUtils
import pandas
from urban_profiler import ApplicationOptions as App


class  ProfilerTestCaseMultipleDatabases(unittest.TestCase):

    # def setUp(self):
        # print '[TEST:', self._testMethodName, ']'

    # ========================================================================== metadata_of(...)
    def test_request_metadata_of_inexistent_id_should_not_be_successful(self):
        metadata = SocrataUtils.metadata_of('inexistent database id')
        assert metadata[MetadataConstants.STATUS] is MetadataConstants.STATUS_ERROR_VIEW_NOT_FOUND

    def test_request_metadata_of_valid_id_should_be_successful(self):
        metadata = SocrataUtils.metadata_of('bbs3-q5us')
        assert metadata[MetadataConstants.STATUS] is MetadataConstants.STATUS_SUCCESS

    # ========================================================================== is_primary(...)
    def test_is_primary_should_return_false_when_metadata_is_None(self):
        metadata = None
        self.assertFalse(SocrataUtils.is_primary(metadata))

    def test_is_primary_should_return_false_when_metadata_status_is_not_success(self):
        metadata = {MetadataConstants.STATUS: 'error'}
        self.assertIsNone(SocrataUtils.is_primary(metadata))

    def test_is_primary_should_return_false_when_metadata_does_not_have_key_author(self):
        metadata = {MetadataConstants.STATUS: MetadataConstants.STATUS_SUCCESS, 'Socrata Owner': 'b'}
        self.assertFalse( SocrataUtils.is_primary(metadata) )

    def test_is_primary_should_return_false_when_metadata_does_not_have_key_owner(self):
        metadata = {MetadataConstants.STATUS: MetadataConstants.STATUS_SUCCESS, 'Socrata Author': 'a'}
        self.assertFalse( SocrataUtils.is_primary(metadata) )

    def test_is_primary_should_return_false_when_metadata_author_and_owner_are_different_and_View_From_is_not_None(self):
        metadata = {MetadataConstants.STATUS: MetadataConstants.STATUS_SUCCESS, 'Socrata Author': 'a', 'Socrata Owner': 'b', 'Socrata View From':'a'}
        self.assertFalse( SocrataUtils.is_primary(metadata) )

    def test_is_primary_should_return_true_when_metadata_author_and_owner_are_equal(self):
        metadata = {MetadataConstants.STATUS: MetadataConstants.STATUS_SUCCESS, 'Socrata Author': 'a', 'Socrata Owner': 'a'}
        self.assertTrue( SocrataUtils.is_primary(metadata) )
        
    # ========================================================================== prepare_location_columns(...)
    def test_prepare_location_columns_with_vz8c_29aj_csv_creates_gps_column(self):
        metadata_types = {'Phone': 'text', 'Districts Served': 'text', 'Borough': 'text', 'Location 1': 'location'}
        database = pandas.read_csv(ResourceUtils.get_test_resource_path('vz8c-29aj.csv'))
        
        SocrataUtils.prepare_location_columns(database, metadata_types)
        database_cols = list(database.columns)
        
        self.assertIn('Location 1'+ SocrataUtils.PREFIX_NEW_COLUMN +'gps', database_cols)



if __name__ == '__main__':
    unittest.main()