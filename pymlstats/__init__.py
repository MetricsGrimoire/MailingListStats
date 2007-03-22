# Copyright (C) 2007 Libresoft Research Group
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
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

# Some stuff about the project
author = "(C) 2007 %s <%s>" % ("Libresoft", "libresoft@gsyc.escet.urjc.es")
name = "mlstats %s - Libresoft Research Group http://libresoft.urjc.es" % ("0.3.2_beta1")
credits = "\n%s \n%s\n" % (name,author)

def usage ():
    print credits
    print "Usage: %s [options] [URL1] [URL2] ... [URLn]" % (sys.argv[0])
    print """
    where URL1, URL2, ...., URLn are the urls of the archive web pages of the mailing list.
    If they are a local dir instead of a remote url,
    the directory will be recursively scanned for mbox files.
    If the option \"-\" is passed instead of a URL(s), the URLs will be read from the standard input.
    
Options:

  -h, --help        Print this usage message.
  --report-file     Filename for the report generated after the analysis  (default is standard output)
                    WARNING: The report file will be overwritten if already exists.
  --no-report       Do not generate report after the retrieval and parsing of the archives
  -                 Read URLs from the standard input. This will ignore all the URLs passed via the command line.
  
  
MySQL database:

  --user            Username to connect to the database (default is operator)
  --password        Password to connect to the database (default is operator)
  --database        Database which contains data previously analyzed (default is mlstats)
  --hostname        Name of the host with a database server running (default is localhost)
  --admin-user      Username to create the mlstats database (default is root)
  --admin-password  Password to create the mlstats database (default is empty)

Examples:

$ mlstats --user=\"root\" --password=\"\" --no-report http://my.mailinglist.com/archives/ /home/user/some/mboxes/

  This will download all the archives from http://my.mailinglist.com/archives/, and will scan /home/user/some/mboxes/ searching for mboxes.

$ cat list_of_urls | mlstats --user=\"root\" --password=\"\" --no-report -

  This will take all the URLs (or local directories) in the file 'list_of_urls'. URLs can be in separated lines, or separated by spaces or tabs.

"""

def start():
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "h"
    #short_opts = "h:t:b:r:l:n:p:d:s:i:r"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help","user=", "password=", "hostname=", "database=","admin-user=","admin-password=","report-file=","no-report"]

    # Default options
    user = 'operator'
    password = 'operator'
    hostname = 'localhost'
    database = 'mlstats'
    admin_user = 'root'
    admin_password = ''
    report_filename = ''
    report = True
    urls = ''
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError, (msg, opt):
        print msg
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
        elif "--user" == opt:
            user = value
        elif "--password" == opt:
            password = value
        elif "--hostname" == opt:
            hostname = value
        elif "--database" == opt:
            database = value
        elif "--admin-user" == opt:
            admin_user = value
        elif "--admin-password" == opt:
            admin_password = value
        elif "--report-file" == opt:
            report_filename = value
        elif "--no-report" == opt:
            report = False
    
           
    myapp = Application(user,password,database,hostname,admin_user,admin_password,urls,report_filename,report)
            
