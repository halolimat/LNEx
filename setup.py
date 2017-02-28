# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='LNEx',
    version='1',
    description='Location Name Extractor tool (LNEx): extracts location names from targeted text streams',
    long_description=readme,
    author='Hussein S. Al-Olimat',
    author_email='hussein@knoesis.org',
    url='https://github.com/halolimat/LNEx',
    license=license,
    packages=find_packages(exclude=('tests'))
)
