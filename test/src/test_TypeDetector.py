import unittest
import pandas

from urban_profiler import ApplicationOptions as App
from urban_profiler.utils import ResourceUtils
from urban_profiler.profiler import TypeDetector

DATABASE_NYPD_MVCS_PATH = ResourceUtils.get_test_resource_path('h9gi-nx95_SAMPLE.csv')
DATABASE_311_PATH = ResourceUtils.get_test_resource_path('311_Service_Requests_2009_SAMPLE.csv')
DATABASE_2j7x_tvss_PATH = ResourceUtils.get_test_resource_path('2j7x-tvss_SAMPLE.csv')
DATABASE_26ze_s5bx_PATH = ResourceUtils.get_test_resource_path('26ze-s5bx.csv')


class TypeDetectorTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.database_NYPD_MVC = pandas.read_csv(DATABASE_NYPD_MVCS_PATH)
		cls.database_311 = pandas.read_csv(DATABASE_311_PATH)
		cls.database_2j7x_tvss = pandas.read_csv(DATABASE_2j7x_tvss_PATH)
		cls.database_26ze_s5bx = pandas.read_csv(DATABASE_26ze_s5bx_PATH)

	def setUp(self):
		App.stop_debuging()
		# print '[TEST:', self._testMethodName, ']'
		self.database_NYPD_MVC = TypeDetectorTests.database_NYPD_MVC
		self.database_311 = TypeDetectorTests.database_311
		self.database_2j7x_tvss = TypeDetectorTests.database_2j7x_tvss
		self.database_26ze_s5bx = TypeDetectorTests.database_26ze_s5bx

		self.type_counts = {
			TypeDetector.GEO_GPS: 0, TypeDetector.GEO_ZIP: 0, TypeDetector.GEO_BOROUGH: 0,
			TypeDetector.TEMPORAL_DATE: 0, TypeDetector.TEMPORAL_TIME: 0, TypeDetector.TEMPORAL_DATE_TIME: 0,
			TypeDetector.NUMERIC_INT: 0, TypeDetector.NUMERIC_DOUBLE: 0,
			TypeDetector.TEXTUAL: 0,
			TypeDetector.NULL: 0}

	def test_type_geo_lat_or_long_loaded(self):
		self.assertIn(TypeDetector.DETECTOR_GEO_GPS_LAT_OR_LON, TypeDetector.data_detectors()[1])

	def test_type_detectors_are_static_if_no_param_passed(self):
		self.assertIn(TypeDetector.STATIC_DETECTORS, TypeDetector.data_detectors()[0])

	def test_SSN_invalid_if_less_than_9_numbers(self):
		values = pandas.Series(['1', '12345678', '123-45-678'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.SSN, values)
		self.assertEquals(len(detected), 0)

	def test_SSN_invalid_examples(self):
		values = pandas.Series(['219-09-9999', '078-05-1120'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.SSN, values)
		self.assertEquals(len(detected), 0)

	def test_SSN_invalid_examples_all_0s_in_each_part(self):
		values = pandas.Series(['000-09-9999', '218-00-9999', '218-09-0000'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.SSN, values)
		self.assertEquals(len(detected), 0)

	def test_SSN_valid_example_218_09_9999(self):
		values = pandas.Series(['218-09-9999'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.SSN, values)
		self.assertEquals(len(detected), 1)

	def test_SSN_valid_example_218099999_without_dashes(self):
		values = pandas.Series(['218099999'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.SSN, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_local(self):
		values = pandas.Series(['754-3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_local_2(self):
		values = pandas.Series(['754 3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_national(self):
		values = pandas.Series(['(541) 754-3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_national_2(self):
		values = pandas.Series(['541 754 3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_national_3(self):
		values = pandas.Series(['541-754-3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_national_international(self):
		values = pandas.Series(['+1 (541) 754-3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_national_international_2(self):
		values = pandas.Series(['+1 541 754-3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)

	def test_phone_valid_example_national_international_3(self):
		values = pandas.Series(['+1-541-754-3010'])
		detected = TypeDetector.valid_values_of_type(TypeDetector.PHONE, values)
		self.assertEquals(len(detected), 1)


	# --------------------------------------------------------------------------- detect single type: Null
	def test_detect_null_on_h9gi_nx95_LATITUDE(self):
		detected = TypeDetector.detect_null(self.database_NYPD_MVC.LATITUDE)[1]
		self.assertEqual(12, len(detected))

	def test_detect_null_nan(self):
		column = pandas.Series(['NaN'])
		detected = TypeDetector.detect_null(column)[1]
		self.assertEqual(1, len(detected))

	def test_detect_null_not_applied(self):
		column = pandas.Series(['N/A'])
		detected = TypeDetector.detect_null(column)[1]
		self.assertEqual(1, len(detected))

	def test_detect_null_none(self):
		column = pandas.Series(['None'])
		detected = TypeDetector.detect_null(column)[1]
		self.assertEqual(1, len(detected))

	def test_detect_null_null(self):
		column = pandas.Series(['Null'])
		detected = TypeDetector.detect_null(column)[1]
		self.assertEqual(1, len(detected))

	# --------------------------------------------------------------------------- DETECTOR_TEMPORAL_TIME
	def test_detect_TEMPORAL_TIME_on_h9gi_nx95_TIME(self):
		detected = TypeDetector.detect_from_regex(TypeDetector.DETECTOR_TEMPORAL_TIME, self.database_NYPD_MVC.TIME)[1]
		self.assertEqual(100, len(detected))

	# --------------------------------------------------------------------------- DETECTOR_TEMPORAL_DATE
	def test_detect_TEMPORAL_DATE_on_h9gi_nx95_DATE(self):
		detected = TypeDetector.detect_from_regex(TypeDetector.DETECTOR_TEMPORAL_DATE, self.database_NYPD_MVC.DATE)[1]
		self.assertEqual(100, len(detected))

	# --------------------------------------------------------------------------- DETECTOR_TEMPORAL_DATE_TIME
	def test_detect_TEMPORAL_DATE_TIME_on_311_Created_date(self):
		expected_type = TypeDetector.DETECTOR_TEMPORAL_DATE_TIME
		detected = TypeDetector.detect_from_regex(expected_type, self.database_311['Created Date'])[1]
		self.assertEqual(100, len(detected))

	# --------------------------------------------------------------------------- DETECTOR_TEMPORAL_DATE_TIME
	def test_detect_TEMPORAL_DATE_TIME_on_2j7x_tvss_Created_date(self):
		expected_type = TypeDetector.DETECTOR_TEMPORAL_DATE_TIME
		detected = TypeDetector.detect_from_regex(expected_type, self.database_2j7x_tvss['Created Date'])[1]
		self.assertEqual(100, len(detected))

	# --------------------------------------------------------------------------- detect single type: GEO_ZIP
	def test_detect_ZIP_with_non_zip_numbers_with_3_digit_should_not_find_any_match(self):
		column = pandas.Series([675, 686, 333])
		detected = TypeDetector.detect_zip(column)[1]
		self.assertEqual(0, len(detected))

	def test_detect_GEO_ZIP_on_h9gi_nx95_LATITUDE(self):
		detected = TypeDetector.detect_zip(self.database_NYPD_MVC.LATITUDE)[1]
		self.assertEqual(0, len(detected))

	def test_detect_GEO_ZIP_on_h9gi_nx95_ZIP_CODE(self):
		detected = TypeDetector.detect_zip(self.database_NYPD_MVC['ZIP CODE'])[1]
		self.assertEqual(88, len(detected))

	def test_detect_GEO_ZIP_on_311_Incident_Zip(self):
		detected = TypeDetector.detect_zip(self.database_311['Incident Zip'])[1]
		self.assertEqual(100, len(detected))

	def test_detect_GEO_ZIP_on_2j7x_tvss_Incident_Zip(self):
		detected = TypeDetector.detect_zip(self.database_2j7x_tvss['Incident Zip'])[1]
		self.assertEqual(98, len(detected))

	def test_detect_GEO_ZIP_on_database_26ze_s5bx_Inmate_Population(self):
		detected = TypeDetector.detect_zip(self.database_26ze_s5bx['Inmate Population'])[1]
		self.assertEqual(4, len(detected))
		# 4 elements hit valid values for zip codes. =/

	# --------------------------------------------------------------------------- detect single type: GEO_GPS
	def test_detect_GEO_GPS_latlon_on_h9gi_nx95_LATITUDE(self):
		detected = TypeDetector.detect_from_regex(TypeDetector.DETECTOR_GEO_GPS_LAT_OR_LON, self.database_NYPD_MVC.LATITUDE)[1]
		self.assertEqual(284646, len(detected))

	def test_detect_GEO_GPS_latlon_on_h9gi_nx95_LATITUDE(self):
		detected = TypeDetector.detect_from_regex(TypeDetector.DETECTOR_GEO_GPS_LAT_OR_LON, self.database_NYPD_MVC.LATITUDE)[1]
		self.assertEqual(88, len(detected))

	# --------------------------------------------------------------------------- detect single type: NUMERIC_INTEGER
	def test_detect_NUMBERIC_INTEGER_on_h9gi_nx95_Unique_key(self):
		expected_type = TypeDetector.DETECTOR_NUMERIC_INT
		detected = TypeDetector.detect_from_regex(expected_type, self.database_NYPD_MVC['Unique Key'])[1]
		self.assertEqual(100, len(detected))

	# --------------------------------------------------------------------------- detect single type: NUMERIC_DOUBLE
	def test_detect_NUMBERIC_DOUBLE_on_h9gi_nx95_LATITUDE(self):
		expected_type = TypeDetector.DETECTOR_NUMERIC_DOUBLE
		detected = TypeDetector.detect_from_regex(expected_type, self.database_NYPD_MVC.LATITUDE)[1]
		self.assertEqual(88, len(detected))

	# --------------------------------------------------------------------------- Data Types
	def test_is_address_with_valid_address(self):
		example = '1 metrotech center, brooklyn NY. 11201'
		result = TypeDetector.is_us_address(example)
		self.assertEqual(True, result)

	def test_is_address_with_invalid_address(self):
		example = '7th avenue'
		result = TypeDetector.is_us_address(example)
		self.assertEqual(False, result)

	def test_is_address_with_integer(self):
		example = '1'
		result = TypeDetector.is_us_address(example)
		self.assertEqual(False, result)

	def test_is_address_with_phone_number(self):
		example = '+1 6469970539'
		result = TypeDetector.is_us_address(example)
		self.assertEqual(False, result)

	def test_is_address_with_zip_code(self):
		example = '11209'
		result = TypeDetector.is_us_address(example)
		self.assertEqual(False, result)

	def test_detect_types_of_h9gi_nx95_LATITUDE_has_no_geo_zip(self):
		types = TypeDetector.types_of(self.database_NYPD_MVC.LATITUDE)
		self.assertEqual(0, types[TypeDetector.GEO_ZIP])

	def test_detect_types_of_h9gi_nx95_LATITUDE_has_geo_GPS_latlon(self):
		detected, not_detected, type_name = TypeDetector.detect_type(TypeDetector.DETECTOR_GEO_GPS_LAT_OR_LON, TypeDetector.STATIC_DETECTORS, self.database_NYPD_MVC.LATITUDE)
		self.assertEqual(TypeDetector.GEO_GPS_LATLON, type_name)
		self.assertGreater(len(detected), 0, '{} should be greatere than 0'.format(len(detected)))

	def test_detect_types_of_h9gi_nx95_LATITUDE_has_null(self):
		types = TypeDetector.types_of(self.database_NYPD_MVC.LATITUDE)
		self.assertEqual(12.0, types[TypeDetector.NULL])

	def test_simplify(self):
		type_counts = {
			TypeDetector.GEO_GPS: 1,
			TypeDetector.GEO_ZIP: 2,
			TypeDetector.GEO_BOROUGH: 3,
			TypeDetector.TEMPORAL_DATE: 4,
			TypeDetector.TEMPORAL_TIME: 5,
			TypeDetector.NUMERIC_INT: 6,
			TypeDetector.NUMERIC_DOUBLE: 7,
			TypeDetector.TEXTUAL: 8,
			TypeDetector.NULL: 0
		}
		correct_simple_type_counts = {
			TypeDetector.GEO: 6,
			TypeDetector.TEMPORAL: 9,
			TypeDetector.NUMERIC: 13,
			TypeDetector.TEXTUAL: 8,
			TypeDetector.NULL: 0
		}
		simple_type_counts = TypeDetector.simplify(type_counts)
		self.assertEqual(correct_simple_type_counts, simple_type_counts)

	def test_simple_type_should_return_GEO(self):
		self.type_counts[TypeDetector.GEO_ZIP] = 1
		simple_type = TypeDetector.simple_type_of_considering_all(self.type_counts, '', column_name='latitude')
		self.assertEqual(TypeDetector.GEO, simple_type)

	def test_simple_type_should_return_TEMPORAL(self):
		self.type_counts[TypeDetector.TEMPORAL_DATE] = 2
		simple_type = TypeDetector.simple_type_of(self.type_counts)
		self.assertEqual(TypeDetector.TEMPORAL, simple_type)

	def test_simple_type_should_return_NUMERIC(self):
		self.type_counts[TypeDetector.TEMPORAL_DATE] = 1
		self.type_counts[TypeDetector.NUMERIC] = 2
		simple_type = TypeDetector.simple_type_of(self.type_counts)
		self.assertEqual(TypeDetector.NUMERIC, simple_type)

	def test_simple_type_should_return_TEXTUAL(self):
		self.type_counts[TypeDetector.TEXTUAL] = 2
		self.type_counts[TypeDetector.NUMERIC] = 1
		simple_type = TypeDetector.simple_type_of(self.type_counts)
		self.assertEqual(TypeDetector.TEXTUAL, simple_type)

	def test_simple_type_should_return_NULL_when_all_types_are_zero(self):
		simple_type = TypeDetector.simple_type_of(self.type_counts)
		self.assertEqual(TypeDetector.NULL, simple_type)

	# ========================================================================== is_temporal_name()
	def test_address_is_not_temporal_name(self):
		assert TypeDetector.is_temporal_name('address') is False

	def test_date_is_temporal_name(self):
		assert TypeDetector.is_temporal_name('date')

		# ========================================================================== is_zipcode_name()

	def test_Unique_Key_is_not_gps_name(self):
		assert TypeDetector.is_zipcode_name('Unique Key') is False

	def test_ZIP_is_zip_code_name(self):
		assert TypeDetector.is_zipcode_name('ZIP')

	def test_zip_is_zip_code_name(self):
		assert TypeDetector.is_zipcode_name('zip')

	# ========================================================================== is_gps_name()
	def test_Unique_Key_is_not_gps_name(self):
		assert TypeDetector.is_gps_name('Unique Key') is False

	def test_latitude_is_gps_name(self):
		assert TypeDetector.is_gps_name('latitude')

	def test_LATITUDE_is_gps_name(self):
		assert TypeDetector.is_gps_name('LATITUDE')

	def test_LONGITUDE_is_gps_name(self):
		assert TypeDetector.is_gps_name('LONGITUDE')

	def test_LOCATION_is_gps_name(self):
		assert TypeDetector.is_gps_name('LOCATION')

	def test_ZIP_is_gps_name(self):
		assert TypeDetector.is_gps_name('ZIP') is False


if __name__ == '__main__':
	unittest.main()
