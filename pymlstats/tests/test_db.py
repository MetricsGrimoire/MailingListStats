# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Germán Poo-Caamaño <gpoo@gnome.org>
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
# Authors : Germán Poo-Caamaño <gpoo@gnome.org>

import unittest
import os

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

# from pymlstats import analyzer
from pymlstats.db.database import Base, MailingLists, CompressedFiles


CUR_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(CUR_DIR, 'data')
DB_NAME = '__mlstats_unit_tests'


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.driver = os.getenv('DB')
        dbname = ':memory:' if self.driver == 'sqlite' else DB_NAME
        # Ask for DBUSER and DBPASSWORD in case of running the unit test
        # in a different setting (local). 'None' is enough for Travis,
        # which is what os.getenv() returns if the variable is undefined.
        user = os.getenv('DBUSER')
        password = os.getenv('DBPASSWORD')
        host = None

        drv = URL(self.driver, user, password, host, database=dbname)
        self.engine = create_engine(drv, encoding='utf8', convert_unicode=True)

        Base.metadata.create_all(self.engine, checkfirst=True)

        Session = sessionmaker()
        Session.configure(bind=self.engine)

        self.connection = self.engine.connect()

        # begin a non-ORM transaction
        self.transaction = self.connection.begin()

        self.session = Session(bind=self.connection)

        self.setup_mailing_lists()
        self.setup_compressed_files()

    def tearDown(self):
        self.transaction.rollback()
        Base.metadata.drop_all(self.engine)
        self.connection.close()

    def setup_mailing_lists(self):
        url = 'http://foo.bar.org/dev-list'
        name = 'dev-list'
        last_analysis = datetime.today()

        self.ml = MailingLists(mailing_list_url=url,
                               mailing_list_name=name,
                               last_analysis=last_analysis)
        self.session.add(self.ml)
        self.session.commit()

    def setup_compressed_files(self):
        url = 'http://foo.bar.org/dev-list/file-1.gz'
        ml_url = 'http://foo.bar.org/dev-list'
        status = 'visited'
        last_analysis = datetime.today()

        self.cf = CompressedFiles(url=url, mailing_list_url=ml_url,
                                  status=status, last_analysis=last_analysis)
        self.session.add(self.cf)
        self.session.commit()

    def test_query_mailing_lists(self):
        '''Insert into MailingLists using ORM'''
        expected = [self.ml]
        result = self.session.query(MailingLists).all()
        self.assertEqual(result, expected)

    def test_query_compressed_files(self):
        '''Insert into CompressedFiles using ORM'''
        expected = [self.cf]
        result = self.session.query(CompressedFiles).all()
        self.assertEqual(result, expected)
