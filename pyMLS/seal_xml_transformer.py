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
   Python: seal_xml_transformer
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from utils import *
from transformer import transformer
import os

class seal_xml_transformer(transformer):

    def __init__(self, config_object, output_directory=""):
        self.config = config_object


    def announce(self, data):
        # El dato recibido es una lista que guarda:
        #  [path_donde_guardar_resultados, base_de_datos]
        result_path  = data[0]
        database     = data[1]
        project_name = database.replace('mailingliststat_','')
        if result_path == '':
            result_path = os.getcwd();
        # ----------- Abriendo la conexion con la base de datos -----------
        self.m_connection = connect(host   = self.config.get_value('database_server'),\
                                    user   = self.config.get_value('database_user'),\
                                    passwd = self.config.get_value('database_password'),\
                                    db     = database)
        # ----------- Creating xml data for Seal -------------------------- 
        f = open(result_path+'/'+project_name+'_for_seal.xml','w')
        f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
        f.write('<seal>\n')
        f.write('    <source type="Mailing List" project="'+project_name+'" url=""></source>\n')

        cursor = self.m_connection.cursor()
        cursor.execute("SELECT email_address, alias FROM people")
        result_set = cursor.fetchall()

        for row in result_set:
            email = row[0]
            alias = row[1]
            f.write('    <identity type="email" i="' + email +'"></identity>\n')
            f.write('    <identity type="realname" i="' + alias +'"></identity>\n')
            f.write('    <match id1="' + email + '" id2="' + alias + '" ev="flossworld"></match>\n')
        f.write('</seal>\n')
        f.close()
        self.finalize_connection()
        print "        Generated "+project_name+" XML for Seal."




    def finish (self):
        print "   - seal_xml_transformer Finished"
        return




    def finalize_connection (self):
        cursor = self.m_connection.cursor()
        cursor.execute("commit;")
        cursor.close()
        self.m_connection.close()
        self.m_connection = None


#---------------------- UNITY TESTS ----------------------

class test_config_object:
    def __init__(self):
        self.m_set = {}
        self.m_set['databases']         = ['mailingliststat_arrakis']
        self.m_set['database_server']   = 'localhost'
        self.m_set['database_user']     = 'operator'
        self.m_set['database_password'] = 'operator'

    def get_value(self, name):
        return self.m_set[name]



def test():
    print "** UNITY TEST: seal_xml_transformer.py **"
    a_config = test_config_object()
    a = seal_xml_transformer(a_config)
    a.announce(['/home/jgascon','mailingliststat_arrakis'])
    a.finish()

if __name__ == "__main__":
    test()

