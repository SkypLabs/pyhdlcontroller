======================
Python HDLC Controller
======================

|PyPI Package| |PyPI Downloads| |PyPI Python Versions| |Build Status|
|Documentation Status|

HDLC_ controller written in Python and based on the `python4yahdlc
<https://github.com/SkypLabs/python4yahdlc>`__ Python module to encode and
decode the HDLC frames.

Installation
============

From PyPI (recommended)
-----------------------

::

    pip3 install --upgrade hdlcontroller

From sources
------------

::

    git clone https://github.com/SkypLabs/python-hdlc-controller.git
    cd python-hdlc-controller
    pip3 install --upgrade .

Documentation
=============

The full documentation is available `here
<https://python-hdlc-controller.readthedocs.io/en/latest/>`__.

License
=======

`MIT <https://opensource.org/license/mit/>`__

.. _HDLC: https://en.wikipedia.org/wiki/High-Level_Data_Link_Control

.. |Build Status| image:: https://github.com/SkypLabs/python-hdlc-controller/actions/workflows/test_and_publish.yml/badge.svg?branch=develop
   :target: https://github.com/SkypLabs/python-hdlc-controller/actions/workflows/test_and_publish.yml?branch=develop
   :alt: Build Status Develop Branch

.. |Documentation Status| image:: https://readthedocs.org/projects/python-hdlc-controller/badge/?version=latest
   :target: https://python-hdlc-controller.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. |PyPI Downloads| image:: https://img.shields.io/pypi/dm/hdlcontroller.svg?style=flat
   :target: https://pypi.org/project/hdlcontroller/
   :alt: PyPI Package Downloads Per Month

.. |PyPI Package| image:: https://badge.fury.io/py/hdlcontroller.svg
   :target: https://pypi.org/project/hdlcontroller/
   :alt: PyPI Package Latest Release

.. |PyPI Python Versions| image:: https://img.shields.io/pypi/pyversions/hdlcontroller.svg?logo=python&style=flat
   :target: https://pypi.org/project/hdlcontroller/
   :alt: PyPI Package Python Versions
