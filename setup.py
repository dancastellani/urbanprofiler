import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "urbanprofiler",
    version = "1.0",
    author = "Daniel Castellani",
    author_email = "daniel.castellani@nyu.edu",
    description = ("Urban Data Profiler code"),
    license = "MIT",
    keywords = "urban data profiling cleaning curation",
    url = "https://gitlab.cusp.nyu.edu/urban-curation/urban-profiler",
    packages=['urban_profiler',
              'urban_profiler/profiler',
              'urban_profiler/utils',
              'urban_profiler/spark',
              ],
    excludes=['test'],
    long_description=read('README.md'),

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],

    install_requires=[
        'pandas'
    ],
	zip_safe = False,
    package_data={'urban_profiler/resources': ['urban_profiler/resources/address_suffix.csv'],
                  'urban_profiler/resources': ['urban_profiler/resources/zip_codes.csv']
                },
    include_package_data=True,
)