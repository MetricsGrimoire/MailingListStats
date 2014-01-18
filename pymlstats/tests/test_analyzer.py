# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Germán Poo-Caamaño <gpoo@gnome.org>
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
# Authors : Germán Poo-Caamaño <gpoo@gnome.org>

import unittest
import os

from pymlstats import analyzer

CUR_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(CUR_DIR, 'data')


class MailArchiveAnalyzerEncodingTest(unittest.TestCase):
    def get_analyzer(self, path, **kwargs):
        fname = os.path.join(DATA_PATH, path)
        return analyzer.MailArchiveAnalyzer(filepath=fname)

    def check_single_message(self, expected, messages):
        for key, value in expected.items():
            output = u"{}:\n" \
                     u"\tExpected: '{}'\n" \
                     u"\tObtained: '{}'".format(key, value, messages[0][key])
            self.assertEqual(value, messages[0][key], output)

    def test_single_message_no_encoding(self):
        maa = self.get_analyzer('pharo-single.mbox')
        messages, non_parsed = maa.get_messages()
        expected = {
            'body': u'Hi!\n\nA message in English, with a signature '
                    u'with a different encoding.\n\nregards, G?ran'
                    u'\n\n\n\n',
            'content-type': None,
            'date': '2010-12-01 14:26:40',
            'date_tz': '3600',
            'in-reply-to': None,
            'list-id': None,
            'message-id': u'<4CF64D10.9020206@domain.com>',
            'received': None,
            'references': None,
            'subject': u'[List-name] Protocol Buffers anyone?',
            'from': [(u'Göran Lastname', u'goran@domain.com')],
            'to': None,
            'cc': None,
        }

        self.assertEqual(1, len(messages), '# of messages')
        self.check_single_message(expected, messages)
        self.assertEqual(0, non_parsed, 'non_parsed')

    def test_single_message_with_quoted_printable_encoding(self):
        '''Content-Transfer-Encoding: Quoted-printable'''
        maa = self.get_analyzer('gnome-quoted-printable.mbox')
        messages, non_parsed = maa.get_messages()
        expected = {  # noqa
            'content-type': u'text/plain; charset=utf-8',
            'date': '2008-03-17 10:35:05',
            'date_tz': '3600',
            'in-reply-to':
                u'<1205676169.6819.27.camel@user-computer.NETWORK> '
                u'(Simos\n\tXenitellis\'s message of "Sun\\, 16 Mar 2008 '
                u'14\\:02\\:49 +0000")',
            'list-id':
                u'GNOME Desktop Development List '
                u'<desktop-devel-list.gnome.org>',
            'message-id': u'<87iqzlofqu.fsf@avet.kvota.net>',
            'received': None,
            'references':
               u'<1204225143.12769.9.camel@localhost.localdomain>\n'
               u'\t<1204236062.14337.5.camel@localhost.localdomain>',
            'subject': u'Re: Low memory hacks',
            'from': [(u'Danilo Šegan', u'danilo@gnome.org')],
            'to': [(u'Simos Xenitellis', u'simos.lists@googlemail.com')],
            'cc': [('', u'desktop-devel-list@gnome.org'),
                   (u'Nikolay V. Shmyrev', u'nshmyrev@yandex.ru'),
                   (u'Brian Nitz', u'Brian.Nitz@sun.com'),
                   (u'Bastien Nocera', u'hadess@hadess.net')],
        }

        self.assertEqual(1, len(messages), '# of messages')
        self.check_single_message(expected, messages)
        self.assertEqual(0, non_parsed, 'non_parsed')

    def test_single_message_with_8_bit_encoding(self):
        '''Content-Transfer-Encoding: 8bit'''
        maa = self.get_analyzer('gnome-8-bit.mbox')
        messages, non_parsed = maa.get_messages()
        expected = {  # noqa
            'body':
                u'El lun, 17-03-2008 a las 10:35 +0100, Danilo Šegan escribió:'
                u'\n> Hi Simos,\n'
                u'> \n\n'
                u'Hi,\n\n'
                u'[...]\n\n'
                u'Cheers.\n\n'
                u'> _______________________________________________\n'
                u'> desktop-devel-list mailing list\n'
                u'> desktop-devel-list@gnome.org\n'
                u'> http://mail.gnome.org/mailman/listinfo/desktop-devel-list'
                u'\n\n',
            'content-type': u'text/plain; charset=utf-8',
            'date': '2008-03-17 11:19:29',
            'date_tz': '3600',
            'in-reply-to': u'<87iqzlofqu.fsf@avet.kvota.net>',
            'list-id':
                u'GNOME Desktop Development List '
                u'<desktop-devel-list.gnome.org>',
            'message-id': u'<1205749169.7470.2.camel@aragorn>',
            'received': None,
            'references':
                u'<1204225143.12769.9.camel@localhost.localdomain>\n'
                u'\t<1204236062.14337.5.camel@localhost.localdomain>\n'
                u'\t<47C80957.6010804@sun.com> '
                u'<1204295876.30088.14.camel@t25>\n'
                u'\t<1205676169.6819.27.camel@user-computer.NETWORK>',
            'subject': u'Re: Low memory hacks',
            'from': [(u'Carlos Perelló Marín', u'carlos@gnome.org')],
            'to': [(u'Danilo Šegan', u'danilo@gnome.org')],
            'cc': [(u'Nikolay V. Shmyrev', u'nshmyrev@yandex.ru'),
                   (u'Brian Nitz', u'Brian.Nitz@sun.com'),
                   ('', u'desktop-devel-list@gnome.org'),
                   (u'Danilo Šegan', u'danilo@gnome.org'),
                   (u'Dmitry G. Mastrukov Дмитрий Геннадьевич Мастрюков',
                    u'dmitry@taurussoft.org'),
                   (u'Ing. Rafael de Jesús Fernández M.',
                    u'rafael@ipicyt.edu.mx')]
        }

        self.assertEqual(1, len(messages), '# of messages')
        self.check_single_message(expected, messages)
        self.assertEqual(0, non_parsed, 'non_parsed')

    def test_single_message_with_7_bit_encoding(self):
        '''Content-Transfer-Encoding: 7bit'''
        maa = self.get_analyzer('gnome-7-bit.mbox')
        messages, non_parsed = maa.get_messages()
        expected = {  # noqa
            'body':
                u">I don't think it's fair to blame the Foundation [...]\n"
                u">of packaging since it's really not (just) a case [...]\n"
                u'>marketing.\n\n'
                u'No matter what is really to blame, it ultimately [...]\n\n'
                u'[...]\n\n'
                u'Rgds,\n'
                u'Eugenia \n',
            'content-type':
                u'text/plain; format=flowed; charset="iso-8859-1";'
                u'\n\treply-type=original',
            'date': '2004-09-22 02:03:40',
            'date_tz': '-25200',
            'in-reply-to': None,
            'list-id':
                u'GNOME Desktop Development List '
                u'<desktop-devel-list.gnome.org>',
            'message-id': u'<BAY12-DAV6Dhd2stb2e0000c0ce@hotmail.com>',
            'received': None,
            'references': None,
            'from': [(u'Eugenia Loli-Queru', u'eloli@hotmail.com')],
            'to': [('', u'language-bindings@gnome.org'),
                   ('', u'desktop-devel-list@gnome.org')],
            'cc': None
        }

        self.assertEqual(1, len(messages), '# of messages')
        self.check_single_message(expected, messages)
        self.assertEqual(0, non_parsed, 'non_parsed')
