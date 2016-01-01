#!/usr/bin/env python3

from setuptools import setup

setup(
	name = 'hdlcontroller',
	version = '0.1.0',
	description = 'HDLC controller',
	license = 'MIT',
	keywords = 'hdlc',
	author = 'Paul-Emmanuel Raoul',
	author_email = 'skyper@skyplabs.net',
	url = 'https://github.com/SkypLabs/python-hdlc-controller',
	py_modules = ['hdlcontroller'],
	install_requires = ['python4yahdlc>=1.0.0'],
	test_suite = 'test',
)
