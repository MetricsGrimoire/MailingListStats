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
   Python: libresoft_big_database_transformer
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from utils import *
from transformer import transformer
import os

class libresoft_big_database_transformer(transformer):

    def __init__(self, config_object, output_directory=""):
        self.config = config_object
        self.libresoft_connection = None
        self.local_connection = None
        try:
            self.libresoft_connection = \
                connect (host   = self.config.get_value('libresoft_big_database_host'),
                         user   = self.config.get_value('libresoft_big_database_user'),
                         passwd = self.config.get_value('libresoft_big_database_password'),
                         db     = self.config.get_value('libresoft_big_database_database'))
        except Error, e:
            print "Error in libresoft_big_database_transformer: %d: %s" % (e.args[0], e.args[1])

        


    def announce(self, data):
        # El dato recibido es una lista que guarda:
        #  [path_donde_guardar_resultados, base_de_datos]
        result_path  = data[0]
        database     = data[1]
        project_name = database.replace('mailingliststat_','')
        # Conectando a la base de datos local.
        self.local_connection = connect(host   = self.config.get_value('database_server'),\
                                        user   = self.config.get_value('database_user'),\
                                        passwd = self.config.get_value('database_password'),\
                                        db     = database)

        # Cogemos el numero de mensajes
        cursor = self.local_connection.cursor()
        cursor.execute("SELECT count(*) FROM messages")
        result_set = cursor.fetchall()
        number_messages = result_set[0][0]
        cursor.close()
        
        # Ahora hay que introducir por la "libresoft_connection" los datos del
        # proyecto (dentro de la tabla "projects").
        libresoft_cursor = self.libresoft_connection.cursor()
        libresoft_cursor.execute("INSERT IGNORE INTO projects "+\
                                 "(project_name) VALUES ('"+\
                                 project_name+"')")

        libresoft_cursor.close()
        # Se coge el project_id de este proyecto que estamos mirando
        libresoft_cursor = self.libresoft_connection.cursor()
        libresoft_cursor.execute("SELECT id FROM projects "+\
                                 "WHERE project_name='"+project_name+"'")
        result_set = libresoft_cursor.fetchone()
        project_id = result_set[0]
        libresoft_cursor.close()

        # Se introduce el numero de mensajes
        libresoft_cursor = self.libresoft_connection.cursor()
        libresoft_cursor.execute("UPDATE projects SET total_messages="+\
                                 str(number_messages)+\
                                 " WHERE project_name = '"+project_name+"'")
        libresoft_cursor.close()

        # Ahora cogemos cada una de las personas y los mensajes
        # en los que ha participado.
        cursor = self.local_connection.cursor()
        cursor.execute(" SELECT email_address, count(email_address) "+\
                       " FROM messages_people "+\
                       " GROUP BY email_address;")
        result_set = cursor.fetchall()
        for row in result_set:
            email_address = row[0]
            messages_sent = row[1]
            libresoft_cursor = self.libresoft_connection.cursor()
            libresoft_cursor.execute("INSERT IGNORE INTO mls_data "+\
            " (author_email, messages_sent, project_name, project_id) "+\
            " VALUES ('"+email_address+"',"+str(messages_sent)+",'"+\
                     project_name+"',"+str(project_id)+")")
            libresoft_cursor.close()
        cursor.close()
        self.finalize_local_connection()

        

    def finish (self):
        self.finalize_libresoft_connection()
        print "   - libresoft_big_database_transformer Finished"
        return



    def finalize_libresoft_connection (self):
        self.libresoft_connection.commit()
        self.libresoft_connection.close()
        self.libresoft_connection = None



    def finalize_local_connection (self):
        self.local_connection.commit()
        self.local_connection.close()
        self.local_connection = None


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
    print "** UNITY TEST: libresoft_big_database_transformer.py **"
    a_config = test_config_object()
    a = libresoft_big_database_transformer(a_config)
    a.announce(['/home/jgascon','mailingliststat_arrakis'])
    a.finish()

if __name__ == "__main__":
    test()

