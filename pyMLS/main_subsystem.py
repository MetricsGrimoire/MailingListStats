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

import os, time
from threading import *
from config_manager import *
import urllib
import utils
import analysis_subsystem
import data_manager
import stats_subsystem

class main_subsystem:

    def __init__(self, config):
        # Tomando el tiempo de inicio
        self.config = config
        self.m_data_manager = data_manager.data_manager()

        
    def run(self):
        print "Working..."
        pre_time = time.time()
        # Se mira cuantas listas de correo hay que analizar.
        if self.config.get_value("projects_file_name") == "":
            #Las listas de correo se han pasado como parametro.
            project_urls  = self.config.get_value("projects_mail_url")
            project_names = self.get_project_names_from_urls(project_urls)
            mailing_names = self.get_mailing_names_from_urls(project_urls)
        else:
            #Las listas de correo estan en un fichero pasado como parametro.
            project_urls  = self.get_all_urls_from_file(self.config.get_value("projects_file_name"))
            project_names = self.get_project_names_from_urls(project_urls)
            mailing_names = self.get_mailing_names_from_urls(project_urls)

        self.config.set_value('databases', [])
        # Se comienza el analisis de cada una de las listas de correo.
        while project_names != []:
            project  = project_names.pop(0)
            mail_url = project_urls.pop(0)
            mail_name = mailing_names.pop(0)
            databases = self.config.get_value('databases')
            print "Processing:  "+mail_name
            # Consiguiendo un nombre para la base de datos
            self.config.set_value('database_name', "mailingliststat_"+project.replace('-','_'))
            databases.append("mailingliststat_"+project.replace('-','_'))
            self.config.set_value('databases',databases)
            
            # Inicializando la base de datos
            self.m_data_manager.initialize (self.config.get_value('database_user'),
                                            self.config.get_value('database_password'),
                                            self.config.get_value('database_name'),
                                            self.config.get_value('database_server'))
            # Se crea un directorio para guardar todos los datos del proyecto,
            # tambien se prepara la base de datos conveniente.
            print "   Step 1) Preparing Project Enviroment."
            temp_destiny_dir = self.preparing_project_enviroment(project, mail_name)

            # Se explora la pagina web de cada lista de correo, de ella se consigue
            # una lista de enlaces a ficheros valida (quitando los enlaces que ya
            # se descargaron en el pasado).
            print "   Step 2) Looking for mailing list file links."
            mail_file_urls = self.get_mail_archive_urls (mail_url)
            
            # Se obtienen y preparan todos los archivos de la lista de correo.
            print "   Step 3) Processing files."
            if mail_file_urls == []:
                self.m_data_manager.store_mailing_list (mail_url, mail_name, project, 'failed')
            else:
                self.m_data_manager.store_mailing_list (mail_url, mail_name, project, 'visited')
                self.processing_files(mail_file_urls, temp_destiny_dir)
                analysis = analysis_subsystem.analysis_subsystem(self.config)
                analysis.run(temp_destiny_dir)
            # Closing database connection
            self.m_data_manager.finalize ()

        # Se inicializa el sistema de generadores, a fin de generar otro tipo de
        # informacion a partir de los datos de la base de datos.
        print "   Final Step) Generating stats."
        stats = stats_subsystem.stats_subsystem(self.config)
        stats.run()
        # El programa finaliza.
        post_time = time.time()
        print "The study has taken "+str(int(post_time - pre_time))+" seconds."
        print "Finished."



    
    def get_all_urls_from_file(self, filename):
        print "  Getting urls from: "+filename
        urls = []
        try:
            f = open(filename, 'r', 32000)
        except:
            print "  ERROR: ",filename," unavailable."
            return []
        line = f.readline()
        line = line.strip(' ')
        while line != "":
            line = line.strip()
            line = line.rstrip('/')
            line = line.replace("\n","")
            if "http" in line and line[0] != '#':
                urls.append(line)
            line = f.readline()
        f.close()
        return urls




    def get_project_names_from_urls (self, urls):
        projects = []
        for url in urls:
            # El nombre de proyecto suele ser la palabra que va despues de la ultima /
            url = url.strip(' ')
            url = url.rstrip('/')
            list_name = url.split('/')[-1]
            if '-' in list_name:
                projects.append(list_name.split('-')[0])
            else:
                projects.append(list_name)
        return projects



    def get_mailing_names_from_urls (self, urls):
        mailing_names = []
        for url in urls:
            # El nombre de proyecto suele ser la palabra que va despues de la ultima /
            url = url.strip()
            url = url.rstrip('/')
            list_name = url.split('/')[-1]
            mailing_names.append(list_name)
        return mailing_names

            


    def preparing_project_enviroment(self, project_name, mailing_list_name):
        # Aqui se crea el directorio encargado de almacenar los resultados
        # Se crea un directorio con el nombre del proyecto, dentro de este directorio:
        #   - Se crea un directorio llamado "temp" para almacenar los datos temporales.
        #   - Se crea un directorio llamado "results" para almacenar los resultados definitivos.
        #   - Se crea un directorio llamado "log" para almacenar los logs.
        # Se crea una conexion a la base de datos, si no hay una disponible.
        previous_directory = os.getcwd()
        results_directory = self.config.get_value("results_directory")
        directory = results_directory+"/"+project_name
        try:
            os.chdir(directory+"/"+mailing_list_name)
        except:
            os.makedirs(directory+"/"+mailing_list_name)

        try:
            os.chdir(directory+"/results")
        except:
            os.makedirs(directory+"/results")
        os.chdir(previous_directory)
        return directory+"/"+mailing_list_name





    def get_mail_archive_urls(self, mail_url):
        definitive_mailing_list_files = []
        # Dada la url se mira en la pagina en busca de enlaces a ficheros.
        temporal_mailing_list_files = utils.get_mailing_list_file_links(mail_url)
        # Ahora se mira en la base de datos para ver cuales ficheros son validos
        # (no los hemos bajado antes)
        downloaded_files = self.m_data_manager.get_url_compressed_files_by_status(mail_url, 'downloaded')
        downloaded_files.extend(self.m_data_manager.get_url_compressed_files_by_status(mail_url, 'analyzed'))
        while temporal_mailing_list_files != []:
            file = temporal_mailing_list_files.pop(0)
            if file not in downloaded_files:
                definitive_mailing_list_files.append(file)
            else:
                print "     Ignore "+file
        return definitive_mailing_list_files




    def processing_files(self, mail_file_urls, destiny_dir):
        # Creando un directorio para cada lista de correo.
        previous_directory = os.getcwd()
        for url in mail_file_urls:
            # Creando un directorio para cada lista de correo y cada archivo.
            url = url.rstrip('/')
            local_file = url.split('/')[-1]
            #local_file = url.replace('.','_')
            #my_destiny_dir = destiny_dir+'/'+local_file
            try:
                os.chdir(destiny_dir)
            except:
                os.makedirs(destiny_dir)
            # Descargando el fichero de marras
            print "     Downloading " + url
            if True == utils.download_url_to (url, destiny_dir+'/'+local_file):
                self.m_data_manager.set_compressed_file_status (url, 'downloaded')
            else:
                self.m_data_manager.set_compressed_file_status (url, 'failed')
            
        # Ahora hay que descomprimir todos los ficheros
        utils.for_every_file (destiny_dir, utils.decompress_file)
        os.chdir(previous_directory)



    def generate_stats(self):
        print "    Generando estadisticas a partir de los resultados"




#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: main_subsystem.py **"

    
if __name__ == "__main__":
    test()

