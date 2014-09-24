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

import sqlalchemy
from sqlalchemy import create_engine, Column, ForeignKey, ForeignKeyConstraint
from sqlalchemy import DateTime, Enum, NUMERIC, TEXT, VARCHAR
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['Base', 'MailingLists', 'CompressedFiles', 'People',
           'Messages', 'MessagesPeople', 'MailingListsPeople']

Base = declarative_base()


def MediumText():
    return sqlalchemy.Text().with_variant(MEDIUMTEXT(), 'mysql')


class MailingLists(Base):
    __tablename__ = 'mailing_lists'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    mailing_list_url = Column(VARCHAR(191), primary_key=True)
    mailing_list_name = Column(VARCHAR(255))
    project_name = Column(VARCHAR(255))
    last_analysis = Column(DateTime)

    def __repr__(self):
        return u"<MailingLists(mailing_list_url='{0}', " \
               "mailing_list_name='{1}', project_name='{2}', " \
               "last_analysis='{3}')>".format(self.mailing_list_url,
                                              self.mailing_list_name,
                                              self.project_name,
                                              self.last_analysis)


class CompressedFiles(Base):
    __tablename__ = 'compressed_files'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    url = Column(VARCHAR(191), primary_key=True)
    mailing_list_url = Column(VARCHAR(191),
                              ForeignKey('mailing_lists.mailing_list_url'),
                              nullable=False)
    status = Column(Enum('new', 'visited', 'failed', native_enum=True,
                         name='enum_status'))
    last_analysis = Column(DateTime)

    def __repr__(self):
        return u"<CompressedFiles(url='{0}', " \
               "mailing_list_url='{1}', status='{2}' " \
               "last_analysis='{3}')>".format(self.mailing_list_url,
                                              self.mailing_list_name,
                                              self.project_name,
                                              self.last_analysis)


class People(Base):
    __tablename__ = 'people'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8mb4'}

    email_address = Column(VARCHAR(191), primary_key=True)
    name = Column(VARCHAR(255))
    username = Column(VARCHAR(255))
    domain_name = Column(VARCHAR(255))
    top_level_domain = Column(VARCHAR(255))

    def __repr__(self):
        return u"<People(email_address='{0}', name='{1}', " \
               "username='{2}' domain_name='{3}'" \
               "top_level_domain='{4}')>".format(self.email_address,
                                                 self.name,
                                                 self.username,
                                                 self.domain_name,
                                                 self.top_level_domain)


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    message_id = Column(VARCHAR(191), primary_key=True)
    mailing_list_url = Column(VARCHAR(191),
                              ForeignKey('mailing_lists.mailing_list_url',
                                         onupdate='CASCADE',
                                         ondelete='CASCADE'),
                              primary_key=True)
    mailing_list = Column(VARCHAR(255))
    first_date = Column(DateTime)
    first_date_tz = Column(NUMERIC(11))
    arrival_date = Column(DateTime)
    arrival_date_tz = Column(NUMERIC(11))
    subject = Column(VARCHAR(1024))
    message_body = Column(MediumText())
    is_response_of = Column(VARCHAR(191), index=True)
    mail_path = Column(TEXT)

    def __repr__(self):
        return u"<Messages(message_id='{0}', " \
               "mailing_list_url='{1}', " \
               "mailing_list='{2}', " \
               "first_date='{3}', first_date_tz='{4}', " \
               "arrival_date='{5}', arrival_date_tz='{6}', " \
               "subject='{7}', message_body='{8}', " \
               "is_response_of='{9}', " \
               "mail_path='{10}')>".format(self.message_id,
                                           self.mailing_list_url,
                                           self.mailing_list,
                                           self.first_date,
                                           self.first_date_tz,
                                           self.arrival_date,
                                           self.arrival_date_tz,
                                           self.subject,
                                           self.message_body,
                                           self.is_response_of,
                                           self.mail_path)


class MessagesPeople(Base):
    __tablename__ = 'messages_people'
    __table_args__ = (
                      ForeignKeyConstraint(['message_id', 'mailing_list_url'],
                                           ['messages.message_id',
                                            'messages.mailing_list_url'],
                                            onupdate='CASCADE',
                                            ondelete='CASCADE'),
                      {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
                      )

    type_of_recipient = Column(Enum('From', 'To', 'Cc',
                                    native_enum=True,
                                    name='enum_type_of_recipient'),
                               primary_key=True,
                               default='From')
    message_id = Column(VARCHAR(191),
                        primary_key=True,
                        index=True)
    mailing_list_url = Column(VARCHAR(191),
                              primary_key=True)
    email_address = Column(VARCHAR(191),
                           ForeignKey('people.email_address',
                                      onupdate='CASCADE',
                                      ondelete='CASCADE'),
                           primary_key=True)

    def __repr__(self):
        return u"<MessagesPeople(type_of_recipient='{0}', " \
               "message_id='{1}', " \
               "mailing_list_url='{1}', " \
               "email_address='{2}')>".format(self.type_of_recipient,
                                              self.message_id,
                                              self.mailing_list_url,
                                              self.email_address)


class MailingListsPeople(Base):
    __tablename__ = 'mailing_lists_people'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}

    email_address = Column(VARCHAR(191),
                           ForeignKey('people.email_address',
                                      onupdate='CASCADE',
                                      ondelete='CASCADE'),
                           primary_key=True)
    mailing_list_url = Column(VARCHAR(191),
                              ForeignKey('mailing_lists.mailing_list_url',
                                         onupdate='CASCADE',
                                         ondelete='CASCADE'),
                              primary_key=True)

    def __repr__(self):
        return u"<MailingListsPeople(email_address='{0}', " \
               "mailing_list_url='{1}')>".format(self.email_address,
                                                 self.mailing_list_url)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print 'Usage: {} <uri>'.format(sys.argv[0])
        print ' driver://user:password@host/database\n'
        print ' eg: sqlite:///:memory:'
        print '     sqlite:///mlstats.db'
        print '     mysql://user:password@localhost/mlstats'
        print '     postgres://user@/mlstats'
        sys.exit(-1)

    engine = create_engine(sys.argv[1], encoding='utf8',
                           echo=False)

    Base.metadata.create_all(engine, checkfirst=True)
