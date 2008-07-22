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
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import MySQLdb
import sys
from pymlstats import datamodel

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
        except MySQLdb.OperationalError, e:

            # Check the error number
            errno = e.args[0]
            if 1045 == errno: # Unknown or unauthorized user
                msg = e.args[1]
                print >>sys.stderr, msg
                print >>sys.stderr, "Please check the --db-user and --db-password command line options"
                sys.exit(2)
            elif 1044 == errno: # User can not access database
                msg = e.args[1]
                print >>sys.stderr, msg
                print >>sys.stderr, "Please check the --db-user and --db-password command line options"
                sys.exit(2)
            elif 1049 == errno: # Unknown database           
                
                # Database does not exist
                # So create it
                try:
                    self.__dbobj = MySQLdb.connect(self.host,self.admin_user,self.admin_password,"")
                except MySQLdb.OperationalError, e:
                    errno = e.args[0]

                    if 1045 == errno: # Unauthorized user
                        msg = e.args[1]
                        print >>sys.stderr, msg
                        print >>sys.stderr, "Please check the --db-admin-user and --db-admin-password command line options"
                        sys.exit(1)
                    else: # Unknown exception
                        message = "ERROR: Runtime error while trying to connect to the database. Error number is "+str(e.args[0])+". Original message is "+str(e.args[1])+". I don't know how to continue after this failure. Please report the failure."
                        # Write message to the stderr
                        print >> sys.stderr, message                        
                        sys.exit(1)
                    
                cursor = self.__dbobj.cursor()
                query = "CREATE DATABASE "+self.name
                cursor.execute(query)
                query = "USE "+self.name+";"
                cursor.execute(query)
                for query in datamodel.data_model_query_list:
                    cursor.execute(query)
                self.__dbobj.commit()

                # Database created, now reconnect
                # If this point has passed the exceptions catching, it should work
                self.__dbobj = MySQLdb.connect(self.host,self.user,self.password,self.name)
                
            else: # Unknown exception
                message = "ERROR: Runtime error while trying to connect to the database. Error number is "+str(e.args[0])+". Original message is "+str(e.args[1])+". I don't know how to continue after this failure. Please report the failure."
                # Write message to the stderr
                print >> sys.stderr, message                        
                sys.exit(1)

            
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

    def next_db_peopleID(self):
        query_max='select max(people_ID) from people;'    
        self.read_cursor.execute(query_max)
        peopleID = self.read_cursor.fetchone()[0]
        if peopleID is not None:
            peopleID += 1
        else:
            peopleID = 1
        return peopleID

    def verify_peoplemail(self,peoplemail):
        #Checking if exists the email address of the people
        query_check='select people_ID from people where email_address=' + '"' + peoplemail  + '";'
        flag=self.read_cursor.execute(query_check)    
        # if 0 then not exist in the datta base this email 
        if flag > 0:
            peopleID = self.read_cursor.fetchone()[0]
        else:
            peopleID = 0
        return peopleID
    

    def insert_people(self,addr,mailing_list_url, peopleID):
        query_people_values = []
        mailing_lists_people_values = []
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

        from_values = [peopleID,email,name,username,domain_name,top_level_domain]
        query_people = 'INSERT INTO people (people_ID, email_address,name,username,domain_name,top_level_domain)'
        query_people += ' VALUES (%s,%s,%s,%s,%s,%s);'
        try:
            self.write_cursor.execute(query_people,from_values)
        except MySQLdb.IntegrityError:
            pass

        query_mailing_lists_people = 'INSERT INTO mailing_lists_people (people_ID,mailing_list_url)'
        query_mailing_lists_people += ' VALUES (%s,%s);'
        mailing_lists_people_values = [peopleID,mailing_list_url]
        try:
            self.write_cursor.execute(query_mailing_lists_people,mailing_lists_people_values)
        except MySQLdb.IntegrityError:
            # Duplicate entry email address-mailing list url
            pass



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
                    if value is None:
                        continue    
                    to_addresses += value
                elif 'cc' == h:
                    if value is None:
                        continue
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
                    if value is None:
                        continue
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
            #NEW PEOPLE_ID VALID    
            peopleID=self.next_db_peopleID()  
            for addr in to_addresses:
                peopleexist= self.verify_peoplemail(addr[1])
                if 0 == peopleexist:
                    peopleexist=peopleID
                    peopleID += 1
                    self.insert_people(addr,mailing_list_url, peopleexist)
                query = 'INSERT INTO messages_people(people_ID, type_of_recipient, message_id)'
                query += ' VALUES (%s,%s,%s);'
                messages_people_values[query] = [peopleexist,"To",message_id]
            
            for addr in cc_addresses:
                peopleexist= self.verify_peoplemail(addr[1])
                if 0 == peopleexist:
                    peopleexist=peopleID
                    peopleID +=1
                    self.insert_people(addr,mailing_list_url, peopleexist)
                query = 'INSERT INTO messages_people(people_ID,type_of_recipient,message_id)'
                query += ' VALUES (%s,%s,%s);'
                messages_people_values[query] = [peopleexist,"Cc",message_id]

            for addr in from_addresses:
                peopleexist= self.verify_peoplemail(addr[1])
                if 0 == peopleexist:
                    peopleexist=peopleID
                    peopleID +=1
                    self.insert_people(addr,mailing_list_url, peopleexist)
                query = 'INSERT INTO messages_people(people_ID,type_of_recipient,message_id)'
                query += ' VALUES (%s,%s,%s);'
                messages_people_values[query] = [peopleexist,"From",message_id]

            # Write the rest of the message
            try:
                self.write_cursor.execute(query_message,values)
            except MySQLdb.IntegrityError:
                # Duplicated message
                stored_messages -= 1
            except:
                error_message = "ERROR: Runtime error while trying to write message with message-id "+message_id+". That message has not been written to the database, but the execution has not been stopped. Please report this failure including the message-id and the URL for the mbox."
                stored_messages -= 1
                # Write message to the stderr
                print >> sys.stderr, error_message
                
            for query in messages_people_values.keys():
                try:
                    self.write_cursor.execute(query,messages_people_values[query])
                except MySQLdb.IntegrityError:
                    # Duplicate entry email_address-to|cc-mailing list url
                    pass
            self.__dbobj.commit()
            stored_messages += 1

        # Check that everything is consistent
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
        query = "select m.mailing_list_url,p.domain_name, count(m.message_id) as num_messages "\
        "  from messages m,messages_people mp, people p "\
        " where m.message_ID=mp.message_ID "\
        "   and mp.people_ID=p.people_ID and  mp.type_of_recipient='From'"\
        " group by m.mailing_list_url, p.domain_name "\
        " order by num_messages desc limit %d;" % limit

        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_people_by_domain(self):

        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists
        query = "select mailing_list_url, domain_name, count(p.email_address) as t "\
                "  from mailing_lists_people as ml, people as p "\
        " where ml.people_ID=p.people_ID group by mailing_list_url, domain_name order by t desc limit %d;" % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_messages_by_tld(self):
        
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists
        query = "select m.mailing_list_url, p.top_level_domain, count(m.message_id) as num_messages "\
        "  from messages m,messages_people mp, people p "\
        " where m.message_ID=mp.message_ID and mp.people_ID=p.people_ID and  mp.type_of_recipient='From'"\
        " group by m.mailing_list_url, p.top_level_domain "\
        " order by num_messages desc limit %d;" % limit
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_people_by_tld(self):
        
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists

        query = "select mailing_list_url, top_level_domain, count(p.email_address) as t "\
        "  from mailing_lists_people as ml, people as p "\
        " where ml.people_ID=p.people_ID group by mailing_list_url, top_level_domain"\
        " order by t desc limit %d;" % limit
        self.read_cursor.execute(query)
        
        return self.read_cursor.fetchall()
    
    def get_messages_by_year(self):

        query = 'select mailing_list_url, year(first_date), count(*) as t from messages group by mailing_list_url, year(first_date);'
        self.read_cursor.execute(query)
        
        return self.read_cursor.fetchall()

    def get_people_by_year(self):
        
        query = "select m.mailing_list_url, year(m.first_date), count(distinct(mp.people_ID)) "\
        "  from messages m , messages_people mp"\
        " where m.message_ID=mp.message_ID"\
        "   and type_of_recipient='From'"\
        " group by m.mailing_list_url, year(m.first_date);"
        self.read_cursor.execute(query)
        
        return self.read_cursor.fetchall()

    def get_messages_by_people(self):

        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = 10*mailing_lists
        query = "select m.mailing_list_url, (select email_address from people where people_ID= mp.people_ID),  count(m.message_ID) as t "\
        "  from messages m, messages_people mp "\
        " where m.message_ID = mp.message_ID "\
        "   and mp.type_of_recipient='From'"\
        " group by m.mailing_list_url,mp.people_ID " \
        " order by t desc limit %d;" % limit

        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_total_people(self):

        query = "select m.mailing_list_url, count(distinct(mp.people_ID))"\
        "  from messages m , messages_people mp"\
        " where m.message_ID=mp.message_ID"\
        "   and mp.type_of_recipient='From'"\
        " group by m. mailing_list_url;" 

        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()

    def get_total_messages(self):

        query = 'select mailing_list_url, count(*) as t from messages group by mailing_list_url;'
        self.read_cursor.execute(query)

        return self.read_cursor.fetchall()
        
                