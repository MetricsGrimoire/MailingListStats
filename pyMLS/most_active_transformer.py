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
   Python: most_active_transformer
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from utils import *
from transformer import transformer
import os, datetime

class most_active_transformer(transformer):

    def __init__(self, config_object, output_directory=""):
        self.config = config_object
        self.number_most_active_people = self.config.get_value('number_most_active_developers')
        if self.number_most_active_people == "":
            self.number_most_active_people = 5


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
        f = open(result_path+'/Most_active_developers_'+project_name+".txt",'w')

        cursor = self.m_connection.cursor()
        cursor.execute("SELECT count(*) FROM messages")
        result_set = cursor.fetchall()
        number_messages = result_set[0][0]
        cursor.close()
        
        cursor = self.m_connection.cursor()
        cursor.execute("SELECT DISTINCT count(email_address),email_address "+\
                       "FROM messages_people GROUP BY email_address "+\
                       "ORDER BY count(email_address) DESC;")
        result_set = cursor.fetchall()

        # Consiguiendo solamente los desarrolladores mas activos.
        if '%' in self.number_most_active_people:
            self.number_most_active_people = int(self.number_most_active_people.replace('%',''))
            self.number_most_active_people = int(cursor.rowcount * self.number_most_active_people / 100)
        else:
            self.number_most_active_people = int(self.number_most_active_people)

        f.write("\n")
        f.write("        Most "+str(self.number_most_active_people)+" Active People at "+project_name+" project\n")
        f.write("-----------------------------------------------------------------------\n\n")
        f.write("Total "+str(number_messages)+" messages at "+str(datetime.date.today())+"\n\n")
        
        for row in result_set:
            number = row[0]
            email = row[1]
            f.write('   %3d ' % number + ' (%6.2f' % (float(number)/float(number_messages)*100.0) + '%)')
            f.write(' '+email+'\n')
            self.number_most_active_people -= 1
            if self.number_most_active_people == 0:
                break
            
        f.close()
        cursor.close()
        self.finalize_connection()
        print "        Generated Most active developers of "+project_name




    def finish (self):
        print "   - most_active_transformer Finished"
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
    print "** UNITY TEST: most_active_transformer.py **"
    a_config = test_config_object()
    a = most_active_transformer(a_config)
    a.announce(['/home/jgascon','mailingliststat_arrakis'])
    a.finish()

if __name__ == "__main__":
    test()

