# -*- coding:utf-8 -*-
# Copyright (C) 2007-2010 Libresoft Research Group
# Copyright (C) 2016 Germán Poo-Caamaño <gpoo@gnome.org>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02111-1301, USA.
#
# Authors : Israel Herraiz <herraiz@gsyc.escet.urjc.es>
# Authors : Germán Poo-Caamaño <gpoo@gnome.org>

"""
Usage and launch functions. Should not change unless command line
options are changed.

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import sys
import argparse
import os
from main import Application
from version import mlstats_version

name = 'mlstats - A tool to retrieve, parse and analyze archived mail boxes'


def start():
    args = argparse.ArgumentParser(description=name)

    args.add_argument('url', nargs='+',
                      help='Urls of the archive web pages of the mailing '
                           'list. If they are a local dir instead of a '
                           'remote URL, the directory will be recursively '
                           'scanned for mbox files. If the option \'-\' is '
                           'passed instead of a URL(s), the URLs will be '
                           'read from the standard input.')

    argen = args.add_argument_group('General options')
    argen.add_argument('-q', '--quiet', action='store_true',
                       default=os.getenv('MLSTATS_QUIET', False),
                       help='Do not show messages about the progress in the '
                            'retrieval and analysis of the archives.'
                            'Environment variable "MLSTATS_QUIET"')
    argen.add_argument('--version', action='version', version=mlstats_version,
                       help='Show the version number and exit.')
    argen.add_argument('--force', action='store_true',
                       default=os.getenv('MLSTATS_FORCE', False),
                       help='Force mlstats to download even the '
                            'mboxes/messages already found locally for a '
                            'given URL.  This option is only valid for remote '
                            'links. For Gmane links, it overrides the offset '
                            'value to 0.'
                            'Environment variable "MLSTATS_FORCE"')
    argen.add_argument('--compressed-dir',
                       default=os.getenv('MLSTATS_COMPRESSED_DIR', None),
                       help='Path to a folder where the archives of the '
                            'mailing list will be stored.'
                            'Environment variable "MLSTATS_COMPRESSED_DIR"'
                       )

    argrp = args.add_argument_group('Report options')
    argrp.add_argument('--report-file',
                       default=os.getenv('MLSTATS_REPORT_FILENAME', ''),
                       help='Filename for the report generated after the '
                            'analysis (default is standard output) WARNING: '
                            'The report file will be overwritten if already '
                            'exists.'
                            'Environment variable "MLSTATS_REPORT_FILENAME"')
    argrp.add_argument('--no-report', action='store_true',
                       default=os.getenv('MLSTATS_REPORT', True),
                       help='Do not generate a report after the retrieval '
                            'and parsing of the archives.'
                            'Environment variable "MLSTATS_REPORT"')

    argweb = args.add_argument_group('Private archive options')
    argweb.add_argument('--web-user',
                        default=os.getenv('MLSTATS_WEB_USERNAME', None),
                        help='If the archives of the mailing list are '
                             'private, use this username to login in order '
                             'to retrieve the files.'
                             'Environment variable "MLSTATS_WEB_USERNAME"')
    argweb.add_argument('--web-password',
                        default=os.getenv('MLSTATS_WEB_PASSWORD', None),
                        help='If the archives of the mailing list are '
                             'private, this password to login in order to '
                             'retrieve the files.'
                             'Environment variable "MLSTATS_WEB_PASSWORD"')

    argdb = args.add_argument_group('Database options')
    argdb.add_argument('--db-driver', default=os.getenv('MLSTATS_DB_DRIVER', 'mysql'),
                       help='Database backend: mysql, postgres, or sqlite '
                            '(default is mysql)'
                            'Environment variable "MLSTATS_DB_DRIVER"')
    argdb.add_argument('--db-user',
                       default=os.getenv('MLSTATS_DB_USERNAME', None),
                       help='Username to connect to the database'
                            'Environment variable "MLSTATS_DB_USERNAME"')
    argdb.add_argument('--db-password',
                       default=os.getenv('MLSTATS_DB_PASSWORD', None),
                       help='Password to connect to the database'
                            'Environment variable "MLSTATS_DB_PASSWORD"')
    argdb.add_argument('--db-name', default=os.getenv('MLSTATS_DB_NAME', 'mlstats'),
                       help='Name of the database that contains data '
                            'previously analyzed'
                            'Environment variable "MLSTATS_DB_NAME"')
    argdb.add_argument('--db-hostname',
                       default=os.getenv('MLSTATS_DB_HOSTNAME', None),
                       help='Name of the host with a database server running'
                            'Environment variable "MLSTATS_DB_HOSTNAME"')

    argbnd = args.add_argument_group('Backend options')
    argbnd.add_argument('--backend', default=os.getenv('MLSTATS_BACKEND', None),
                        help='Mailing list backend for remote repositories: '
                             'gmane, mailman, or webdirectory. (default is '
                             'autodetected for gmane and mailman)'
                             'Environment variable "MLSTATS_BACKEND"')
    argbnd.add_argument('--offset', default=os.getenv('MLSTATS_OFFSET', 0), type=int,
                        help='Start from a given message. Only works with the '
                             'gmane, backend. (default is 0) '
                             'Environment variable "MLSTATS_OFFSET"')

    opts = args.parse_args()

    if '-' in opts.url:
        # Read URLs from standard input instead of command line
        urls = [url.strip() for url in sys.stdin.readlines()]
    else:
        urls = opts.url

    db_driver = opts.db_driver
    db_user = opts.db_user
    db_password = opts.db_password
    db_hostname = opts.db_hostname
    db_name = opts.db_name
    web_user = opts.web_user
    web_password = opts.web_password
    compressed_dir = opts.compressed_dir
    report_filename = opts.report_file
    report = not opts.no_report
    quiet = opts.quiet
    force = opts.force
    backend = opts.backend
    offset = opts.offset

    myapp = Application(db_driver, db_user, db_password, db_name,
                        db_hostname, urls, report_filename, report,
                        quiet, force, web_user, web_password, compressed_dir,
                        backend, offset)