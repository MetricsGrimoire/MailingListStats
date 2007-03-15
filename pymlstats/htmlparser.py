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
# Authors :
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>

"""
This module contains a basic HTML parser. It reads the HTML code and will
return a list with all the links contained in the web page.

@authors:      Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      herraiz@gsyc.escet.urjc.es
"""

import htmllib
import formatter

class MyHTMLParser(htmllib.HTMLParser):

    def __init__(self,verbose=0):

        f = formatter.NullFormatter()

        self.links = []

        htmllib.HTMLParser.__init__(self,f,verbose)

    def anchor_bgn(self, href, name, type):
        self.save_bgn()

        if not href in self.links:
            self.links.append(href)
