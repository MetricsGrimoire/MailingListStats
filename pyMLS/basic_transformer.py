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
   Python: basic_transformer
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from utils import *
from transformer import transformer


class basic_transformer(transformer):

    def __init__(self, config_object, output_directory=""):
        self.config = config_object
        self.output_directory = output_directory
        self.m_connection = None
        # Data about most active project 
        self.most_active_project               = ''
        self.most_active_project_messages      = 0
        self.most_active_project_mailing_lists = 0
        self.most_active_project_people        = 0
        self.most_active_project_files         = 0

                  
    def announce(self, data):
        # Creando una conexion a la base de datos
        database = data[1]
        try:
            self.m_connection = connect (host   = self.config.get_value('database_server'),
                                         user   = self.config.get_value('database_user'),
                                         passwd = self.config.get_value('database_password'),
                                         db     = database)
        except:
            print "basic_transformer->ERROR: Database connection failed: "+database
            return

        number_files = 0
        number_mailing_lists = 0
        number_messages = 0
        number_people = 0

        cursor = self.m_connection.cursor()
        cursor.execute("SELECT count(*) FROM compressed_files ")
        result_set = cursor.fetchall()
        for row in result_set:
            number_files = int(row[0])
        cursor.close()

        cursor = self.m_connection.cursor()
        cursor.execute("SELECT count(*) FROM mailing_lists ")
        result_set = cursor.fetchall()
        for row in result_set:
            number_mailing_lists = int(row[0])
        cursor.close()

        cursor = self.m_connection.cursor()
        cursor.execute("SELECT count(*) FROM messages ")
        result_set = cursor.fetchall()
        for row in result_set:
            number_messages = int(row[0])
        cursor.close()

        cursor = self.m_connection.cursor()
        cursor.execute("SELECT count(*) FROM people ")
        result_set = cursor.fetchall()
        for row in result_set:
            number_people = int(row[0])
        cursor.close()
        
        print
        print "-------------------------------------------------------------"
        print "                 Database : "+ database
        print "-------------------------------------------------------------"
        print " - Files         : " + str(number_files)
        print " - Mailing Lists : " + str(number_mailing_lists)
        print " - Messages      : " + str(number_messages)
        print " - People        : " + str(number_people)
        print "-------------------------------------------------------------"
        print

        if (number_messages > self.most_active_project_messages):
            # Se comprueba si este proyecto es el mas activo de todos los mirados
            self.most_active_project               = database.replace('mailingliststat_','')
            self.most_active_project_messages      = number_messages
            self.most_active_project_mailing_lists = number_mailing_lists
            self.most_active_project_people        = number_people
            self.most_active_project_files         = number_files




        
    def finish (self):
      
        print "\n\n\n"
        print "-------------------------------------------------------------"
        print "       Most Active Project : "+self.most_active_project
        print "-------------------------------------------------------------"
        print " - Files         : " + str(self.most_active_project_files)
        print " - Mailing Lists : " + str(self.most_active_project_mailing_lists)
        print " - Messages      : " + str(self.most_active_project_messages)
        print " - People        : " + str(self.most_active_project_people)
        print "-------------------------------------------------------------"
        print "\n\n\n"
        print "   - basic_transformer Finished"
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
    print "** UNITY TEST: basic_transformer.py **"
    a_config = test_config_object()
    a = basic_transformer(a_config)
    a.announce(['/','mailingliststat_arrakis'])
    a.finish()

if __name__ == "__main__":
    test()

