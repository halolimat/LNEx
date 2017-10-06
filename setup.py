"""#############################################################################
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
#############################################################################"""

#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_file = f.read()

setup(
    name='LNEx',
    version='1.1',
    description='Location Name Extractor (LNEx): extracts location names from targeted text streams',
    long_description=readme,
    author='Hussein S. Al-Olimat',
    author_email='hussein@knoesis.org',
    url='https://github.com/halolimat/LNEx',
    license=license_file,
    packages=find_packages(exclude=('_Data')),
    package_data={'LNEx': ['_Dictionaries/*.txt']},
    install_requires=[
          'elasticsearch',
          'elasticsearch-dsl<2.0.0',
          'nltk',
          'geopy',
          'texttable',
          'wordsegment'
      ]
)
