#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from codecs import open as fopen
from os.path import dirname, abspath, join
from setuptools import setup, find_packages

from hdlcontroller.version import VERSION

DIR = dirname(abspath(__file__))

with fopen(join(DIR, 'README.rst'), encoding='utf-8') as f:
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
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    packages = find_packages(),
    scripts = ['bin/hdlc_test'],
    test_suite = 'test',
    install_requires = [
        'python4yahdlc >= 1.1.0',
        'pyserial >= 3.0'
    ],
    extras_require = {
        'docs': [
            'sphinx >= 1.4.0',
            'sphinxcontrib-seqdiag >= 0.8.5',
            'sphinx-argparse >= 0.2.2',
            'sphinx_rtd_theme',
        ],
    },
)
