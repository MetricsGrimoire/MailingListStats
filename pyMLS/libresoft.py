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

# If you use another Database system, change "MySQLdb" by other database module
from MySQLdb import *

class libresoft (object):
    # Cuando creamos una nueva instancia se recibe un unica instancia.
    ######################## CODIGO DEL SINGLETON ##############################
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
    ###################### FIN CODIGO DEL SINGLETON ############################
        
    def initialize (self, user, password, database, host="localhost"):
        # Se crea una conexion a la base de datos
        # Se comprueba que existe la base de datos, en caso de no existir se crea.
        # Se comprueba que existen las tablas, en caso de no existir se crean.
        self.m_user     = user
        self.m_password = password
        self.m_database = database
        self.m_host     = host
        self.last_mailing_list = ""
        # Cerrando la anterior conexion (si la habia)
        try:
            if self.m_connection != None:
                self.finalize()
        except:
            None
        # Realizando una conexion nueva
        try:
            self.m_connection = connect (host   = self.m_host,
                                         user   = self.m_user,
                                         passwd = self.m_password,
                                         db     = self.m_database)
        except Error, e:
            self.m_connection = connect (host   = self.m_host,
                                         user   = self.m_user,
                                         passwd = self.m_password,
                                         db     = "test")
            try:
                cursor = self.m_connection.cursor ()
                cursor.execute("create database "+self.m_database)
                print "Created database ",self.m_database
                cursor.close()
                self.m_connection.close()
                self.m_connection = connect (host   = self.m_host,
                                             user   = self.m_user,
                                             passwd = self.m_password,
                                             db     = self.m_database)
            except Error, e:
                print "Error %d: %s" % (e.args[0], e.args[1])
                sys.exit (1)  
        # Momento de crear las tablas, si no estan creadas
        self.ensure_tables_creation()



    def finalize (self):
