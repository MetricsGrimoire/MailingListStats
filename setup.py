#!/usr/bin/python
#-*- coding:utf-8 -*-
# 
# Copyright (C) 2007-2010 Libresoft Research Group
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.m 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Authors : Israel Herraiz <herraiz@gsyc.escet.urjc.es>
# Authors : Germán Poo-Caamaño <gpoo@gnome.org>

"""
Installer

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      herraiz@gsyc.escet.urjc.es
"""


import sys
from setuptools import setup
from pymlstats.version import mlstats_version

# Dirty trick to allow installing the man page, making setuptools behave
# like distutils. Uncomment the following if you would like that behavior.
# sys.argv += ['--single-version-externally-managed', '--record=mlstats.txt']

extra = {}
# Not exactly Python3-ready...
if sys.version_info >= (3,):
    extra['use_2to3'] = True

README = open('README.md').read()

setup(
    name='mlstats',
    version=mlstats_version,
    author='Libresoft Research Group',
    author_email='metrics-grimoire@lists.libresoft.es',
    description='Mailing lists analysis tool of the Metrics Grimoire suite.',
    long_description=README,
    license='GNU GPL 2 or any later version',
    url='http://metricsgrimoire.github.io/MailingListStats/',
    platforms = ['any'],
    packages = ['pymlstats', 'pymlstats.backends'],
    scripts = ['mlstats'],
    data_files = [('share/man/man1',['man/mlstats.1'])],
    test_suite = 'pymlstats.tests',
    extras_require = {
        'mysql': ['MySQL-python'],
        'postgres': ['psycopg2']
    },
    **extra
)
