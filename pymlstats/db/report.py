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

from sqlalchemy import func, extract
from sqlalchemy.sql.expression import label
from sqlalchemy.orm import aliased

import database as db
from session import Database


class Report(Database):

    def __init__(self):
        Database.__init__(self)

    def get_num_of_mailing_lists(self, session):
        '''SELECT count(distinct mailing_list_url)
             FROM mailing_lists;'''
        ml = aliased(db.MailingLists)
        ret = session.query(func.count(func.distinct(ml.mailing_list_url)))
        return ret.first()

    def get_messages_by_domain(self, session, limit=10):
        '''SELECT m.mailing_list_url, lower(p.domain_name) as domain,
                  count(m.message_id) as num_messages
             FROM messages m,messages_people mp, people p
            WHERE m.message_ID = mp.message_ID
              AND lower(mp.email_address) = lower(p.email_address)
              AND mp.type_of_recipient = 'From'
            GROUP BY m.mailing_list_url, domain
            ORDER BY num_messages DESC, domain
            LIMIT %s;'''
        mailing_lists = int(self.get_num_of_mailing_lists(session)[0])
        limit = limit * mailing_lists

        m = aliased(db.Messages)
        mp = aliased(db.MessagesPeople)
        p = aliased(db.People)
        ret = session.query(m.mailing_list_url,
                            label('domain', func.lower(p.domain_name)),
                            func.count(m.message_id)) \
            .filter(m.message_id == mp.message_id) \
            .filter(func.lower(mp.email_address) ==
                    func.lower(p.email_address)) \
            .filter(mp.type_of_recipient == 'From') \
            .group_by(m.mailing_list_url,
                      func.lower(p.domain_name)) \
            .order_by(func.count(m.message_id).desc(),
                      func.lower(p.domain_name)) \
            .limit(limit)
        return ret.all()

    def get_people_by_domain(self, session, limit=10):
        '''SELECT mailing_list_url, lower(domain_name) as domain,
                  count(lower(p.email_address)) as t
             FROM mailing_lists_people as ml, people as p
            WHERE lower(ml.email_address) = lower(p.email_address)
            GROUP BY mailing_list_url, domain
            ORDER BY t DESC, domain
            LIMIT %s;'''

        mailing_lists = int(self.get_num_of_mailing_lists(session)[0])
        limit = limit * mailing_lists

        mlp = aliased(db.MailingListsPeople)
        p = aliased(db.People)
        ret = session.query(mlp.mailing_list_url,
                            label('domain', func.lower(p.domain_name)),
                            func.count(func.lower(p.email_address))) \
            .filter(func.lower(mlp.email_address) ==
                    func.lower(p.email_address)) \
            .group_by(mlp.mailing_list_url,
                      func.lower(p.domain_name)) \
            .order_by(func.count(func.lower(p.email_address)).desc(),
                      func.lower(p.domain_name)) \
            .limit(limit)
        return ret.all()

    def get_messages_by_tld(self, session, limit=10):
        '''SELECT m.mailing_list_url,
                  lower(p.top_level_domain) as tld,
                  count(m.message_id) as num_messages
             FROM messages m, messages_people mp, people p
            WHERE m.message_ID = mp.message_ID
              AND lower(mp.email_address) = lower(p.email_address)
              AND mp.type_of_recipient = 'From'
            GROUP BY m.mailing_list_url, tld
            ORDER BY num_messages DESC, tld
            LIMIT %s;'''

        mailing_lists = int(self.get_num_of_mailing_lists(session)[0])
        limit = limit * mailing_lists

        m = aliased(db.Messages)
        mp = aliased(db.MessagesPeople)
        p = aliased(db.People)
        ret = session.query(m.mailing_list_url,
                            label('tld', func.lower(p.top_level_domain)),
                            func.count(m.message_id)) \
            .filter(m.message_id == mp.message_id) \
            .filter(func.lower(mp.email_address) ==
                    func.lower(p.email_address)) \
            .filter(mp.type_of_recipient == 'From') \
            .group_by(m.mailing_list_url,
                      func.lower(p.top_level_domain)) \
            .order_by(func.count(m.message_id).desc(),
                      func.lower(p.top_level_domain)) \
            .limit(limit)
        return ret.all()

    def get_people_by_tld(self, session, limit=10):
        '''SELECT mailing_list_url, lower(top_level_domain) as tld,
                  count(p.email_address) as t
             FROM mailing_lists_people as ml, people as p
            WHERE lower(ml.email_address) = lower(p.email_address)
            GROUP BY mailing_list_url, tld
            ORDER BY t DESC, tld
            LIMIT %s;'''

        mailing_lists = int(self.get_num_of_mailing_lists(session)[0])
        limit = limit * mailing_lists

        mlp = aliased(db.MailingListsPeople)
        p = aliased(db.People)
        ret = session.query(mlp.mailing_list_url,
                            label('tld', func.lower(p.top_level_domain)),
                            func.count(p.email_address)) \
            .filter(func.lower(mlp.email_address) ==
                    func.lower(p.email_address)) \
            .group_by(mlp.mailing_list_url,
                      func.lower(p.top_level_domain)) \
            .order_by(func.count(p.email_address).desc(),
                      func.lower(p.top_level_domain)) \
            .limit(limit)
        return ret.all()

    def get_messages_by_year(self, session):
        '''SELECT m.mailing_list_url,
                  extract(year from m.first_date) as year,
                  count(distinct(lower(mp.email_address)))
             FROM messages m, messages_people mp
            WHERE m.message_ID = mp.message_ID
              AND type_of_recipient = 'From'
            GROUP BY m.mailing_list_url, year;'''

        ret = session.query(db.Messages.mailing_list_url,
                            extract('year', db.Messages.first_date),
                            func.count(db.Messages.mailing_list_url)) \
            .group_by(db.Messages.mailing_list_url,
                      extract('year', db.Messages.first_date)) \
            .order_by(db.Messages.mailing_list_url,
                      extract('year', db.Messages.first_date))
        return ret.all()

    def get_people_by_year(self, session):
        '''SELECT m.mailing_list_url,
                  extract(year from m.first_date) as year,
                  count(distinct(lower(mp.email_address)))
             FROM messages m, messages_people mp
            WHERE m.message_ID = mp.message_ID
              AND type_of_recipient = 'From'
                    GROUP BY m.mailing_list_url, year;'''

        m = aliased(db.Messages)
        mp = aliased(db.MessagesPeople)
        ret = session.query(m.mailing_list_url,
                            extract('year', m.first_date),
                            func.count(func.distinct(
                                func.lower(mp.email_address)))) \
            .filter(m.message_id == mp.message_id) \
            .filter(mp.type_of_recipient == 'From') \
            .group_by(m.mailing_list_url,
                      extract('year', m.first_date))
        return ret.all()

    def get_messages_by_people(self, session, limit=10):
        '''SELECT m.mailing_list_url, lower(mp.email_address) as email,
                  count(m.message_ID) as t
             FROM messages m, messages_people mp
            WHERE m.message_ID = mp.message_ID
              AND mp.type_of_recipient = 'From'
            GROUP BY m.mailing_list_url, email
            ORDER BY t desc, email limit %s;'''

        m = aliased(db.Messages)
        mp = aliased(db.MessagesPeople)
        ret = session.query(m.mailing_list_url,
                            label('email', func.lower(mp.email_address)),
                            label('t', func.count(m.message_id))) \
            .filter(m.message_id == mp.message_id) \
            .filter(mp.type_of_recipient == 'From') \
            .group_by(m.mailing_list_url,
                      func.lower(mp.email_address)) \
            .order_by(func.count(m.message_id).desc(),
                      func.lower(mp.email_address)) \
            .limit(limit)
        return ret.all()

    def get_total_people(self, session):
        '''SELECT m.mailing_list_url,
                  count(distinct(lower(mp.email_address)))
             FROM messages m, messages_people mp
            WHERE m.message_ID = mp.message_ID
              AND mp.type_of_recipient = 'From'
            GROUP BY m. mailing_list_url;'''

        m = aliased(db.Messages)
        mp = aliased(db.MessagesPeople)
        ret = session.query(m.mailing_list_url,
                            func.count(func.distinct(
                                func.lower(mp.email_address)))) \
            .filter(m.message_id == mp.message_id) \
            .filter(mp.type_of_recipient == 'From') \
            .group_by(m.mailing_list_url)
        return ret.all()

    def get_total_messages(self, session):
        '''SELECT mailing_list_url, count(*) as t
             FROM messages
            GROUP BY mailing_list_url;'''

        ret = session.query(db.Messages.mailing_list_url,
                            func.count(db.Messages.mailing_list_url)) \
            .group_by(db.Messages.mailing_list_url)
        return ret.all()

    def determine_longest_values(self, keyed_tuple, callbacks):
        """
        Function to determine the longest length of the content of the
        various columns. If you want to display a table in CLI, you have
        to know what is the longest value of this column.
        Otherwise it is not possible to adjust the
        header length of this column.

        :param list keyed_tuple: List of sqlalchemy.util._collections.KeyedTuple objects (database results)
        :param dict callbacks: Callbacks to execute before measuring the length of a value
                               This is needed, to get the displayed and not the real content length.
        :return: dict
        """

        # Determine how many attributes are in one row
        num_of_attributes = len(keyed_tuple[0])

        # Initialize the max length of attributes with 0
        value_length = {}
        for i in range(0, num_of_attributes):
            value_length[i] = 0

        # Loop over every row + every attribute to determine the length
        # If there is a callback defined for a number of attribute, execute this first
        for row in keyed_tuple:
            for i in range(0, num_of_attributes):

                if i in callbacks:
                    attribute_length = len(str(callbacks[i](row[i])))
                else:
                    attribute_length = len(str(row[i]))

                if value_length[i] < attribute_length:
                    value_length[i] = attribute_length

        return value_length

    def get_mailinglist_name_by_url(self, url):
        """
        Function to strip the name of a mailing list by the url.

        :param string url: A mailinglist url. E.g. "http://lists.typo3.org/pipermail/typo3-ug-koeln"
        :return: string The name of the mailinglist. E.g. "typo3-ug-koeln"
        """
        return url.rstrip('/').split('/')[-1]

    def column_value(self, value, max_value_length, min_column_value):
        """
        Function to adjust content of a column according to the displayed length of the table / value

        :param string value: Content of the table column
        :param integer max_value_length: Maximum length of a value in this column
        :param integer min_column_value: Minimum length of this column
        :return: string The adjusted content of the column, maybe adjusted with additional whitespace
        """
        ljust = min_column_value
        if max_value_length > ljust:
            ljust = max_value_length

        column = str(value).ljust(ljust, ' ')
        return column

    def print_brief_report(self, session=None, report_filename=None):
        session = session or self.session

        # total_lists = self.get_num_of_mailing_lists(session)  # Unused
        messages_by_domain = self.get_messages_by_domain(session)
        people_by_domain = self.get_people_by_domain(session)
        messages_by_tld = self.get_messages_by_tld(session)
        people_by_tld = self.get_people_by_tld(session)
        messages_by_year = self.get_messages_by_year(session)
        people_by_year = self.get_people_by_year(session)
        messages_by_people = self.get_messages_by_people(session)
        total_people = self.get_total_people(session)
        total_messages = self.get_total_messages(session)

        # Define a callback for the first row
        callbacks = {
            0: self.get_mailinglist_name_by_url
        }

        output = '\nMLStats report\n'
        output += '--------------\n'

        #
        # Total messages by domain name (only top 10 per list)
        #
        column_length = self.determine_longest_values(messages_by_domain, callbacks)
        output += '\n' \
                  'Total messages by domain name (only top 10 per list):\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('Domain name',      column_length[1], 11) + '\t' \
                  + '#  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',      column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, domain, num in messages_by_domain:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,     column_length[0], 16),
                self.column_value(domain, column_length[1], 11),
                num
            )

        #
        # Total people posting by domain name (only top 10 per list)
        #
        column_length = self.determine_longest_values(people_by_domain, callbacks)
        output += '\n\n' \
                  'Total people posting by domain name ' \
                  '(only top 10 per list):'
        output += '\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('Domain name',    column_length[1], 11) + '\t' \
                  + '#  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',    column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, domain, num in people_by_domain:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,     column_length[0], 16),
                self.column_value(domain, column_length[1], 11),
                num
            )

        #
        # Total messages by top level domain (only top 10 per list)
        #
        column_length = self.determine_longest_values(messages_by_tld, callbacks)
        output += '\n\n' \
                  'Total messages by top level domain (only top 10 per list):' \
                  '\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('    TLD    ',      column_length[1], 11) + '\t' \
                  + '#  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',      column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, tld, num in messages_by_tld:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,  column_length[0], 16),
                self.column_value(tld, column_length[1], 11),
                num
            )

        #
        # Total people posting by top level domain (only top 10 per list)
        #
        column_length = self.determine_longest_values(people_by_tld, callbacks)
        output += '\n\n' \
                  'Total people posting by top level domain (only top 10 per list):\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('    TLD    ',      column_length[1], 11) + '\t' \
                  + ' #  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',      column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, tld, num in people_by_tld:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,  column_length[0], 16),
                self.column_value(tld, column_length[1], 11),
                num
            )

        #
        # Total messages by year
        #
        column_length = self.determine_longest_values(messages_by_year, callbacks)
        output += '\n\nTotal messages by year:\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('    Year   ',      column_length[1], 11) + '\t' \
                  + ' #  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',      column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, year, num in messages_by_year:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,        column_length[0], 16),
                self.column_value(int(year), column_length[1], 11),
                num
            )

        #
        # Total people posting by year
        #
        column_length = self.determine_longest_values(people_by_year, callbacks)
        output += '\n\nTotal people posting by year:\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('    Year   ',      column_length[1], 11) + '\t' \
                  + ' #  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',      column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, year, num in people_by_year:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,        column_length[0], 16),
                self.column_value(int(year), column_length[1], 11),
                num
            )

        #
        # Total messages by email address (only top 10 in total)
        #
        column_length = self.determine_longest_values(messages_by_people, callbacks)
        output += '\n\n' \
                  'Total messages by email address (only top 10 in total):\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + self.column_value('   Email   ',      column_length[1], 11) + '\t' \
                  + ' #  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + self.column_value('-----------',      column_length[1], 11) + '\t' \
                  + '----\n'
        for ml, email, num in messages_by_people:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\t{2}\n'.format(
                self.column_value(ml,    column_length[0], 16),
                self.column_value(email, column_length[1], 11),
                num
            )

        #
        # Total people posting in each list
        #
        column_length = self.determine_longest_values(total_people, callbacks)
        output += '\n\nTotal people posting in each list:\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + ' #  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + '----\n'
        for ml, num in total_people:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\n'.format(
                self.column_value(ml, column_length[0], 16),
                num
            )

        #
        # Total messages in each list
        #
        column_length = self.determine_longest_values(total_messages, callbacks)
        output += '\n\nTotal messages in each list:\n' \
                  + self.column_value('Mailing list    ', column_length[0], 16) + '\t' \
                  + ' #  \n' \
                  + self.column_value('----------------', column_length[0], 16) + '\t' \
                  + '----\n'
        for ml, num in total_messages:
            ml = self.get_mailinglist_name_by_url(ml)
            output += '{0}\t{1}\n'.format(
                self.column_value(ml, column_length[0], 16),
                num
            )

        output += "\n\n\n" \
                  "MLStats, Copyright (C) 2007-2010 Libresoft Research Group\n\n" \
                  "MLStats is Open Source Software/Free Software, licensed under the GNU GPL.\n" \
                  "MLStats comes with ABSOLUTELY NO WARRANTY, and you are welcome to " \
                  "redistribute it under certain conditions as specified by the GNU GPL license " \
                  "see the documentation for details.\n" \
                  "Please credit this data as generated using Libresoft's 'MLStats'."

        if report_filename:
            print u"Report written to {}".format(report_filename)
            with open(report_filename, 'w') as f:
                f.write(output)
        else:
            print output


if __name__ == '__main__':
    import sys
    import logging
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

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

    Session = sessionmaker()
    Session.configure(bind=engine)

    session = Session()

    report = Report()
    report.set_session(session)
    report.print_brief_report()
