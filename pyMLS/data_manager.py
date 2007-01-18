
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

import sys
from mls_structures import *

from utils import debug
from utils import *


class data_manager(object):
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
                                         db     = "mysql")
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
        cursor = self.m_connection.cursor()
        self.m_connection.commit()
        cursor.close()
        self.m_connection.close()
        self.m_connection = None

        

    def ensure_tables_creation (self):
        print "Creating Tables"
        rows = []
        cursor = self.m_connection.cursor ()
        cursor.execute("show tables")
        result_set = cursor.fetchall ()
        for row in result_set:
            rows.append(row[0])
        cursor.close()
        
        if 'mailing_lists' not in rows:            
            creation_queries = "CREATE TABLE IF NOT EXISTS mailing_lists("+\
            "mailing_list_url varchar(400) primary key, "+\
            "mailing_list_name varchar(60) unique, "+\
            "project_name varchar(30),                  "+\
            "status enum('new', 'visited', 'failed'),  "+\
            "last_analysis datetime) ENGINE=INNODB;     "
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()
            
        if 'compressed_files' not in rows:            
            creation_queries = "CREATE TABLE IF NOT EXISTS compressed_files( "+\
            "url varchar(500) primary key,             "+\
            "status enum('new', 'downloaded', 'analyzed', 'failed'),  "+\
            "last_analysis datetime,                   "+\
            "mailing_list_url varchar(400),            "+\
            "foreign key (mailing_list_url) references "+\
            "      mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;"
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()
            
        if 'messages' not in rows:            
            creation_queries = "CREATE TABLE IF NOT EXISTS messages( "+\
            "message_id char(128) primary key,  "+\
            "first_date datetime,               "+\
            "arrival_date datetime,             "+\
            "subject varchar(200),              "+\
            "message_body text,                 "+\
            "mailing_list_url varchar(400),     "+\
            "is_response_of char(128) default '',"+\
            "mail_path text,                    "+\
            "foreign key (mailing_list_url) references "+\
            " mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;"
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()
            
        if 'people' not in rows:
            creation_queries = "CREATE TABLE IF NOT EXISTS people( "+\
            "email_address varchar(100), "+\
            "alias varchar(100), "+\
            "primary key (email_address, alias)) ENGINE=INNODB; "
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()

        if 'messages_people' not in rows:
            creation_queries = "CREATE TABLE IF NOT EXISTS  messages_people( "+\
            "email_address varchar(100),                  "+\
            "type_of_recipient enum(\'From\',\'To\',\'Cc\',\'Bcc\'), "+\
            "message_id char(128),                    "+\
            "foreign key (email_address) references   "+\
            "     people(email_address) on delete cascade, "+\
            "foreign key (message_id) references      "+\
            "     messages(message_id) on delete cascade ) ENGINE=INNODB;"
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()

        if 'mailing_lists_people' not in rows:
            creation_queries = "CREATE TABLE IF NOT EXISTS mailing_lists_people( "+\
            "email_address varchar(100),         "+\
            "mailing_list_url varchar(400),     "+\
            "foreign key (email_address) references        "+\
            "     people(email_address) on delete cascade, "+\
            "foreign key (mailing_list_url) references     "+\
            "     mailing_lists(mailing_list_url) on delete cascade) ENGINE=INNODB;"
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()


            
        if 'libresoft' not in rows:
            creation_queries = "CREATE TABLE IF NOT EXISTS libresoft( "+\
                "id smallint unsigned primary key auto_increment, "+\
                "event_date datetime unique not null, "+\
                "project varchar(30) not null, "+\
                "tool varchar(30) not null, "+\
                "author varchar(30) not null, "+\
                "role varchar(20) not null, "+\
                "status_id smallint not null, "+\
                "first_analysis_date datetime not null, "+\
                "last_analysis_date datetime, "+\
                "tool_date_version datetime, "+\
                "description text not null, "+\
                "created_on timestamp not null, "+\
                "updated_on timestamp not null, "+\
                "lock_version integer default 0) ENGINE=INNODB;"
            cursor = self.m_connection.cursor ()
            cursor.execute(creation_queries)
            self.m_connection.commit()
            cursor.close()

    '''
    cursor.close ()
    cursor = conn.cursor (MySQLdb.cursors.DictCursor)
    cursor.execute ("SELECT name, category FROM animal")
    result_set = cursor.fetchall ()
    for row in result_set:
        print "%s, %s" % (row["name"], row["category"])
    print "Number of rows returned: %d" % cursor.rowcount
    '''
    def store_mailing_list (self, new_mailing_list, mailing_list_name, project, status):
        self.last_mailing_list = new_mailing_list

        cursor = self.m_connection.cursor()

        query = "INSERT IGNORE INTO mailing_lists "+\
                    "(mailing_list_url, mailing_list_name, project_name, status, last_analysis) "+\
                    "VALUES ('"+ new_mailing_list+"', '"+mailing_list_name+"', '"+project+"', '"+status+"',"+\
                    "now());"
        cursor.execute(query)
        query = "UPDATE mailing_lists SET status='visited' "+\
                "WHERE mailing_list_url='"+new_mailing_list+"';"
        cursor.execute(query)
        self.m_connection.commit()
        cursor.close()
        # Aqui hay que comprobar si la lista de correo se ha introducido correctamente, a veces
        # encontramos que una misma lista de correo tiene dos o mas urls distintas
        # pero que acceden a la misma lista, conviene utilizar solamente una url.
        query = "SELECT mailing_list_url "+\
                "FROM mailing_lists "+\
                "WHERE mailing_list_name='"+mailing_list_name+"';"
        cursor = self.m_connection.cursor()
        cursor.execute(query)
        result_set = cursor.fetchall ()
        self.last_mailing_list = result_set[0][0]
        cursor.close()
        

        

    def set_compressed_file_status (self, file_url, status):
        cursor = self.m_connection.cursor()

        query = "INSERT IGNORE INTO compressed_files "+\
                    "(url, status, last_analysis, mailing_list_url) "+\
                    "VALUES ('"+ file_url+"','"+status+"',now(),'"+\
                            self.last_mailing_list+"');"
        cursor.execute(query)
        query = "UPDATE compressed_files SET status='"+status+"' "+\
                "WHERE url='"+file_url+"';"
        cursor.execute(query)
        self.m_connection.commit()
        cursor.close()


           
    def get_url_compressed_files_by_status (self, mailing_list_url, status):
        compressed_files = []
        query = "SELECT url FROM compressed_files "+\
                "WHERE mailing_list_url='"+mailing_list_url+"' and status='"+status+"';"
        cursor = self.m_connection.cursor()
        cursor.execute(query)
        result_set = cursor.fetchall ()
        for row in result_set:
            compressed_files.append(row[0])
        cursor.close()
        return compressed_files
      
            


    def store_person (self, person):
        if person.email_address == '':
            return

        cursor = self.m_connection.cursor()

        query = "INSERT IGNORE INTO people "+\
                    "(email_address, alias) "+\
                    "VALUES ('"+person.email_address+"','"+person.alias+"');"
        cursor.execute(query)
                    
        if person.mailing_list != '':
            query = "INSERT IGNORE INTO mailing_lists_people "+\
                    "(email_address, mailing_list_url) "+\
                    "VALUES ('"+person.email_address+"','"+person.mailing_list+"');"
            cursor.execute(query)

                
        if person.associated_message_id != "":
            query = "INSERT IGNORE INTO messages_people "+\
                    "(email_address, type_of_recipient, message_id) "+\
                    "VALUES ('"+person.email_address+"',"+\
                            "'"+person.type_recipient+"',"+\
                            "'"+person.associated_message_id+"');"
            cursor.execute(query)

        self.m_connection.commit()
        cursor.close()





      
    def store_email (self, new_email, file_processed = ''):

        # Quitando caracteres indeseables
        #new_email.subject = new_email.subject.replace("'","''")
        #new_email.body = new_email.body.replace("'","''")
        cursor = self.m_connection.cursor()

        query = "INSERT IGNORE INTO messages "+\
            "(message_id, first_date, arrival_date, subject, "+\
            " message_body, mailing_list_url, is_response_of, mail_path)"+\
            " VALUES " +\
            "('" + new_email.generate_unique_id() + "', "+\
            " '" + new_email.first_date + "' , "+\
            " '" + new_email.arrival_date + "', "+\
            " '" + new_email.subject + "', "+\
            " '" + new_email.body +"', "+\
            " '" + self.last_mailing_list + "', "+\
            " '', '');"

        '''
        # Sistema de hilos:
            Para que un email consiga un mensaje, lo que se hace es buscar todos
            los mensajes cuyo subject sea el mismo que este sin la "Re: " inicial,
            como pueden aparecer varios mensajes, por defecto se coge el mas antiguo.
            
        '''
        
        cursor.execute(query)

        self.m_connection.commit()
        cursor.close()        
        '''
            new_email.author_from  = ""
            new_email.author_alias = ""
            new_email.mailing_list = ""
            new_email.to           = []
            new_email.carbon_copy  = []
        '''
        # Guardando la persona que envia el correo.
        self.store_person( person(new_email.author_from,\
                                  new_email.author_alias,\
                                  self.last_mailing_list,\
                                  new_email.message_id,\
                                  'From') )
        # Guardando los destinatarios
        for receiver in new_email.to:
            receiver_email = receiver
            receiver_alias = ""
            #"Nickolay V. Shmyrev" <nshmyrev@yandex.ru>
            if '"' in receiver:
                receiver = receiver.replace('"','')
            if '<' in receiver:
                receiver = receiver.rstrip('>')
                receiver = receiver.split('<')
                receiver_email = receiver[1].strip(' ')
                receiver_alias = receiver[0].strip(' ')
                debug(receiver_email+"  -->  "+receiver_alias)
            self.store_person( person(receiver_email,\
                                      receiver_alias,\
                                      self.last_mailing_list,\
                                      new_email.message_id,\
                                      'To') )

        # Guardando las copias en carbon
        for receiver in new_email.carbon_copy:
            receiver_email = receiver
            receiver_alias = ""
            #"Nickolay V. Shmyrev" <nshmyrev@yandex.ru>
            #evince-list@gnome.org
            if '"' in receiver:
                receiver = receiver.replace('"','')
            if '<' in receiver:
                receiver = receiver.rstrip('>')
                receiver = receiver.split('<')
                receiver_email = receiver[1].strip(' ')
                receiver_alias = receiver[0].strip(' ')
                debug(receiver_email+"  -->  "+receiver_alias)
            self.store_person( person(receiver_email,\
                                      receiver_alias,\
                                      self.last_mailing_list,\
                                      new_email.message_id,\
                                      'Cc') )



#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: data_manager.py **"
    my_data_manager = data_manager()
    my_data_manager.setup_database('operator', 'operator', 'pepote')
    my_data_manager.close_database()
    

        
if __name__ == "__main__":
    test()





