#-*- coding:utf-8 -*-
# Copyright (C) 2014 Germán Poo-Caamaño <gpoo@calcifer.org>
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

"""
This module contains a the definition of the generic SQL tables used
by mlstats.
"""

from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError, DataError
import logging

import database as db


class Database(object):
    (VISITED, NEW, FAILED) = ('visited', 'new', 'failed')

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.WARN)

    @staticmethod
    def create_engine(engine=None):
        engine = create_engine(engine or 'sqlite:///:memory:')
        return engine

    @staticmethod
    def create_tables(engine, checkfirst=True):
        db.Base.metadata.create_all(engine, checkfirst=checkfirst)

    @staticmethod
    def drop_tables(engine):
        db.Base.metadata.drop_all(engine)

    def truncate(self, text, width=None):
        if width and len(text) > width:
            text = text[:width-3] + '...'
        return text

    def filter(self, address):
        if not address:
            return address

        # remove double quotes (") from the e-mail
        aux0 = address[0][0]
        aux1 = address[0][1].replace('"', '')
        return ((aux0, aux1),)

    def set_session(self, session):
        self.session = session

    def insert_people(self, name, email):
        tld = get_top_level_domain_from_email(email)
        user, domain = get_user_and_domain_from_email(email)

        people = db.People(email_address=email, name=name, username=user,
                           domain_name=domain, top_level_domain=tld)
        try:
            self.session.add(people)
            self.session.commit()
        except IntegrityError:
            self.log.debug(self.truncate(u'Integrity: {}'.format(people), 68))
            self.session.rollback()
        except DataError:
            self.log.warning(u'DataError: {}'.format(people))

    def insert_mailing_list_people(self, email, mailing_list_url):
        mlp = db.MailingListsPeople(email_address=email,
                                    mailing_list_url=mailing_list_url)
        try:
            self.session.add(mlp)
            self.session.commit()
        except IntegrityError:
            self.log.debug(self.truncate(u'Integrity: {}'.format(mlp), 68))
            self.session.rollback()
        except DataError:
            self.log.warning(u'DataError: {}'.format(mlp))

    def insert_messages_people(self, msg_people_value):
        msg_people = db.MessagesPeople(type_of_recipient=msg_people_value[1],
                                       email_address=msg_people_value[0],
                                       message_id=msg_people_value[2],
                                       mailing_list_url=msg_people_value[3])

        try:
            self.session.add(msg_people)
            self.session.commit()
        except IntegrityError:
            self.log.debug(self.truncate(u'Integrity: {}'.format(msg_people),
                                         68))
            self.session.rollback()
        except DataError:
            self.log.warning(u'DataError: {}'.format(msg_people))

    def insert_messages(self, message, mailing_list_url):
        result = 0
        msg = db.Messages(message_id=message['message-id'],
                          mailing_list_url=mailing_list_url,
                          mailing_list=message['list-id'],
                          first_date=message['date'],
                          first_date_tz=message['date_tz'],
                          arrival_date=message['received'],
                          subject=message['subject'],
                          message_body=message['body'],
                          is_response_of=message['in-reply-to'])
        try:
            self.session.add(msg)
            self.session.commit()
            result = 1
        except IntegrityError:
            self.log.debug(self.truncate(u'Integrity: {}'.format(msg), 68))
            self.session.rollback()
            result = -1
        except DataError:
            self.log.warning(u'DataError: {}'.format(msg))
            result = -2

        return result

    def store_messages(self, message_list, mailing_list_url):
        stored_messages = 0
        duplicated_messages = 0
        error_messages = 0

        for m in message_list:
            msgs_people_value = {}
            for header in ('from', 'to', 'cc'):
                addresses = self.filter(m[header])
                if not addresses:
                    continue

                for name, email in addresses:
                    self.insert_people(name, email)
                    self.insert_mailing_list_people(email, mailing_list_url)
                    key = '%s-%s' % (header, email)
                    value = (email, header.capitalize(), m['message-id'],
                             mailing_list_url)
                    msgs_people_value.setdefault(key, value)

            # Write the rest of the message
            insert_result = self.insert_messages(m,  mailing_list_url)

            # Everything works fine
            if insert_result > 0:
                stored_messages += insert_result

            # IntegrityError
            elif insert_result == -1:
                duplicated_messages += 1
                continue

            # DataError
            elif insert_result == -2:
                error_messages += 1

            for key, value in msgs_people_value.iteritems():
                self.insert_messages_people(value)

        return stored_messages, duplicated_messages, error_messages

    def update_mailing_list(self, url, name, last_analysis):
        """
        q_select = '''SELECT last_analysis FROM mailing_lists
                       WHERE mailing_list_url=%s;'''
        q_insert = '''INSERT INTO mailing_lists
                      (mailing_list_url, mailing_list_name, last_analysis)
                      VALUES (%s, %s, %s);'''
        q_update = '''UPDATE mailing_lists
                      SET last_analysis=%s WHERE mailing_list_url=%s;'''
        """

        ml = db.MailingLists(mailing_list_url=url,
                             mailing_list_name=name,
                             last_analysis=last_analysis)

        self.session.merge(ml)
        self.session.commit()

    def set_visited_url(self, url, mailing_list_url, last_analysis, status):
        """
        q_select = '''SELECT last_analysis FROM compressed_files
                      WHERE url=%s;'''
        q_update = '''UPDATE compressed_files
                      SET status=%s, last_analysis=%s WHERE url=%s;'''
        q_insert = '''INSERT INTO compressed_files
                      (url, mailing_list_url, status, last_analysis)
                      VALUES (%s, %s, %s, %s);'''
        """

        cf = db.CompressedFiles(url=url,
                                mailing_list_url=mailing_list_url,
                                last_analysis=last_analysis,
                                status=status)

        self.session.merge(cf)
        self.session.commit()

    def get_compressed_files(self, mailing_list_url):
        cf = aliased(db.CompressedFiles)
        ret = self.session.query(cf)\
                          .filter(cf.mailing_list_url==mailing_list_url)
        return ret.all()

    def check_compressed_file(self, url):
        cf = aliased(db.CompressedFiles)
        ret = self.session.query(cf.status).filter(cf.url == url).all()

        status = ret[0] if len(ret) > 0 else None
        return status


def get_top_level_domain_from_email(email):
    try:
        top_level_domain = email.split('.')[-1]
    except IndexError:
        top_level_domain = ''

    return top_level_domain


def get_user_and_domain_from_email(email):
    try:
        username, domain_name = email.split('@')
    except ValueError:
        username, domain_name = ('', '')

    return username, domain_name


if __name__ == '__main__':
    import sys
    from sqlalchemy import create_engine

    if len(sys.argv) < 2:
        print 'Usage: {} <uri>'.format(sys.argv[0])
        print ' driver://user:password@host/database\n'
        print ' eg: sqlite:///:memory:'
        print '     sqlite:///mlstats.db'
        print '     mysql://user@password@localhost/mlstats'
        print '     postgres://user@/mlstats'
        sys.exit(-1)

    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

    engine = create_engine(sys.argv[1], encoding='utf8')

    Database.create_tables(engine, checkfirst=True)
