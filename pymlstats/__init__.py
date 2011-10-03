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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
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
import os
import time
import string
import stat
import getopt
from main import *
from version import mlstats_version

# Some stuff about the project
author = "(C) 2007-2010 %s <%s>" % ("Libresoft", "libresoft-tools-devel@lists.morfeo-project.org")
name = "mlstats %s - Libresoft Research Group http://libresoft.es" % mlstats_version
credits = "\n%s \n%s\n" % (name,author)

def usage ():
    print credits
    print "Usage: %s [options] [URL1] [URL2] ... [URLn]" % (sys.argv[0])
    print """
    where URL1, URL2, ...., URLn are the urls of the archive web pages of the mailing list.
    If they are a local dir instead of a remote url,
    the directory will be recursively scanned for mbox files.
    If the option \"-\" is passed instead of a URL(s), the URLs will be read from the standard input.
    
General options:

  -h, --help        Print this usage message.
  -q, --quiet       Do not show messages about the progress in the retrieval and analysis of the archives.
  --version         Show the version number and exit.
  -                 Read URLs from the standard input. This will ignore all the URLs passed via the command line.

Report options:

  --report-file     Filename for the report generated after the analysis  (default is standard output)
                    WARNING: The report file will be overwritten if already exists.
  --no-report       Do not generate report after the retrieval and parsing of the archives.


Private archives options:

  --web-user        If the archives of the mailing list are private, use this username to login in order to retrieve the files.
  --web-password    If the archives of the mailing list are private, use this password to login in order to retrieve the files.

Database options:

  --db-driver          Database backend: mysql or postgres (default is mysql)
  --db-user            Username to connect to the database (default is operator)
  --db-password        Password to connect to the database (default is operator)
  --db-name            Name of the database that contains data previously analyzed (default is mlstats)
  --db-hostname        Name of the host with a database server running (default is localhost)
  --db-admin-user      Username to create the mlstats database (default is root)
  --db-admin-password  Password to create the mlstats database (default is empty)
"""

def start():
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hq"
    #short_opts = "h:t:b:r:l:n:p:d:s:i:r"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help", "db-driver=", "db-user=", "db-password=", "db-hostname=", "db-name=","db-admin-user=","db-admin-password=","report-file=","no-report","version","quiet","web-user=","web-password="]

    # Default options
    db_driver = 'mysql'
    db_user = 'operator'
    db_password = 'operator'
    db_hostname = 'localhost'
    db_name = 'mlstats'
    db_admin_user = 'root'
    db_admin_password = ''
    web_user = None
    web_password = None
    report_filename = ''
    report = True
    quiet = False
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
        elif "--db-admin-user" == opt:
            db_admin_user = value
        elif "--db-admin-password" == opt:
            db_admin_password = value
        elif "--report-file" == opt:
            report_filename = value
        elif "--no-report" == opt:
            report = False
        elif opt in ("-q", "--quiet"):
            quiet = True
        elif "--web-user" == opt:
            web_user = value
        elif "--web-password" == opt:
            web_password = value
        elif "--version" == opt:
            print mlstats_version
            sys.exit(0)

    myapp = Application(db_driver, db_user, db_password, db_name,
                        db_hostname, db_admin_user, db_admin_password,
                        urls, report_filename, report, quiet,
                        web_user, web_password)
