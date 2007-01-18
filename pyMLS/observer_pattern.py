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
   Python: observer_pattern
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''



class observer_pattern:

    def __init__(self):
        self.observers = []

        
    def subscribe (self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

        
    def unsubscribe (self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

            
    def announce (self, data):
        for ob in self.observers:
            #try:
            ob.announce(data)
            #except:
            #    print "ERROR, a client does not have 'announce' method"

                
    def finish (self):
        for ob in self.observers:
            #try:
            ob.finish()
            #except:
            #    print "ERROR, a client does not have 'finish' method"



#---------------------- UNITY TESTS ----------------------

class mini_client:
    def __init__(self, number):
        self.m_number = number
    def announce(self, data):
        print "Hi, i am ",self.m_number,"th observer, received data is: ",data
    def finish(self):
        print "Oh! I am dying!"


def test():
    ob = observer_pattern()
    print "** UNITY TEST: observer_pattern.py **"
    print "Subscribing three clients"
    ob.subscribe ( mini_client(0) )
    a_client = mini_client(1)
    ob.subscribe ( a_client )
    ob.subscribe ( mini_client(2) )
    ob.announce("Bang! Bang!")
    print "Unsubscribing second client"
    ob.unsubscribe ( a_client )
    ob.announce("Bang! Bang!")
    print "Finishing"
    ob.finish()
        

if __name__ == "__main__":
    test()


  