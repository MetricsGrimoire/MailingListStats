#!/usr/bin/env python

# Copyright (C) 2006 Jorge Gascon Perez
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
# Authors : Jorge Gascon <jgascon@gsyc.escet.urjc.es>


'''
Generic transformer, all your transformers have to
inherit from this class.
'''

class transformer:

    def __init__(self, output_directory=""):
        print "__init__: Not implemented in 'transformer' class"
        
        
    def announce(self, data):
        print "announce: Not implemented in 'transformer' class"
        
    def finish (self):
        print "finish: Not implemented in 'transformer' class"


#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: transformer.py **"


if __name__ == "__main__":
    test()

