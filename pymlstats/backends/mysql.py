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
import MySQLdb as dbapi

from pymlstats.backends import datamodel
from pymlstats.database import GenericDatabase


class Database(GenericDatabase):

    def __init__(self, dbname='', username='', password='', hostname='',
                 admin_user=None, admin_password=None):
        GenericDatabase.__init__(self)

        self.name = dbname
        self.user = username
        self.password = password
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.host = hostname or 'localhost'

    def connect(self):
        check_options_msg = "Please check the --db-user and " \
                            "--db-password command line options"

        try:
            db = dbapi.connect(self.host, self.user,
                               self.password, self.name,
                               charset='utf8', use_unicode=True)
        except dbapi.OperationalError, e:

            # Check the error number
            errno = e.args[0]
            if 1045 == errno:  # Unknown or unauthorized user
                msg = e.args[1]
                print >>sys.stderr, msg
                print >>sys.stderr, check_options_msg
                sys.exit(2)
            elif 1044 == errno:  # User can not access database
                msg = e.args[1]
                print >>sys.stderr, msg
                print >>sys.stderr, check_options_msg
                sys.exit(2)
            elif 1049 == errno:  # Unknown database
                # Database does not exist
                # So create it
                try:
                    db = dbapi.connect(self.host, self.admin_user,
                                       self.admin_password, '',
                                       charset='utf8', use_unicode=True)
                except dbapi.OperationalError, e:
                    errno = e.args[0]

                    if 1045 == errno:  # Unauthorized user
                        msg = e.args[1]
                        print >>sys.stderr, msg
                        print >>sys.stderr, check_options_msg
                        sys.exit(1)
                    else:  # Unknown exception
                        message = """ERROR: Runtime error while trying to
                        connect to the database. Error number is '%s'.
                        Original message is '%s'. I don't know how to
                        continue after this failure. Please report the
                        failure.""" % (str(e.args[0]), str(e.args[1]))

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
                # If this point has passed the exceptions catching,
                # it should work
                db = dbapi.connect(self.host, self.user,
                                   self.password, self.name,
                                   charset='utf8', use_unicode=True)
            else:  # Unknown exception
                message = """ERROR: Runtime error while trying to connect to
                the database. Error number is '%s'. Original
                message is '%s'. I don't know how to continue
                after this failure. Please report the
                failure.""" % (str(e.args[0]), str(e.args[1]))

                # Write message to the stderr
                print >> sys.stderr, message
                sys.exit(1)

        GenericDatabase.connect(self, db)

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
        except dbapi.IntegrityError:
            pass
        except dbapi.DataError:
            pprint.pprint(from_values)

        query_mailing_lists_people = '''INSERT INTO mailing_lists_people
                                        (email_address, mailing_list_url)
                                        VALUES (%s, %s);'''
        mailing_lists_people_values = [email, mailing_list_url]
        try:
            self.write_cursor.execute(query_mailing_lists_people,
                                      mailing_lists_people_values)
        except dbapi.IntegrityError:
            # Duplicate entry email address-mailing list url
            pass
        except dbapi.DataError:
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
            except dbapi.IntegrityError:
                # Duplicated message
                stored_messages -= 1
            except:
                error_message = """ERROR: Runtime error while trying to write
                message with message-id '%s'. That message has not been written
                to the database, but the execution has not been stopped. Please
                report this failure including the message-id and the URL for
                the mbox.""" % m['message-id']

                stored_messages -= 1
                # Write message to the stderr
                print >> sys.stderr, error_message

            for key, values in msgs_people_value.iteritems():
                try:
                    self.write_cursor.execute(query_m_people, values)
                except dbapi.IntegrityError:
                    # Duplicate entry email_address-to|cc-mailing list url
                    pass
            self.dbobj.commit()
            stored_messages += 1

        # Check that everything is consistent
        query = 'SET FOREIGN_KEY_CHECKS = 1;'
        self.write_cursor.execute(query)
        self.dbobj.commit()

        return stored_messages
