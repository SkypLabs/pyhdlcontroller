#!/usr/bin/env python3

from setuptools import setup
from os.path import dirname, abspath, join
from codecs import open

DIR = dirname(abspath(__file__))
VERSION = '0.3.1'

with open(join(DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'hdlcontroller',
    version = VERSION,
    description = 'HDLC controller',
    long_description = long_description,
    license = 'MIT',
    keywords = 'hdlc controller',
    author = 'Paul-Emmanuel Raoul',
    author_email = 'skyper@skyplabs.net',
    url = 'https://github.com/SkypLabs/python-hdlc-controller',
    download_url = 'https://github.com/SkypLabs/python-hdlc-controller/archive/v{0}.zip'.format(VERSION),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
    py_modules = ['hdlcontroller'],
    scripts = ['hdlcontroller.py'],
    install_requires = ['python4yahdlc>=1.0.2', 'pyserial'],
    test_suite = 'test',
)
