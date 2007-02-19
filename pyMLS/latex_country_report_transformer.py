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
   Python: latex_country_report_transformer
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''


'''
    $<$put-a-country-here$>$
    $<$put-mailing-lists-number$>$
    $<$put-projects-number$>$
    $<$put-posters-number$>$
    $<$put-messages-number$>$
    $<$put-date$>$
    $<$put-top10-mailing-lists$>$
    $<$put-all-mailing-lists$>$
    $<$put-all-posters$>$
'''
from utils import *
import os, datetime
from transformer import transformer
from data_manager import *


class latex_country_report_transformer(transformer):

    def __init__(self, config_object, output_directory=""):
        self.config               = config_object
        self.country              = self.config.get_value("country")
        self.country_database     = "mailingliststat_"+self.country
        self.country_database     = self.country_database.replace(" ","_")
        self.mailing_lists_number = 0
        self.projects_number      = 0
        self.posters_number       = 0
        self.messages_number      = 0
        self.date                 = datetime.datetime.now().strftime("%d %B %Y")
        self.top10_mailing_lists  = []
        self.all_mailing_lists    = []
        self.top10_mailing_lists  = []
        self.top10_posters        = []
        self.all_posters          = []
        self.result_path          = os.getcwd()
        self.m_connection         = None
        self.country_db_connection= None
        # Ahora creamos una base de datos que unifique todos los datos de todos
        # los proyectos.
        self.country_db_connection = create_database(
                                        self.config.get_value('database_server'),
                                        self.config.get_value('database_user'),
                                        self.config.get_value('database_password'),
                                        self.country_database)
        # Necesitamos crear una base de datos, conseguir una conexion a la misma
        # y tambien hace falta crear dos tablas:
        
        # Necesitamos una tabla que contenga todas las listas de correo analizadas,
        # indicando el proyecto, numero de mensajes y numero de posters.

        table_definition = "CREATE TABLE mailing_lists("+\
                           "mailing_list_name varchar(60) primary key, "+\
                           "project_name varchar(30),                  "+\
                           "posters integer,                           "+\
                           "messages integer,                          "+\
                           "last_analysis datetime) ENGINE=INNODB; "

        ensure_table_creation(self.country_db_connection, table_definition)
        # Necesitamos una tabla que contenga todos los posters encontrados,
        # indicando el numero de mensajes que han emitido.
        table_definition = "CREATE TABLE posters(                    "+\
                           "email_address varchar(100) primary key,  "+\
                           "messages integer,                        "+\
                           "last_analysis datetime) ENGINE=INNODB; "
        ensure_table_creation(self.country_db_connection, table_definition)





    def announce(self, data):
        # El dato recibido es una lista que guarda:
        #  [path_donde_guardar_resultados, base_de_datos]
        database    = data[1]
        project_name = database.replace('mailingliststat_','')
        self.result_path = data[0]
        if self.result_path == '':
            self.result_path = os.getcwd()
        # ----------- Abriendo la conexion con la base de datos -----------
        self.m_connection = connect(host   = self.config.get_value('database_server'),
                                    user   = self.config.get_value('database_user'),
                                    passwd = self.config.get_value('database_password'),
                                    db     = database)
        # -----------------------------------------------------------------

        # Hay que coger todas las listas de correo, para cada una de ellas
        # hay que coger el numero de mensajes y el numero de posters, una
        # vez que los tengamos hay que meterlas en la tabla "mailing_lists"

        local_mailing_lists = do_select_query (self.m_connection,\
                "SELECT mailing_list_url, count(distinct email_address) as ea "+\
                "FROM  mailing_lists_people " +\
                "GROUP BY mailing_list_url " +\
                "ORDER BY ea DESC")


        for ml in local_mailing_lists:
            messages = do_count_query (self.m_connection,\
                                "SELECT count(distinct message_md5) "+\
                                "FROM messages " +\
                                "WHERE mailing_list_url = '"+ml[0]+"' "+\
                                "GROUP BY mailing_list_url")
            # Solo queremos el nombre de la lista de correo, no su url
            ml[0] = ml[0].split('/')[-1]
            # Insertando todos los resultados
            do_input_query (self.country_db_connection,\
                      "INSERT IGNORE INTO mailing_lists "+\
                      "(mailing_list_name,project_name,posters,messages,last_analysis) "+\
                      "VALUES ('"+ml[0]+"','"+project_name+"',"+str(ml[1])+","+str(messages)+",now())")
            # Si ya estaba por un casual la fila la actualizamos por si acaso
            do_input_query (self.country_db_connection,\
                      "UPDATE mailing_lists SET "+\
                      "posters  = "+str(ml[1])+",  "+\
                      "messages = "+str(messages)+",  "+\
                      "last_analysis = now() "+\
                      "WHERE  mailing_list_name = '"+ml[0]+"'")


        # Hay que coger el e-mail de cada poster y el numero de mensajes que
        # ha enviado (siempre que sea mayor de 1), una
        # vez que los tengamos hay que meterlas en la tabla "posters"

        local_posters = do_select_query (self.m_connection,\
                "SELECT email_address, count(message_id) as mi "+\
                "FROM  messages_people " +\
                "GROUP BY email_address " +\
                "ORDER BY mi DESC")


        for lp in local_posters:
            # Insertando todos los resultados
            do_input_query (self.country_db_connection,\
                      "INSERT IGNORE INTO posters "+\
                      "(email_address, messages, last_analysis) "+\
                      "VALUES ('"+lp[0]+"',"+str(lp[1])+",now())")
            # Si ya estaba por un casual la fila la actualizamos por si acaso
            do_input_query (self.country_db_connection,\
                            "UPDATE posters SET "+\
                            "messages = "+str(lp[1])+",  "+\
                            "last_analysis = now() "+\
                            "WHERE  email_address = '"+lp[0]+"'")







    def finish (self):
        #"$<$put-a-country-here$>$"
        #"$<$put-mailing-lists-number$>$"
        #"$<$put-projects-number$>$"
        #"$<$put-posters-number$>$"
        #"$<$put-messages-number$>$"
        #"$<$put-date$>$"
        #"$<$put-top10-mailing-lists$>$"
        #"$<$put-all-mailing-lists$>$"
        #"$<$put-all-posters$>$"
        working_path = self.result_path + '../'
        print "Estamos en ",os.getcwd()," el path de resultados es ",self.result_path
        f = open('templates/mls_country_report.tex','r')
        final_text = f.read()
        f.close()

        if "$<$put-a-country-here$>$" in final_text:
            final_text = final_text.replace("$<$put-a-country-here$>$",
                                            self.country)


        if "$<$put-mailing-lists-number$>$" in final_text:
            self.mailing_lists_number = do_count_query(
                                        self.country_db_connection,
                                        "SELECT count(*) from mailing_lists")
            final_text = final_text.replace("$<$put-mailing-lists-number$>$",
                                            str(self.mailing_lists_number))



        if "$<$put-projects-number$>$" in final_text:
            self.projects_number = do_count_query(self.country_db_connection,
                    "SELECT count(distinct project_name) from mailing_lists")
            final_text = final_text.replace("$<$put-projects-number$>$",
                                            str(self.projects_number))



        if "$<$put-posters-number$>$" in final_text:
            self.posters_number = do_count_query(self.country_db_connection,
                                        "SELECT count(*) from posters")
            final_text = final_text.replace("$<$put-posters-number$>$",
                                            str(self.posters_number))


        if "$<$put-messages-number$>$" in final_text:
            self.messages_number = do_count_query(self.country_db_connection,
                                        "SELECT sum(messages) from mailing_lists")
            final_text = final_text.replace("$<$put-messages-number$>$",
                                            str(self.messages_number))


        if "$<$put-date$>$" in final_text:
            final_text = final_text.replace("$<$put-date$>$", self.date)



        if "$<$put-top10-mailing-lists$>$" in final_text:
            self.top10_mailing_lists = do_select_query(self.country_db_connection,
                    "SELECT project_name,mailing_list_name,posters,messages "+\
                    "FROM mailing_lists "+\
                    "ORDER BY posters DESC "+\
                    "LIMIT 10 ")

            latex_table = ""
            for ml in self.top10_mailing_lists:
                latex_table += "                                "
                latex_table += ml[0]+" & "+ml[1]+" & "+ml[2]+" & "+ml[3]+" \\\\ \n"
                latex_table += "                                \hline \n"
            latex_table = latexfy_text(latex_table)
            final_text = final_text.replace("$<$put-top10-mailing-lists$>$",
                                            latex_table)




        if "$<$put-top10-posters$>$" in final_text:
            self.top10_posters = do_select_query(self.country_db_connection,
                                "SELECT email_address, messages "+\
                                "FROM posters "+\
                                "ORDER BY messages DESC "+\
                                "LIMIT 10")
            latex_table = ""
            for ml in self.top10_posters:
                latex_table += "                                "
                latex_table += ml[0]+" & "+ml[1]+" \\\\ \n"
                latex_table += "                                \hline \n"
            latex_table = latexfy_text(latex_table)
            final_text = final_text.replace("$<$put-top10-posters$>$",
                                            latex_table)




        if "$<$put-all-mailing-lists$>$" in final_text:
            self.all_mailing_lists = do_select_query(self.country_db_connection,
                    "SELECT project_name,mailing_list_name,posters,messages "+\
                    "FROM mailing_lists "+\
                    "ORDER BY posters DESC ")
            latex_table = ""
            counter = 0
            for ml in self.all_mailing_lists:
                latex_table += "                                "
                latex_table += ml[0]+" & "+ml[1]+" & "+ml[2]+" & "+ml[3]+" \\\\ \n"
                latex_table += "                                \hline \n"
                counter += 1
                if counter == 30:
                    latex_table +="         \\end{tabular}  \n"
                    latex_table +="     \\end{center}       \n"
                    latex_table +=" \\end{table}            \n"
                    latex_table +=" \n"
                    latex_table +="  \\begin{table}[h]      \n"
                    latex_table +="     \\begin{center}     \n"
                    latex_table +="         \\begin{tabular}[t]{|l|l|c|c|}\n"
                    latex_table += "                                \hline \n"
                    counter = 0

            latex_table = latexfy_text(latex_table)
            final_text = final_text.replace("$<$put-all-mailing-lists$>$",
                                            latex_table)



        if "$<$put-all-posters$>$" in final_text:
            self.all_posters = do_select_query(self.country_db_connection,
                                "SELECT email_address, messages "+\
                                "FROM posters "+\
                                "WHERE messages > 3 "+\
                                "ORDER BY messages DESC")
            latex_table = ""
            counter = 0
            for ml in self.all_posters:
                latex_table += "                                "
                latex_table += ml[0]+" & "+ml[1]+" \\\\ \n"
                latex_table += "                                \hline \n"
                counter += 1
                if counter == 30:
                    latex_table +="         \\end{tabular}  \n"
                    latex_table +="     \\end{center}       \n"
                    latex_table +=" \\end{table}            \n"
                    latex_table +=" \n"
                    latex_table +="  \\begin{table}[h]      \n"
                    latex_table +="     \\begin{center}     \n"
                    latex_table +="         \\begin{tabular}[t]{|l|c|}\n "
                    latex_table += "                                \hline \n"
                    counter = 0

            other_posters = do_count_query(self.country_db_connection,
                                "SELECT sum(messages) "+\
                                "FROM posters "+\
                                "WHERE messages <= 3 ")
            latex_table += "                                "
            latex_table += "\\textbf{Others} & "+other_posters+" \\\\ \n"
            latex_table += "                                \hline \n"
            latex_table = latexfy_text(latex_table)
            final_text = final_text.replace("$<$put-all-posters$>$",latex_table)

        output_filename = working_path + self.country + '_mls_report.tex'
        output_filename = output_filename.replace(" ","_")
        g = open(output_filename, 'w')
        g.write(final_text)
        g.close()

        # pdf generation
        previous_path = os.getcwd()
        os.chdir(working_path)

        os.system("latex   " + output_filename)
        os.system("bibtex  " + output_filename.replace('.tex','.aux'))
        os.system("latex   " + output_filename)
        os.system("dvipdft " + output_filename.replace('.tex','.dvi'))

        os.system("rm -f *.aux *.bbl *.blg *.dvi *.log")
        os.chdir(previous_path)
        print "   - latex_country_report_transformer Finished"
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
    print "** UNITY TEST: latex_country_report_transformer.py **"
    a_config = test_config_object()
    a = latex_country_report_transformer(a_config)
    a.announce(['/home/jgascon','mailingliststat_arrakis'])
    a.finish()

if __name__ == "__main__":
    test()

