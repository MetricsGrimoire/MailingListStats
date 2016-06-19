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
import urlparse
import urllib
import urllib2
import cStringIO
import gzip


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

        if href not in self.links:
            self.links.append(href)

    def get_links(self):
        htmltxt = fetch_remote_resource(self.url, self.user, self.password)
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

        return self.links


def fetch_remote_resource(url, user=None, password=None):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 ' \
                 '(KHTML, like Gecko) Ubuntu/11.04 Chromium/15.0.871.0 ' \
                 'Chrome/15.0.871.0 Safari/535.2'
    headers = {'User-Agent': user_agent,
               'Accept-Encoding': 'gzip, deflate'}

    postdata = None
    if user:
        postdata = urllib.urlencode({'username': user, 'password': password})

    request = urllib2.Request(url, postdata, headers)
    response = urllib2.urlopen(request)
    data = response.read()

    if response.info().getheader('content-encoding') == 'gzip':
        data = cStringIO.StringIO(data)
        content = gzip.GzipFile(mode='r', compresslevel=0,
                                fileobj=data).read()
    else:
        content = data

    response.close()

    return content
