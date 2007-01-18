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
   Python: config_parser
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from parser import *

class config_parser(parser):

    def __init__(self):
        #Constructor de la clase madre:
        parser.__init__(self)
        #Propiedades:
        self.result = {}
        #Cadenas de tokens que debe reconocer nuestro parser.
        self.load_expression(r"#.",  self.process_comment)
        self.load_expression(".+=.", self.process_key)
        self.load_expression(".+=", self.process_empty_key)


    def process_comment (self, text):
        #print "procesado comentario: "+text
        None




    def process_key (self, text):
        text = text.replace("\n","")
        text = text.replace("\t","")
        text = text.replace('"',"")
        text = text.replace("'","")
        text = text.strip(" ")
        parameter = text.split("=")
        #print "procesada clave-valor: ",parameter
        self.result[parameter[0]] = parameter[1]


    def process_empty_key (self, text):
        text = text.replace("\n","")
        text = text.replace("\t","")
        text = text.replace('"',"")
        text = text.replace("'","")
        text = text.strip(" ")
        text = text.replace("=","")
        #print "procesada clave-valor: ",parameter
        self.result[text] = ""

        

    def get_result(self):
        return self.result


    def finish(self):
        #Para este parser no se hace nada
        None



#---------------------- UNIT TESTS ----------------------

def test():
    print "** UNIT TEST: config_parser.py **"
    a = config_parser()
    a.match_file("MailingListStat.conf")
    

if __name__ == "__main__":
    test()


