# Copyright (C) 2007 Libresoft Research Group
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
# Authors :
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>

"""
This module contains a basic SQL wrapper. It uses the standard
database API of Python, so any module may be used (just substitute
import MySQLdb for any other, for instance import PyGreSQL).

@authors:      Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      herraiz@gsyc.escet.urjc.es
"""

import MySQLdb
from pymlstats import data_model

class Database:

    def __init__(self):

        self.name = ''
        self.user = ''
        self.password = ''
        self.admin_user = ''
        self.admin_password = ''
        self.host = ''

        self.__dbobj = None
        # Use this cursor to access to data in the database
        self.read_cursor = None
        # Use this cursor to dump data into the database
        self.write_cursor = None

    def connect(self):

        try:
            self.__dbobj = MySQLdb.connect(self.host,self.user,self.password,self.name)
        except MySQLdb.OperationalError:
            # Database does not exist
            # So create it
            self.__dbobj = MySQLdb.connect(self.host,self.admin_user,self.admin_password,"")
            cursor = self.__dbobj.cursor()
            query = "CREATE DATABASE "+self.name
            cursor.execute(query)
            query = "USE "+self.name+";"
            cursor.execute(query)
            for query in data_model.data_model_query_list:
                cursor.execute(query)
            self.__dbobj.commit()

            # Database created, now reconnect
            self.__dbobj = MySQLdb.connect(self.host,self.user,self.password,self.name)
            
        self.read_cursor = self.__dbobj.cursor()
        self.write_cursor = self.__dbobj.cursor()

    def check_compressed_file(self,url):

        query = 'SELECT status FROM compressed_files where url="'+url+'";'
        num_of_results = self.read_cursor.execute(query)

        try:
            status = self.read_cursor.fetchone()[0]
        except TypeError:
            status = None

        return status

    def update_mailing_list(self,url,name,last_analysis):

        query = 'UPDATE mailing_lists SET last_analysis="'+last_analysis+'" WHERE mailing_list_url="'+url+'";'
        num_of_results = self.write_cursor.execute(query)
        
        if 0 == num_of_results:
            
            query = 'INSERT INTO mailing_lists (mailing_list_url,mailing_list_name,last_analysis)'
            query += ' VALUES ("'+url+'","'+name+'","'+last_analysis+'");'
            self.write_cursor.execute(query)

        self.__dbobj.commit()

    def set_visited_url(self,url,mailing_list_url,last_analysis):

        query = 'UPDATE compressed_files SET status="visited", last_analysis="'+last_analysis+'" WHERE url="'+url+'";'
        num_of_results = self.write_cursor.execute(query)

        if 0 == num_of_results:
            query = 'INSERT INTO compressed_files (url,mailing_list_url,status,last_analysis)'
            query += ' VALUES ("'+url+'","'+mailing_list_url+'","visited","'+last_analysis+'");'
            self.write_cursor.execute(query)

        self.__dbobj.commit()

    def store_messages(self,message_list,mailing_list_url):

        query = 'SET FOREIGN_KEY_CHECKS = 0;'
        self.write_cursor.execute(query)

        stored_messages = 0
        
        for m in message_list:
            query_left = 'INSERT INTO messages('
            query_right = ' VALUES ('
            query_people = ''
            query_messages_people = []

            values = []
            to_addresses = []
            cc_addresses = []
            from_addresses = []

            message_id = ""

            headers = m.keys()
            for h in headers:
                value = m[h]

                if 'message-id' == h:
                    query_left += 'message_id,'
                    query_right += '%s,'
                    values.append(value)
                    message_id = value
                elif 'to' == h:
                    to_addresses += value
                elif 'cc' == h:
                    cc_addresses += value
                elif 'date' == h:
                    query_left += 'first_date,'
                    query_right += '"'+value+'",'
                elif 'date_tz' == h:
                    query_left += 'first_date_tz,'
                    query_right += value+','
                elif 'received' == h:
                    query_left += 'arrival_date,'
                    query_right += '"'+value+'",'
                elif 'received_tz' == h:
                    query_left += 'arrival_date_tz,'
                    query_right += value+','
                elif 'list-id' == h:
                    query_left += 'mailing_list,'
                    query_right += '%s,'
                    values.append(value)
                elif 'in-reply-to' == h:
                    query_left += 'is_response_of,'
                    query_right += '%s,'
                    values.append(value)
                elif 'body' == h:
                    query_left += 'message_body,'
                    query_right += '%s,'
                    values.append(value)
                elif 'from' == h:
                    query_left += 'author_email_address,'
                    query_right += '%s,'
                    try:
                        values.append(value[0][1])
                    except:
                        values.append('')                        
                    from_addresses += value
                elif 'subject' == h:
                    query_left += 'subject,'
                    query_right += '%s,'
                    values.append(value)

            query_left += 'mailing_list_url,'
            query_right += '%s,'
            values.append(mailing_list_url)
            
            query_left = query_left.rstrip(',') + ')'
            query_right = query_right.rstrip(',') + ');'
            query_message = query_left + query_right

            # FIXME: If primary key check fails, ignore and continue
            messages_people_values = {}
            for addr in to_addresses:
                query = 'INSERT INTO messages_people(email_address,type_of_recipient,message_id)'
                query += ' VALUES (%s,%s,%s);'
                messages_people_values[query] = [addr[1],"To",message_id]
            
            for addr in cc_addresses:
                query = 'INSERT INTO messages_people(email_address,type_of_recipient,message_id)'
                query += ' VALUES (%s,%s,%s);'
                messages_people_values[query] = [addr[1],"Cc",message_id]

            from_values = []
            mailing_lists_people_values = []
            for addr in from_addresses:
                name = addr[0]
                email = addr[1]
                try:
                    top_level_domain = email.split(".")[-1]
                except IndexError:
                    top_level_domain = ''

                try:
                    domain_name = email.split("@")[1]
                except IndexError:
                    domain_name = ''

                try:
                    username = email.split("@")[0]
                except IndexError:
                    username = ''

                from_values = [email,name,username,domain_name,top_level_domain]

                query_people = 'INSERT INTO people (email_address,name,username,domain_name,top_level_domain)'
                query_people += ' VALUES (%s,%s,%s,%s,%s);'
                #query_people += ' VALUES ("'+email+'","'+name+'","'+username+'","'+domain_name+'","'+top_level_domain+'");'

                query_mailing_lists_people = 'INSERT INTO mailing_lists_people (email_address,mailing_list_url)'
                query_mailing_lists_people += ' VALUES (%s,%s);'
                mailing_lists_people_values = [email,mailing_list_url]

            try:
                self.write_cursor.execute(query_message,values)
            except MySQLdb.IntegrityError:
                # Duplicated message
                #print "  ***WARNING: Duplicated message "+m['message-id']+"***"
                stored_messages -= 1
            except:
                import sys
                print "ERROR: Oops. Something went really bad. Please copy the information that appears below and send it to herraiz@gsyc.escet.urjc.es"
                print
                print " -------------------- COPY BELOW -----------------------"
                print query_message
                print values
                print " -------------------- END OF COPY -----------------------"
                sys.exit(1)

            try:
                self.write_cursor.execute(query_people,from_values)
            except MySQLdb.IntegrityError:
                pass

            for query in messages_people_values.keys():
                try:
                    self.write_cursor.execute(query,messages_people_values[query])
                except MySQLdb.IntegrityError:
                    # Duplicate entry email_address-to|cc-mailing list url
                    pass
            
            try:
                self.write_cursor.execute(query_mailing_lists_people,mailing_lists_people_values)
            except MySQLdb.IntegrityError:
                # Duplicate entry email address-mailing list url
                pass
                
            self.__dbobj.commit()
            stored_messages += 1


        query = 'SET FOREIGN_KEY_CHECKS = 1;'
        self.write_cursor.execute(query)
        self.__dbobj.commit()

        return stored_messages

    # --------------------
    # Report functions
    # --------------------

    def get_num_of_mailing_lists(self):

        query = 'select count(distinct mailing_list_url) from mailing_lists;'
        self.read_cursor.execute(query)

        return self.read_cursor.fetchone()[0]

    def get_messages_by_domain(self):

        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists

        query = 'select mailing_list_url, domain_name, count(message_id) as t from messages, people where author_email_address=email_address group by mailing_list_url, domain_name order by t desc limit %d;' % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_people_by_domain(self):

        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists

        query = 'select mailing_list_url, domain_name, count(p.email_address) as t from mailing_lists_people as ml, people as p where ml.email_address=p.email_address group by mailing_list_url, domain_name order by t desc limit %d;' % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_messages_by_tld(self):
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists

        query = 'select mailing_list_url, top_level_domain, count(message_id) as t from messages, people where author_email_address=email_address group by mailing_list_url, top_level_domain order by t desc limit %d;' % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_people_by_tld(self):
        
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists

        query = 'select mailing_list_url, top_level_domain, count(p.email_address) as t from mailing_lists_people as ml, people as p where ml.email_address=p.email_address group by mailing_list_url, top_level_domain order by t desc limit %d;' % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()
    
    def get_messages_by_year(self):

        query = 'select mailing_list_url, year(first_date), count(*) as t from messages group by mailing_list_url, year(first_date);'
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_people_by_year(self):

        query = 'select mailing_list_url, year(first_date), count(distinct author_email_address) as t from messages,people where author_email_address=email_address group by mailing_list_url, year(first_date);'
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_messages_by_people(self):

        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists

        query = 'select mailing_list_url, author_email_address, count(*) as t from messages group by mailing_list_url,author_email_address order by t desc limit %d;' % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_total_people(self):

        query = 'select mailing_list_url, count(distinct author_email_address) as t from messages group by mailing_list_url;'
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_total_messages(self):

        query = 'select mailing_list_url, count(*) as t from messages group by mailing_list_url;'
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()
        
        
