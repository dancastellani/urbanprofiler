import unittest
import pandas

from urban_profiler.utils import ResourceUtils
from urban_profiler.utils import PandasUtils as PandasUtils

DATABASE_NYPD_MVCS_PATH = ResourceUtils.get_test_resource_path('h9gi-nx95_SAMPLE.csv')
DATABASE_2nju_4jd4_PATH = ResourceUtils.get_test_resource_path('2nju-4jd4.json')

class PandaUtils_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        PandaUtils_Tests.database_NYPD_MVC = pandas.read_csv(DATABASE_NYPD_MVCS_PATH)

    def setUp(self):
        # print '[TEST:', self._testMethodName, ']'
        self.database_NYPD_MVC = PandaUtils_Tests.database_NYPD_MVC

    # ========================================================================== load_database()
    def test_load_database_with_csv(self):
        assert PandasUtils.load_database(DATABASE_NYPD_MVCS_PATH) is not None
        
    def test_load_json_with_data_and_metadata_and_subcolumns(self):
        data_frame = PandasUtils.load_database(DATABASE_2nju_4jd4_PATH)
        self.assertEqual(24, len(data_frame.columns))
        
    def test_load_with_file_not_found_should_raise_error(self):
        self.assertRaises(IOError, PandasUtils.load_database, 'bla')


if __name__ == '__main__':
    unittest.main()