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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02111-1301, USA.
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


class DatabaseException (Exception):
    '''Generic Database Exception'''


class DatabaseDriverNotSupported (DatabaseException):
    '''Database driver is not supported'''


class GenericDatabase(object):
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
        aux1 = data_address[0][1].replace('"', '')
        return ((aux0, aux1),)

    def get_compressed_files(self, mailing_list_url):
        query = 'SELECT url FROM compressed_files WHERE mailing_list_url = %s;'
        self.read_cursor.execute(query, (mailing_list_url,))
        return [row[0] for row in self.read_cursor.fetchall()]

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
        # mailing_lists = int(self.get_num_of_mailing_lists())
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


def create_database(driver='mysql', dbname='', username='', password='',
                    hostname=None, admin_user=None, admin_password=None):
    drivers = {'mysql': 'mysql', 'postgres': 'postgresql'}

    if driver not in drivers:
        raise DatabaseDriverNotSupported(driver)

    backend = 'pymlstats.db.%s' % drivers[driver]
    module = __import__(backend, fromlist=['Database'])

    try:
        db = module.Database(dbname, username, password, hostname,
                             admin_user, admin_password)
    except:
        raise

    return db
