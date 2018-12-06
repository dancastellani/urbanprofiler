# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import unittest
from urban_profiler.utils import ResourceUtils as ResourceUtils

TEST_PATH = 'test/'

class ResourceUtilsTestCase(unittest.TestCase):

    # -------------- TEST RESOURCEs
    def test_get_test_resource_path_file_is_right(self):
        answer = ResourceUtils.get_test_resource_path('aAa')
        # print 'answer= ', answer
        assert answer.endswith('aAa')

    def test_get_test_resource_path_folder_is_right(self):
        answer = ResourceUtils.get_test_resource_path('aAa')
        folder = answer.rstrip('aAa')
        # print 'folder= ', folder
        assert folder.endswith('/test/resources/')

    def test_get_test_resource_path_folder_has_test_path(self):
        answer = ResourceUtils.get_test_resource_path('aAa')
        folder = answer.rstrip('aAa')
        # print 'folder= ', folder
        assert TEST_PATH in answer

    # -------------- MAIN RESOURCES
    def test_get_resource_path_file_is_right(self):
        answer = ResourceUtils.resource_path_of('aAa')
        # print 'answer= ', answer
        assert answer.endswith('aAa')

    def test_get_resource_path_folder_is_right(self):
        answer = ResourceUtils.resource_path_of('aAa')
        folder = answer.rstrip('aAa')
        # print 'folder= ', folder
        assert folder.endswith('/urban_profiler/resources/')

    def test_get_resource_path_folder_dont_have_test_path(self):
        answer = ResourceUtils.resource_path_of('aAa')
        folder = answer.rstrip('aAa')
        # print 'folder= ', folder
        assert TEST_PATH not in answer

    # def test_egg_resource_has_egg_path(self):
    #     resource = 'zip_codes.csv'
    #     answer = ResourceUtils.get_resource_from_egg(resource)
    #     folder = answer.rstrip(resource)
    #     assert folder.endswith('egg/urban_profiler/resources/')


if __name__ == '__main__':
    unittest.main()
