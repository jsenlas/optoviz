# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='optoviz',
    version='0.0.0',
    description='Visualizer for spectrum data from optical cables',
    long_description=readme,
    author='Jakub Sencak',
    author_email='xsenca00@vut.cz',
    url='https://github.com/jsenlas/optoviz',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

