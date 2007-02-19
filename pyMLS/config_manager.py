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
    Config:
    Se encargar de leer el fichero de configuracion y de interpretar sus valores

    Los workers utilizan este objeto para acceder a valores de la configuracion.

    La configuracion contiene los valores del proyecto a descargar, la url,
    el tipo de repositorio, los transformadores que deben utilizarse, etc...

    Internamente no es mas que un diccionario.
'''

import os
from parser_factory import parser_factory

class config_manager:

    def __init__(self, config_file=""):
        self.order_parameters = []
        # Este objeto tiene una serie de variables con valores predeterminados.      
        self.parameters = {}
        # Tambien tienen unos comentarios con informacion acerca de los parametros.
        self.comments = {}
        
        #---------------------- DEFAULT VALUES ----------------------
        if config_file == "":
            self.order_parameters.append('config_file')
            self.parameters['config_file'] = "mailingListStat.conf"
        else:
            self.order_parameters.append('config_file')
            self.parameters['config_file'] = config_file

        self.comments['config_file']   =\
        "#  MailingListStat configuration file"


        self.order_parameters.append('country')
        self.parameters['country'] = "<put_a_country_here>"
        self.comments['country'] = \
        "# This value is used for some transformers, for giving a \n"+\
        "# country to every project."

        '''
        self.order_parameters.append('only_calculate_stats')
        self.parameters['only_calculate_stats'] = "NO"
        self.comments['only_calculate_stats'] = \
        "# If this option is YES, MailingListStat only calculates stats and finishes."

        self.order_parameters.append('seal_xml_transformer')
        self.parameters['seal_xml_transformer'] = "NO"
        self.comments['seal_xml_transformer'] = \
        "# A generator that generates xml files for seal."

        self.order_parameters.append('send_to_seal_server')
        self.parameters['send_to_seal_server'] = "127.0.0.1"
        self.comments['send_to_seal_server'] = \
        "# Sends generated XML file to SEAL server."

        self.order_parameters.append('purge_temporal_data')
        self.parameters['purge_temporal_data'] = "NO"
        self.comments['purge_temporal_data'] = \
        "# Delete temporal files after every analysis."
        '''
        
        self.order_parameters.append('basic_transformer')
        self.parameters['basic_transformer'] = "YES"
        self.comments['basic_transformer'] = \
        "# A simple generator that counts how many elements are in tables."
        
        self.order_parameters.append('dump_db_transformer')
        self.parameters['dump_db_transformer'] = "YES"
        self.comments['dump_db_transformer'] = \
        "# A generator that dumps database to a compressed sql file."

        self.order_parameters.append('most_active_transformer')
        self.parameters['most_active_transformer'] = "NO"
        self.comments['most_active_transformer'] = \
        "# Shows in a file stored in Results directory the most active \n"+\
        "# developers per project, see 'number_most_active_developers' option."


        self.order_parameters.append('latex_country_report_transformer')
        self.parameters['latex_country_report_transformer'] = "YES"
        self.comments['latex_country_report_transformer'] = \
        "# This transformer generates a report of all projects in a country.\n"+\
        "# This report is built in Latex, and stored in Results/Documents directory."


        self.order_parameters.append('libresoft_big_database_transformer')
        self.parameters['libresoft_big_database_transformer'] = "NO"
        self.comments['libresoft_big_database_transformer'] = \
        "# This transformer sends relevant data about every project and \n"+\
        "# sends it to Libresoft central Database."


        self.order_parameters.append('libresoft_big_database_host')
        self.parameters['libresoft_big_database_host'] = "chico.libresoft.es"
        self.comments['libresoft_big_database_host'] = \
        "# Host where Libresoft has its central Database."


        self.order_parameters.append('libresoft_big_database_database')
        self.parameters['libresoft_big_database_database'] = "floss_project_store"
        self.comments['libresoft_big_database_database'] = \
        "# Database where Libresoft has its central Database."

        
        self.order_parameters.append('libresoft_big_database_user')
        self.parameters['libresoft_big_database_user'] = "customer"
        self.comments['libresoft_big_database_user'] = \
        "# User to access where Libresoft has its central Database."


        self.order_parameters.append('libresoft_big_database_password')
        self.parameters['libresoft_big_database_password'] = "b1llpuert45"
        self.comments['libresoft_big_database_password'] = \
        "# Password to access where Libresoft has its central Database."


        self.order_parameters.append('number_most_active_developers')
        self.parameters['number_most_active_developers'] = "20%"
        self.comments['number_most_active_developers'] = \
        "# A parameter for 'most_active_transformer', indicates how many\n" + \
        "# developers should be shown."

        self.order_parameters.append('database_system')
        self.parameters['database_system'] = "mysql"
        self.comments['database_system'] = \
        "# Default database system where all results will be stored."

        self.order_parameters.append('database_server')
        self.parameters['database_server'] = "localhost"
        self.comments['database_server'] = \
        "# Default database host where all results will be stored."

        self.order_parameters.append('database_user')
        self.parameters['database_user'] = "operator"
        self.comments['database_user'] = \
        "# Default database user for databases creation and operation."

        self.order_parameters.append('database_password')
        self.parameters['database_password'] = "operator"
        self.comments['database_password'] = \
        "# Default database password for databases creation and operation."

        self.order_parameters.append('destiny_directory')
        self.parameters['destiny_directory'] = "Results"
        self.comments['destiny_directory'] = \
        "# Directory where temporal results will be stored."

        #-- PUT HERE YOUR DEFAULT VALUES


        #---------------------- END OF DEFAULT VALUES ----------------------
        
        # En primer lugar se ocupa de ver si existe el fichero de configuracion.
        #try:
        # Si existe entonces crea un parser especifico que se encargue de
        # analizarlo, los valores resultantes los guarda en "self.parameters"
        try:
            f=open(self.parameters['config_file'], "r")
            f.close()
            self.parse_file( self.parameters['config_file'] )
        except:
            # Si el fichero de configuracion no existe entonces se crea uno con los
            # parametros y valores por defecto.
            print "El fichero de configuracion no existe o no es correcto, creandolo."
            self.rewrite_file( self.parameters['config_file'] )
  



    def parse_file(self, filename):
        my_parser = parser_factory.get_parser("CONFIG")
        my_parser.match_file(filename)
        result = my_parser.get_result()
        for key in result.keys():
            self.parameters[key] = result[key]


        

    def rewrite_file(self, filename):
        f = open(self.parameters['config_file'], "w")
        for par in self.order_parameters:
            f.write(self.comments[par])
            f.write("\n")
            f.write(par+"="+self.parameters[par])
            f.write("\n\n\n")
        f.close()



    def get_value(self, key):
        # 
        if self.parameters.has_key(key):
            return self.parameters[key]
        else:
            return ""


      
    def set_value(self, key, value):
        self.parameters[key] = value



    def get_keys_that_contain (self, text):
        result = []
        for key in self.parameters:
            if text in key:
                result.append(key)
        return result
      

#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: config_manager.py **"
    a = config_manager()
    print "PARAMETROS: ",a.parameters
    print "Agregando una nueva clave: dump_core -> YES"
    a.set_value("dump_core","YES")
    print "Leyendo el nuevo valor de dump_core"
    print a.get_value("dump_core")
    print "Cogiendo todas las claves que contengan la palabra: generator"
    print a.get_keys_that_contain("generator")


if __name__ == "__main__":
    test()
