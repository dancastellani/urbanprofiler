.PHONY: clean

.DEFAULT:
	make test

test: green-test

unittest: clean
	PYTHONPATH=urban_profiler/:test/src python -m unittest discover test/src/ -v

green-test: clean
	cd test/src && PYTHONPATH=../../urban_profiler green -vvr

nose-test: clean
	PYTHONPATH='urban_profiler/' nosetests test/src/ --exe -vv --rednose

clean:
	@find . -name "*.pyc" -type f -delete
	@echo "*.pyc removed."
	python setup.py clean
	rm -rf dist/ build/ urbanprofiler.egg-info/

install:
	pip install -r requirements.txt

#	CONDA_VERSION=$(shell pwd )
#	@echo Version of Anaconda should be 2.0.1. Run 'conda --version' to check.

egg-dist: clean
	python setup.py -q bdist_egg

egg-install:
	python setup.py -q install

egg-uninstall:
	pip uninstall urbanprofiler -y || echo "Uninstalled"

egg-reinstall: egg-uninstall egg-install

SPARK_PARAMS = --packages com.databricks:spark-csv_2.11:1.4.0 --py-files=dist/urbanprofiler-1.0-py2.7.egg --files urban_profiler/resources/zip_codes.csv,urban_profiler/resources/address_suffix.csv,urban_profiler/resources/zipcode_lat_lon.csv,urban_profiler/resources/nyc_pluto_prepared.csv,urban_profiler/resources/types_to_detect.csv

pyspark: egg-dist
	pyspark $(SPARK_PARAMS)

spark-test-prepare:
	hadoop fs -rm -r -f spark-test
	mkdir -p spark-test
	rm -rf spark-test/*

spark-test: egg-dist spark-test-prepare
	spark-submit $(SPARK_PARAMS) urban_profiler/spark/main.py
	hadoop fs -getmerge spark-test/erm2-nwe9-result/* spark-test/result

spark-check-logs:
	yarn logs -appOwner dancastellani -applicationId $(id)
