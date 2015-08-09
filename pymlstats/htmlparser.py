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
# Authors :
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>

"""
This module contains a basic HTML parser. It reads the HTML code and will
return a list with all the links contained in the web page.

@authors:      Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import formatter
import htmllib
import os
import urlparse
import utils


MOD_MBOX_THREAD_STR = "/thread"


class MyHTMLParser(htmllib.HTMLParser):
    def __init__(self, url, web_user=None, web_password=None, verbose=0):

        f = formatter.NullFormatter()

        self.url = url
        self.user = web_user
        self.password = web_password
        self.links = []
        self.mboxes_links = []

        htmllib.HTMLParser.__init__(self, f, verbose)

    def anchor_bgn(self, href, name, type):
        self.save_bgn()

        if not href in self.links:
            self.links.append(href)

    def get_mboxes_links(self, force=False):
        htmltxt = utils.fetch_remote_resource(self.url, self.user,
                                              self.password)

        scheme = urlparse.urlparse(self.url).scheme

        if scheme in ('ftp', 'ftps'):
            # FTP servers return a plain page that contains
            # the list of files on the directory. Each line
            # has the next pattern:
            #     -rw-r--r--  1  500  500  1799055  Sep 30  2013  mbox
            #
            # where 'mbox' is the file name.
            #
            lines = htmltxt.split('\r\n')
            self.links = [line.split()[-1] for line in lines if line]
        else:
            # Read links from HTML code. Links usually come sorted
            # from newest to oldest but we reverse the list to analyze
            # oldest first.
            self.feed(htmltxt)
            self.links.reverse()

        self.close()

        accepted_types = utils.COMPRESSED_TYPES + utils.ACCEPTED_TYPES

        filtered_links = []
        for l in self.links:
            if force:
                filtered_links.append(os.path.join(self.url, l))
            else:
                # Links from Apache's 'mod_mbox' plugin contain
                # trailing "/thread" substrings. Remove them to get
                # the links where mbox files are stored.
                if l.endswith(MOD_MBOX_THREAD_STR):
                    l = l[:-len(MOD_MBOX_THREAD_STR)]

                ext1 = os.path.splitext(l)[-1]
                ext2 = os.path.splitext(l.rstrip(ext1))[-1]

                # Ignore links with not recognized extension
                if ext1 in accepted_types or ext1+ext2 in accepted_types:
                    filtered_links.append(os.path.join(self.url, l))

        self.mboxes_links = filtered_links

        return self.mboxes_links
