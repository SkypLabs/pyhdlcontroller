#!/usr/bin/env python3

from setuptools import setup

VERSION = '0.2.0'

setup(
	name = 'hdlcontroller',
	version = VERSION,
	description = 'HDLC controller',
	license = 'MIT',
	keywords = 'hdlc',
	author = 'Paul-Emmanuel Raoul',
	author_email = 'skyper@skyplabs.net',
	url = 'https://github.com/SkypLabs/python-hdlc-controller',
	download_url = 'https://github.com/SkypLabs/python-hdlc-controller/archive/v{0}.zip'.format(VERSION),
	setup_requires = ['setuptools-markdown'],
	long_description_markdown_filename = 'README.md',
	py_modules = ['hdlcontroller'],
	scripts = ['hdlcontroller.py'],
	install_requires = ['python4yahdlc>=1.0.2', 'pyserial'],
	test_suite = 'test',
)
