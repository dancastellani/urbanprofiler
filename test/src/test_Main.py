# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import unittest

import sys
sys.path.append("/urban_profiler/plot")

from urban_profiler.utils import ResourceUtils
from urban_profiler import Main
from urban_profiler.utils import CLI as CLI
from urban_profiler import ApplicationOptions


LIST_DATABASES_FAST_PATH = ResourceUtils.get_test_resource_path('open_data_test_list_fast.csv')
LIST_DATABASES_FAST_WITH_ERROR_PATH = ResourceUtils.get_test_resource_path('open_data_test_list_fast_with_Error.csv')

class  Profile_Multiple_Datasets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ApplicationOptions.OPTIONS = {'silent':True, 'stop_on_error':True}

    # def setUp(self):
        # print '[TEST:', self._testMethodName, ']'

    # TODO: refactor those tests and uncomment them.
    # def test_profile_dataset_list_with_error(self):
    #     CLI.ARGS = ['--silent', '--stop_on_error', '--to_folder=/tmp', '--file=a']
    #     self.assertRaises(Exception, Main.main)
    #
    # def test_profile_dataset_list_with_error_but_dont_stop_on_error(self):
    #     CLI.ARGS = ['--silent', '--show_details', '--to_folder=/tmp', '--database_refs=' + LIST_DATABASES_FAST_WITH_ERROR_PATH]
    #     Main.main()
    #
if __name__ == '__main__':
    unittest.main()