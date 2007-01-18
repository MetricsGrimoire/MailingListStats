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
   Python: dump_db_transformer
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from utils import *
from transformer import transformer
import os

class dump_db_transformer(transformer):

    def __init__(self, config_object, output_directory=""):
        self.config = config_object

                  
    def announce(self, data):
        # El dato recibido es una lista que guarda:
        #  [path_donde_guardar_resultados, base_de_datos]
        database    = data[1]
        result_path = data[0]
        if result_path == '':
            result_path = os.getcwd()
        try:
            if self.config.get_value('database_password') == '':
                os.system('mysqldump -u '+self.config.get_value('database_user')+\
                        '  '+database+' | gzip > '+result_path+'/'+database+'.sql.gz')
            else:
                os.system('mysqldump -u '+self.config.get_value('database_user')+\
                        ' -p'+self.config.get_value('database_password')+\
                        '  '+database+' | gzip > '+result_path+'/'+database+'.sql.gz')
        except:
            print "dump_db_transformer->ERROR: error in mysqldump or in gzip: "+database
            return
        print "        Generated Database "+database+" dump."



        
    def finish (self):
        print "   - dump_db_transformer Finished"
        return

        
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
    print "** UNITY TEST: dump_db_transformer.py **"
    a_config = test_config_object()
    a = dump_db_transformer(a_config)
    a.announce(['/home/jgascon','mailingliststat_arrakis'])
    a.finish()

if __name__ == "__main__":
    test()

