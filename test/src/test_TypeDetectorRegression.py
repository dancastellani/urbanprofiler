import unittest
import pandas

from urban_profiler import ApplicationOptions as App
from urban_profiler.utils import ResourceUtils
from urban_profiler.profiler import TypeDetector

DATABASE_h9gi_nx95_PATH = ResourceUtils.get_test_resource_path('h9gi-nx95_SAMPLE.csv')


class TypeDetectorTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.database_h9gi_nx95 = pandas.read_csv(DATABASE_h9gi_nx95_PATH)

	def setUp(self):
		App.stop_debuging()
		# print '[TEST:', self._testMethodName, ']'
		self.database_h9gi_nx95 = TypeDetectorTests.database_h9gi_nx95

		self.type_counts = {
			TypeDetector.GEO_GPS: 0, TypeDetector.GEO_ZIP: 0, TypeDetector.GEO_BOROUGH: 0,
			TypeDetector.TEMPORAL_DATE: 0, TypeDetector.TEMPORAL_TIME: 0, TypeDetector.TEMPORAL_DATE_TIME: 0,
			TypeDetector.NUMERIC_INT: 0, TypeDetector.NUMERIC_DOUBLE: 0,
			TypeDetector.TEXTUAL: 0,
			TypeDetector.NULL: 0}

	# --------------------------------------------------------------------------- Regression Tests
	# def test_regressions_DB_h9gi_nx95_CONTRIBUTING_FACTOR_VEHICLE_1_IS_TEXT(self):
	# 	col_data = self.database_h9gi_nx95['CONTRIBUTING FACTOR VEHICLE 1']
	# 	detected_type = TypeDetector.type_of_column_data(col_data)
	# 	self.assertEqual(TypeDetector.TEXTUAL, detected_type)

	def test_regressions_DB_h9gi_nx95_ON_STREET_NAME_SIMPLE_TYPE_IS_GEO(self):
		col_data = self.database_h9gi_nx95['ON STREET NAME']
		detected_type = TypeDetector.type_of_column_data(col_data)
		self.assertEqual(TypeDetector.TEXTUAL, detected_type)

	def test_regressions_DB_h9gi_nx95_ON_STREET_NAME_MOST_DETECTED_TYPE_IS_GEO_ADDRESS(self):
		col_data = self.database_h9gi_nx95['ON STREET NAME']
		detected_type = TypeDetector.most_detected(TypeDetector.types_of(col_data))[0]
		print 'detected types:', TypeDetector.types_of(col_data)
		print 'detected type:', detected_type
		self.assertEqual(TypeDetector.TEXTUAL, detected_type)

	# If Fails, check the type, because should be Numeric Integer.
	def test_regressions_DB_2bh6_qmgg_Mean_Scale_Score_is_Geo_Zip_but_should_be_Numeric_Integer(self):
		col_data = pandas.read_csv(ResourceUtils.get_test_resource_path('2bh6-qmgg'))['Mean Scale Score']
		detected_type = TypeDetector.most_detected(TypeDetector.types_of(col_data))[0]
		self.assertEqual(TypeDetector.GEO_ZIP, detected_type)

	# Actually some of the values are zip code valid values.
	def test_regressions_DB_2bh6_qmgg_Mean_Scale_Score_has_no_zip_codes(self):
		# App.start_debuging()
		col_data = pandas.read_csv(ResourceUtils.get_test_resource_path('2bh6-qmgg'))['Mean Scale Score']
		detected = TypeDetector.detect_zip(col_data)[1]
		self.assertEqual(54, len(detected))


if __name__ == '__main__':
	unittest.main()
