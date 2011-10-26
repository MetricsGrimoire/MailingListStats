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

import htmllib
import urllib
import urllib2
import os
import formatter
import utils

class MyHTMLParser(htmllib.HTMLParser):


    def __init__(self, url, web_user = None, web_password = None, verbose=0):

        f = formatter.NullFormatter()

        self.url = url
        self.user = web_user
        self.password = web_password
        self.links = []
        self.mboxes_links = []

        htmllib.HTMLParser.__init__(self,f,verbose)

    def anchor_bgn(self, href, name, type):
        self.save_bgn()

        if not href in self.links:
            self.links.append(href)

    def get_mboxes_links(self):

        self.__get_html()
        
        # Ignore links with not recognized extension
        filtered_links = []
        for l in self.links:
            ext1 = os.path.splitext(l)[-1]
            ext2 = os.path.splitext(l.rstrip(ext1))[-1]

            accepted_types = utils.COMPRESSED_TYPES + utils.ACCEPTED_TYPES

            if ext1 in accepted_types or ext1+ext2 in accepted_types:
                filtered_links.append(os.path.join(self.url,l))

        self.mboxes_links = filtered_links

        return self.mboxes_links

    def __get_html(self):
        ''' Download index.html to a temp file '''

        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 ' \
                     '(KHTML, like Gecko) Ubuntu/11.04 Chromium/15.0.871.0 ' \
                     'Chrome/15.0.871.0 Safari/535.2'
        headers = { 'User-Agent': user_agent }
        postdata = None

        if self.user:
            postdata = urllib.urlencode({'username': self.user,
                                         'password': self.password})

        request = urllib2.Request(self.url, postdata, headers)
        response = urllib2.urlopen(request)

        htmltxt = response.read()
        response.close()

        self.feed(htmltxt) # Read links from HTML code
        self.close()
