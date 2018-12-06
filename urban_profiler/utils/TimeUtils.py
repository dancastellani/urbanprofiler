# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 22, 2014 3:07:49 PM$"

import locale; 
import time;
import datetime, traceback, numpy
from dateutil import parser
from urban_profiler import ApplicationOptions as App
from urban_profiler import ApplicationConstants as Constants
import PandasUtils

EPOCH = datetime.datetime(1970,1,1)

def current_time_formated():
	locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') 
	return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

def datetime_from_str_date(string_date):
	try:
		if PandasUtils.is_valid(string_date): 
			# print '>>>', string_date, ' type:', type(string_date)
			parsed_date = parser.parse(string_date, fuzzy=True, default=EPOCH)
			return parsed_date
		else:	
			return Constants.MISSING_DATA_SYMBOL
	
	except:
		App.debug('ERROR CONVERTIN DATE FROM STRING: TimeUtils.datetime_from_str_date({0})'.format(string_date))
		return Constants.MISSING_DATA_SYMBOL
		raise

def epoch_from_str_date(string_date):
	parsed_date = datetime_from_str_date(string_date)
	#This is not a proper date
	if parsed_date in [EPOCH, Constants.MISSING_DATA_SYMBOL]: return Constants.MISSING_DATA_SYMBOL

	return int((parsed_date - EPOCH).total_seconds())

def join_date_and_time(date_str, time_str):
	return date_str + ' ' + time_str

def date_from_str_date(string_date):
	datetime = datetime_from_str_date(string_date)
	return datetime.date() if datetime else datetime

