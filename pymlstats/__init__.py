# -*- coding:utf-8 -*-
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02111-1301, USA.
#
# Authors : Israel Herraiz <herraiz@gsyc.escet.urjc.es>

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
import getopt
import os
from main import Application
from version import mlstats_version

# Some stuff about the project
author = "(C) 2007-2010 %s <%s>" % \
         ("Libresoft", "libresoft-tools-devel@lists.morfeo-project.org")
name = "mlstats %s - Libresoft Research Group http://libresoft.es" % \
       mlstats_version
credits = "%s\n%s\n" % (name, author)


def usage():
    print credits
    print "Usage: %s [options] [URL1] [URL2] ... [URLn]" % (sys.argv[0])
    print """
    where URL1, URL2, ...., URLn are the urls of the archive web pages
    of the mailing list. If they are a local dir instead of a remote URL,
    the directory will be recursively scanned for mbox files.
    If the option \"-\" is passed instead of a URL(s), the URLs will be
    read from the standard input.

General options:

  -h, --help        Print this usage message.
  -q, --quiet       Do not show messages about the progress in the
                    retrieval and analysis of the archives.
                    Environment variable "MLSTATS_QUIET"
  --version         Show the version number and exit.
  --force           Force mlstats to download and parse any link found
                    in a given URL (only valid for remote links, neither
                    Gmane links nor local files).
                    Environment variable "MLSTATS_FORCE"
  -                 Read URLs from the standard input. This will ignore
                    all the URLs passed via the command line.
  --compressed-dir  Path to a folder where the archives of the mailing
                    list will be stored.
                    Environment variable "MLSTATS_COMPRESSED_DIR"


Report options:

  --report-file     Filename for the report generated after the analysis
                    (default is standard output)
                    WARNING: The report file will be overwritten if
                    already exists.
                    Environment variable "MLSTATS_REPORT_FILENAME"
  --no-report       Do not generate a report after the retrieval and
                    parsing of the archives.
                    Environment variable "MLSTATS_REPORT"


Private archives options:

  --web-user        If the archives of the mailing list are private, use
                    this username to login in order to retrieve the files.
                    Environment variable "MLSTATS_WEB_USERNAME"
  --web-password    If the archives of the mailing list are private, use
                    this password to login in order to retrieve the files.
                    Environment variable "MLSTATS_WEB_PASSWORD"

Database options:

  --db-driver          Database backend: mysql, postgres, or sqlite
                       (default is mysql)
                       Environment variable "MLSTATS_DB_DRIVER"
  --db-user            Username to connect to the database
                       (default is operator)
                       Environment variable "MLSTATS_DB_USERNAME"
  --db-password        Password to connect to the database
                       (default is operator)
                       Environment variable "MLSTATS_DB_PASSWORD"
  --db-name            Name of the database that contains data previously
                       analyzed (default is mlstats)
                       Environment variable "MLSTATS_DB_NAME"
  --db-hostname        Name of the host with a database server running
                       (default is localhost)
                       Environment variable "MLSTATS_DB_HOSTNAME"
"""


def start():
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hq"
    # short_opts = "h:t:b:r:l:n:p:d:s:i:r"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help",
                 "db-driver=", "db-user=", "db-password=", "db-hostname=",
                 "db-name=", "report-file=", "no-report", "version",
                 "quiet", "force", "web-user=", "web-password=",
                 "compressed-dir="]

    # Default options
    db_driver = os.getenv('MLSTATS_DB_DRIVER', 'mysql')
    db_user = os.getenv('MLSTATS_DB_USERNAME', None)
    db_password = os.getenv('MLSTATS_DB_PASSWORD', None)
    db_hostname = os.getenv('MLSTATS_DB_HOSTNAME', None)
    db_name = os.getenv('MLSTATS_DB_NAME', 'mlstats')
    web_user = os.getenv('MLSTATS_WEB_USERNAME', None)
    web_password = os.getenv('MLSTATS_WEB_PASSWORD', None)
    compressed_dir = os.getenv('MLSTATS_COMPRESSED_DIR', None)
    report_filename = os.getenv('MLSTATS_REPORT_FILENAME', '')
    report = os.getenv('MLSTATS_REPORT', True)
    quiet = os.getenv('MLSTATS_QUIET', False)
    force = os.getenv('MLSTATS_FORCE', False)
    urls = ''

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError, (msg, opt):
        print >>sys.stderr, msg
        usage()
        sys.exit(2)

    urls = args
    if "-" in args:
        # Read URLs from standard input instead of command line
        urls = [url.rstrip('\n').rstrip('\t') for url in sys.stdin.readlines()]

    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif "--db-driver" == opt:
            db_driver = value
        elif "--db-user" == opt:
            db_user = value
        elif "--db-password" == opt:
            db_password = value
        elif "--db-hostname" == opt:
            db_hostname = value
        elif "--db-name" == opt:
            db_name = value
        elif "--report-file" == opt:
            report_filename = value
        elif "--no-report" == opt:
            report = False
        elif opt in ("-q", "--quiet"):
            quiet = True
        elif "--force" == opt:
            force = True
        elif "--web-user" == opt:
            web_user = value
        elif "--web-password" == opt:
            web_password = value
        elif "--compressed-dir" == opt:
            compressed_dir = value.rstrip(os.path.sep)
        elif "--version" == opt:
            print mlstats_version
            sys.exit(0)

    myapp = Application(db_driver, db_user, db_password, db_name,
                        db_hostname, urls, report_filename, report,
                        quiet, force, web_user, web_password, compressed_dir)
