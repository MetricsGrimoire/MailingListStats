#-*- coding:utf-8 -*-
# Copyright (C) 2007-2010 Libresoft Research Group
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>
#       Germán Poo-Caamaño <gpoo@gnome.org>

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

import sys
import pprint
from pymlstats import datamodel

class DatabaseException (Exception):
    '''Generic Database Exception'''
class DatabaseDriverNotSupported (DatabaseException):
    '''Database driver is not supported'''

class Database:
    (VISITED, NEW, FAILED) = ('visited', 'new', 'failed')

    def __init__(self):
        self.dbobj = None
        # Use this cursor to access to data in the database
        self.read_cursor = None
        # Use this cursor to dump data into the database
        self.write_cursor = None

        self.limit = 10

    def connect(self, conn):
        self.dbobj = conn
        self.read_cursor = self.dbobj.cursor()
        self.write_cursor = self.dbobj.cursor()

    def filter(self, data_address):
        if not data_address:
            return data_address

        #erase the " in the e-mail
        aux0 = data_address[0][0]
        aux1 = data_address[0][1].replace('"','')
        return ((aux0, aux1),)

    def check_compressed_file(self, url):
        query = 'SELECT status FROM compressed_files WHERE url=%s;'
        self.read_cursor.execute(query, (url,))

        if self.read_cursor.rowcount >= 1:
            status = self.read_cursor.fetchone()[0]
        else:
            status = None

        return status

    def update_mailing_list(self, url, name, last_analysis):
        q_select = '''SELECT last_analysis FROM mailing_lists
                       WHERE mailing_list_url=%s;'''
        q_insert = '''INSERT INTO mailing_lists
                      (mailing_list_url, mailing_list_name, last_analysis)
                      VALUES (%s, %s, %s);'''
        q_update = '''UPDATE mailing_lists
                      SET last_analysis=%s WHERE mailing_list_url=%s;'''

        self.read_cursor.execute(q_select, (url,))

        if self.read_cursor.rowcount >= 1:
            self.write_cursor.execute(q_update, (last_analysis, url))
        else:
            self.write_cursor.execute(q_insert, (url, name, last_analysis))

        self.dbobj.commit()

    def set_visited_url(self, url, mailing_list_url, last_analysis, status):
        q_select = '''SELECT last_analysis FROM compressed_files
                      WHERE url=%s;'''
        q_update = '''UPDATE compressed_files
                      SET status=%s, last_analysis=%s WHERE url=%s;'''
        q_insert = '''INSERT INTO compressed_files
                      (url, mailing_list_url, status, last_analysis)
                      VALUES (%s, %s, %s, %s);'''

        self.read_cursor.execute(q_select, (url,))

        if self.read_cursor.rowcount >= 1:
            # Theoretically, this code never is executed.
            values = (status, last_analysis, url)
            self.write_cursor.execute(q_update, values)
        else:
            values = (url, mailing_list_url, status, last_analysis)
            self.write_cursor.execute(q_insert, values)

        self.dbobj.commit()

    # --------------------  Reports  --------------------
    def get_num_of_mailing_lists(self):
        query = 'SELECT count(distinct mailing_list_url) FROM mailing_lists;'
        self.read_cursor.execute(query)
        return self.read_cursor.fetchone()[0]

    def get_messages_by_domain(self):
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = self.limit * mailing_lists
        query = '''SELECT m.mailing_list_url, lower(p.domain_name) as domain,
                          count(m.message_id) as num_messages
                   FROM messages m,messages_people mp, people p
                   WHERE m.message_ID = mp.message_ID
                     AND lower(mp.email_address) = lower(p.email_address)
                     AND mp.type_of_recipient = 'From'
                   GROUP BY m.mailing_list_url, domain
                   ORDER BY num_messages DESC, domain
                   LIMIT %s;'''
        self.read_cursor.execute(query, (limit,))
        return self.read_cursor.fetchall()

    def get_people_by_domain(self):
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = self.limit * mailing_lists
        query = '''SELECT mailing_list_url, lower(domain_name) as domain,
                          count(lower(p.email_address)) as t
                     FROM mailing_lists_people as ml, people as p
                    WHERE lower(ml.email_address) = lower(p.email_address)
                    GROUP BY mailing_list_url, domain
                    ORDER BY t DESC, domain
                    LIMIT %s;'''
        self.read_cursor.execute(query, (limit,))
        return self.read_cursor.fetchall()

    def get_messages_by_tld(self):
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = self.limit * mailing_lists
        query = '''SELECT m.mailing_list_url,
                          lower(p.top_level_domain) as tld,
                          count(m.message_id) as num_messages
                     FROM messages m, messages_people mp, people p
                    WHERE m.message_ID = mp.message_ID
                      AND lower(mp.email_address) = lower(p.email_address)
                      AND mp.type_of_recipient = 'From'
                    GROUP BY m.mailing_list_url, tld
                    ORDER BY num_messages DESC, tld
                    LIMIT %s;'''
        self.read_cursor.execute(query, (limit,))
        return self.read_cursor.fetchall()

    def get_people_by_tld(self):
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = self.limit * mailing_lists
        query = '''SELECT mailing_list_url, lower(top_level_domain) as tld,
                          count(p.email_address) as t
                     FROM mailing_lists_people as ml, people as p
                    WHERE lower(ml.email_address) = lower(p.email_address)
                    GROUP BY mailing_list_url, tld
                    ORDER BY t DESC, tld
                    LIMIT %s;'''
        self.read_cursor.execute(query, (limit,))
        return self.read_cursor.fetchall()

    def get_messages_by_year(self):
        query = '''SELECT mailing_list_url,
                          extract(year from first_date) as year,
                          count(*) as t
                     FROM messages
                    GROUP BY mailing_list_url, year;'''
        self.read_cursor.execute(query)
        return self.read_cursor.fetchall()

    def get_people_by_year(self):
        query = '''SELECT m.mailing_list_url,
                          extract(year from m.first_date) as year,
                          count(distinct(lower(mp.email_address)))
                     FROM messages m, messages_people mp
                    WHERE m.message_ID = mp.message_ID
                      AND type_of_recipient = 'From'
                    GROUP BY m.mailing_list_url, year;'''
        self.read_cursor.execute(query)
        return self.read_cursor.fetchall()

    def get_messages_by_people(self):
        mailing_lists = int(self.get_num_of_mailing_lists())
        limit = self.limit
        query = '''SELECT m.mailing_list_url, lower(mp.email_address) as email,
                          count(m.message_ID) as t
                     FROM messages m, messages_people mp
                    WHERE m.message_ID = mp.message_ID
                      AND mp.type_of_recipient = 'From'
                    GROUP BY m.mailing_list_url, email
                    ORDER BY t desc, email limit %s;'''
        self.read_cursor.execute(query, (limit, ))
        return self.read_cursor.fetchall()

    def get_total_people(self):
        query = '''SELECT m.mailing_list_url,
                          count(distinct(lower(mp.email_address)))
                     FROM messages m, messages_people mp
                    WHERE m.message_ID = mp.message_ID
                      AND mp.type_of_recipient = 'From'
                    GROUP BY m. mailing_list_url;'''
        self.read_cursor.execute(query)
        return self.read_cursor.fetchall()

    def get_total_messages(self):
        query = '''SELECT mailing_list_url, count(*) as t
                     FROM messages
                    GROUP BY mailing_list_url;'''
        self.read_cursor.execute(query)
        return self.read_cursor.fetchall()


class DatabaseMysql(Database):
    import MySQLdb
    dbapi = MySQLdb

    def __init__(self, dbname='', username='', password='', hostname='',
                 admin_user=None, admin_password=None):
        Database.__init__(self)

        self.name = ''
        self.user = username
        self.password = password
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.host = hostname

    def connect(self):
        try:
            db = self.dbapi.connect(self.host, self.user,
                                    self.password, self.name,
                                    charset='utf8', use_unicode=True)
        except self.dbapi.OperationalError, e:

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
                    db = self.dbapi.connect(self.host, self.admin_user,
                                            self.admin_password, '',
                                            charset='utf8', use_unicode=True)
                except self.dbapi.OperationalError, e:
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

                cursor = db.cursor()
                query = 'CREATE DATABASE %s' % self.name
                cursor.execute(query)
                query = 'USE %s' % self.name
                cursor.execute(query)
                for query in datamodel.data_model_query_list:
                    cursor.execute(query)
                db.commit()

                # Database created, now reconnect
                # If this point has passed the exceptions catching, it should work
                db = self.dbapi.connect(self.host, self.user,
                                        self.password,self.name,
                                        charset='utf8', use_unicode=True)
            else: # Unknown exception
                message = "ERROR: Runtime error while trying to connect to the database. Error number is "+str(e.args[0])+". Original message is "+str(e.args[1])+". I don't know how to continue after this failure. Please report the failure."
                # Write message to the stderr
                print >> sys.stderr, message
                sys.exit(1)

        Database.connect(self, db)

    def insert_people(self, name, email, mailing_list_url):
        try:
            top_level_domain = email.split(".")[-1]
        except IndexError:
            top_level_domain = ''
        try:
            username, domain_name = email.split('@')
        except ValueError:
            username, domain_name = ('', '')

        query_people = '''INSERT INTO people
                                      (email_address, name, username,
                                       domain_name, top_level_domain)
                          VALUES (%s, %s, %s, %s, %s);'''
        from_values = [email, name, username, domain_name, top_level_domain]
        try:
            self.write_cursor.execute(query_people, from_values)
        except self.dbapi.IntegrityError:
            pass
        except self.dbapi.DataError:
            pprint.pprint(from_values)

        query_mailing_lists_people = '''INSERT INTO mailing_lists_people
                                        (email_address, mailing_list_url)
                                        VALUES (%s, %s);'''
        mailing_lists_people_values = [email, mailing_list_url]
        try:
            self.write_cursor.execute(query_mailing_lists_people,
                                      mailing_lists_people_values)
        except self.dbapi.IntegrityError:
            # Duplicate entry email address-mailing list url
            pass
        except self.dbapi.DataError:
            pprint.pprint(mailing_lists_people_values)

    def store_messages(self, message_list, mailing_list_url):
        query = 'SET FOREIGN_KEY_CHECKS = 0;'
        self.write_cursor.execute(query)

        stored_messages = 0
        query_message = '''INSERT INTO messages (
                                   message_id, is_response_of,
                                   arrival_date, first_date, first_date_tz,
                                   mailing_list, mailing_list_url,
                                   subject, message_body)
                           VALUES (%(message-id)s, %(in-reply-to)s,
                                   %(received)s, %(date)s, %(date_tz)s,
                                   %(list-id)s, %(mailing_list_url)s,
                                   %(subject)s, %(body)s);'''
        query_m_people = '''INSERT INTO messages_people
                               (email_address, type_of_recipient, message_id)
                            VALUES (%s, %s, %s);'''

        for m in message_list:
            values = m
            values['mailing_list_url'] = mailing_list_url

            # FIXME: If primary key check fails, ignore and continue
            msgs_people_value = {}
            for header in ('from', 'to', 'cc'):
                addresses = self.filter(m[header])
                if not addresses:
                    continue

                for name, email in addresses:
                    self.insert_people(name, email, mailing_list_url)
                    key = '%s-%s' % (header, email)
                    value = (email, header.capitalize(), m['message-id'])
                    msgs_people_value.setdefault(key, value)

            # Write the rest of the message
            try:
                self.write_cursor.execute(query_message, values)
            except self.dbapi.IntegrityError:
                # Duplicated message
                stored_messages -= 1
            except:
                error_message = "ERROR: Runtime error while trying to write message with message-id '%s'. That message has not been written to the database, but the execution has not been stopped. Please report this failure including the message-id and the URL for the mbox." % m['message-id']
                stored_messages -= 1
                # Write message to the stderr
                print >> sys.stderr, error_message

            for key, values in msgs_people_value.iteritems():
                try:
                    self.write_cursor.execute(query_m_people, values)
                except self.dbapi.IntegrityError:
                    # Duplicate entry email_address-to|cc-mailing list url
                    pass
            self.dbobj.commit()
            stored_messages += 1

        # Check that everything is consistent
        query = 'SET FOREIGN_KEY_CHECKS = 1;'
        self.write_cursor.execute(query)
        self.dbobj.commit()

        return stored_messages


class DatabasePostgres(Database):
    import psycopg2
    dbapi = psycopg2

    def __init__(self, dbname='', username='', password='', hostname='',
                 admin_user=None, admin_password=None):
        Database.__init__(self)

        self.name = ''
        self.user = username
        self.password = password
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.host = hostname

    def connect(self):
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        self.host = None
        try:
            if self.host is not None:
                db = self.dbapi.connect(database=self.name,
                                        user=self.user,
                                        password=self.password,
                                        host=self.host)
            else:
                db = self.dbapi.connect(database=self.name,
                                        user=self.user)
            db.set_client_encoding('UTF8')
            db.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        except:
            raise

        Database.connect(self, db)

    def insert_people(self, name, email, mailing_list_url):
        try:
            top_level_domain = email.split(".")[-1]
        except IndexError:
            top_level_domain = ''
        try:
            username, domain_name = email.split('@')
        except ValueError:
            username, domain_name = ('', '')

        query_people = '''INSERT INTO people
                                      (email_address, name, username,
                                       domain_name, top_level_domain)
                          VALUES (%s, %s, %s, %s, %s);'''
        from_values = [email, name, username, domain_name, top_level_domain]
        try:
            self.write_cursor.execute(query_people, from_values)
        except self.dbapi.IntegrityError:
            pass
        except self.dbapi.DataError:
            pprint.pprint(from_values)
            raise

        query_mailing_lists_people = '''INSERT INTO mailing_lists_people
                                        (email_address, mailing_list_url)
                                        VALUES (%s, %s);'''
        mailing_lists_people_values = [email, mailing_list_url]
        try:
            self.write_cursor.execute(query_mailing_lists_people,
                                      mailing_lists_people_values)
        except self.dbapi.IntegrityError:
            # Duplicate entry email address-mailing list url
            pass
        except self.dbapi.DataError:
            pprint.pprint(mailing_lists_people_values)
            raise

    def store_messages(self, message_list, mailing_list_url):
        query = 'SET CONSTRAINTS ALL DEFERRED'
        self.write_cursor.execute(query)

        stored_messages = 0
        query_message = '''INSERT INTO messages (
                                   message_id, is_response_of,
                                   arrival_date, first_date, first_date_tz,
                                   mailing_list, mailing_list_url,
                                   subject, message_body)
                           VALUES (%(message-id)s, %(in-reply-to)s,
                                   %(received)s, %(date)s, %(date_tz)s,
                                   %(list-id)s, %(mailing_list_url)s,
                                   %(subject)s, %(body)s);'''
        query_m_people = '''INSERT INTO messages_people
                               (email_address, type_of_recipient, message_id)
                            VALUES (%s, %s, %s);'''

        for m in message_list:
            values = m
            values['mailing_list_url'] = mailing_list_url

            # FIXME: If primary key check fails, ignore and continue
            msgs_people_value = {}
            for header in ('from', 'to', 'cc'):
                addresses = self.filter(m[header])
                if not addresses:
                    continue

                for name, email in addresses:
                    self.insert_people(name, email, mailing_list_url)
                    key = '%s-%s' % (header, email)
                    value = (email, header.capitalize(), m['message-id'])
                    msgs_people_value.setdefault(key, value)

            # Write the rest of the message
            try:
                self.write_cursor.execute(query_message, values)
            except self.dbapi.IntegrityError:
                # Duplicated message
                stored_messages -= 1
            except self.dbapi.DataError:
                pprint.pprint(values)
                raise
            except:
                error_message = "ERROR: Runtime error while trying to write message with message-id '%s'. That message has not been written to the database, but the execution has not been stopped. Please report this failure including the message-id and the URL for the mbox." % m['message-id']
                stored_messages -= 1
                # Write message to the stderr
                print >> sys.stderr, error_message

            for key, values in msgs_people_value.iteritems():
                try:
                    self.write_cursor.execute(query_m_people, values)
                except self.dbapi.IntegrityError:
                    # Duplicate entry email_address-to|cc-mailing list url
                    pass
                except self.dbapi.DataError:
                    pprint.pprint(values)
                    raise
            self.dbobj.commit()
            stored_messages += 1

        # Check that everything is consistent
        query = 'SET CONSTRAINTS ALL IMMEDIATE'
        self.write_cursor.execute(query)
        self.dbobj.commit()

        return stored_messages


def create_database(driver='mysql', dbname='', username='', password='',
                     hostname='', admin_user=None, admin_password=None):

    drivers = { 'mysql': DatabaseMysql, 'postgres': DatabasePostgres }
    try:
        call_db = drivers[driver]
        db = call_db(dbname, username, password, hostname,
                     admin_user, admin_password)
    except:
        raise DatabaseDriverNotSupported(driver)

    return db
