#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
# Authors :
#       Jesus M. Gonzalez-Barahona <jgb@bitergia.com>

#
# get-gmane-mbix.py
#
# Simple script to get a mailing list from Gmane in mbox format
#
# Info about the Gmane download API:
#  http://gmane.org/export.php

import argparse
import os
from subprocess import call

# Location of MetricsGrimoire repositories
gmane = "http://download.gmane.org"

# Parse command line options
parser = argparse.ArgumentParser(description="""
Simple script to get a mailing list from Gmane in mbox format
""")
parser.add_argument("list",
                    help="Mailing list to download")
parser.add_argument("--last",
                    help="Number of last message to download")
parser.add_argument("--size",
                    help="Size of each batch (in number of messages")
parser.add_argument("--dir",
                    help="Directory to write mboxes (will be created if doesn't exist)")
args = parser.parse_args()

# Create and move to the installation directory
if not os.path.exists(args.dir):
    os.makedirs(args.dir)
os.chdir(args.dir)

lastMessage = int(args.last)
batchSize = int(args.size)

print (lastMessage - 1) / batchSize

for batch in range (((lastMessage - 1) / batchSize) + 1):
    print batch
    url = gmane + "/" + args.list + "/" + \
        str (batch * batchSize + 1) + "/" + \
        str((batch +1) * batchSize)
    print url
    call (["wget", "--directory-prefix=" + args.dir, url ])
