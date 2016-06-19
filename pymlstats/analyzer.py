# -*- coding:utf-8 -*-
# Copyright (C) 2007-2010 Libresoft Research Group
# Copyright (C) 2011-2014 Germán Poo-Caamaño <gpoo@gnome.org>
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
# Authors : Israel Herraiz <herraiz@gsyc.escet.urjc.es>

"""
This module contains a basic email parser. It uses the standard
Python modules for email parsing. It parses only mboxes files,
but it could be easily adopted using any other mailbox class
from the standard Python modules (for instance, Maildir).

@authors:      Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import re
import datetime
import hashlib
import sys

from email.header import decode_header
from email.utils import getaddresses, parsedate_tz
from email.Iterators import typed_subpart_iterator
from pymlstats.strictmbox import CustomMailbox
from pymlstats.utils import EMAIL_OBFUSCATION_PATTERNS


def to_unicode(string, charset='latin-1'):
    """Converts a string type to an object of unicode type.

    Gets an string object as argument, and tries several
    encoding to convert it to unicode. It basically tries
    encodings in sequence, until one of them doesn't raise
    an exception, since conversion into unicode using a
    given encoding raises an exception of one unknown character
    (for that encoding) is found.

    The string should usually be of str type (8-bit encoding),
    and the returned object is of unicode type.
    If the string is already of unicode type, just return it."""

    if isinstance(string, unicode):
        return string
    elif isinstance(string, str):
        encoded = False
        for encoding in [charset, 'ascii', 'utf-8', 'iso-8859-15']:
            try:
                uni_string = unicode(string, encoding)
            except:
                continue
            encoded = True
            break
        if encoded:
            return uni_string
        else:
            # All conversions failed, get unicode with unknown characters
            return (unicode(string, errors='replace'))
    else:
        raise TypeError('string should be of str type')


class ParseMessage:
    common_headers = ['message-id', 'list-id', 'content-type', 'references']

    # Some In-reply-to headers add some noise after the message-id. We
    # can clean it up.
    re_reply_to = re.compile('^.*[^<]*(<.*>).*', re.IGNORECASE)

    def parse_message(self, message):
        filtered_message = {}

        # Read unix from before headers
        unixfrom = message.get_unixfrom()
        charset = message.get_content_charset()

        try:
            date_to_parse = unixfrom.split('  ', 1)[1]
            parsed_date = parsedate_tz(date_to_parse)
            msgdate = datetime.datetime(*parsed_date[:6])
        except:
            msgdate = None

        # Some messages have a received header, but it is now being
        # ignored by MLStats and substituted by the value of the Unix
        # From field (first line of the message)
        filtered_message['received'] = msgdate

        # The 'body' is not actually part of the header, but it will be
        # treated as any other header
        body, patches = self.__get_body(message, charset)
        filtered_message['body'] = u'\n'.join(body)

        filtered_message['subject'] = self.__decode(message.get('subject'),
                                                    charset)

        # message.getaddrlist returns a list of tuples
        # Each one of the tuples is like this
        # (name,email_address)
        #
        # For instance, if the header is
        #      To: Alice <alice@alice.com>, Bob <bob@bob.com>
        # it will return
        #      [('Alice','alice@alice.com'), ('Bob','bob@bob.com')]
        #
        # If the header is 'from', this list will contain only one element.
        # If the header is 'to' or 'cc', it may contain several items
        # (or it could also be an empty list when such header is missing
        #  in the original message).
        for header in ('from', 'to', 'cc'):
            address = message.get(header)

            if not address:
                filtered_message[header] = None  # [('','')]
                continue

            address = self.__check_spam_obscuring(address)
            addresses = self.__get_decoded_addresses(address, charset)
            filtered_message[header] = addresses or None

        msgdate, tz_secs = self.__get_date(message)
        filtered_message['date'] = msgdate
        filtered_message['date_tz'] = str(tz_secs)

        in_reply_to = message.get('in-reply-to')
        # filtered_message['in-reply-to'] = self.re_reply_to.sub(r'\1',
        #                                                        in_reply_to)
        filtered_message['in-reply-to'] = in_reply_to

        # Retrieve other headers requested
        for header in self.common_headers:
            msg = message.get(header)
            if msg:
                try:
                    msg = to_unicode(msg, charset)
                except TypeError:
                    print >> sys.stderr, 'TypeError: msg: %s % msg'
                    msg = [to_unicode(e, charset) for e in msg]

            filtered_message[header] = msg

        return filtered_message

    def __get_body(self, msg, charset):
        body = []
        patches = []

        # Non multipart messages should be straightforward
        if not msg.is_multipart():
            body.append(to_unicode(msg.get_payload(decode=True), charset))
            return body, patches

        # Include all the attached texts if it is multipart
        parts = [part for part in typed_subpart_iterator(msg, 'text')]
        for part in parts:
            part_charset = part.get_content_charset()
            part_body = part.get_payload(decode=True)
            part_subtype = part.get_content_subtype()
            if part_subtype == 'plain':
                body.append(to_unicode(part_body, part_charset))
            elif part_subtype in ('x-patch', 'x-diff'):
                patches.append(to_unicode(part_body, part_charset))

        return body, patches

    def __get_date(self, message):
        parsed_date = parsedate_tz(message.get('date'))

        if not parsed_date:
            msgdate = datetime.datetime(*(1979, 2, 4, 0, 0))
            tz_secs = 0
            return msgdate, tz_secs

        try:
            msgdate = datetime.datetime(*parsed_date[:6])
            # Workaround for `strftime` which allow dates higher than 1900.
            # And the MySQL module uses `strftime` to convert a datetime.
            if msgdate.year < 1900:
                # Usually we see years like 0102, but in case someboedy
                # set the date to 1800 or something alike, we leave only
                # the centuries before adding 1900.
                fixed_year = (msgdate.year % 1000) + 1900
                msgdate = msgdate.replace(year=msgdate.year + fixed_year)
        except ValueError:
            msgdate = datetime.datetime(*(1979, 2, 4, 0, 0))

        tz_secs = parsed_date[-1] or 0

        return msgdate, tz_secs

    def __get_decoded_addresses(self, address, charset):
        result = []
        for name, email in getaddresses([address]):
            result.append((self.__decode(name, charset),
                           self.__decode(email, charset)))
        return result

    def __check_spam_obscuring(self, field):
        if not field:
            return field

        for pattern in EMAIL_OBFUSCATION_PATTERNS:
            if field.find(pattern) != -1:
                return field.replace(pattern, '@')

        return field

    def __decode(self, s, charset='latin-1', sep=u' '):
        """ Decode a header.  A header can be composed by strings with
            different encoding each.  We convert each group to unicode
            separately and then we merge them back."""

        charset = charset or 'latin-1'

        try:
            decoded_s = decode_header(s)
            r = sep.join([to_unicode(text, text_charset or charset)
                          for text, text_charset in decoded_s])
        except:
            print >> sys.stderr, 'WARNING: charset: %s' % charset,
            print >> sys.stderr, '"%s"' % s
            r = s

        return r


class MailArchiveAnalyzer:
    def __init__(self, archive=None):
        self.archive = archive

    def get_messages(self):
        messages_list = []
        fp = self.archive.container
        mbox = CustomMailbox(fp)

        without_message_id = 0
        for message in mbox:
            filtered_message = {}

            msg = ParseMessage()
            filtered_message = msg.parse_message(message)

            # if there is no message-id, we try to create one unique (but
            # repeatable) using the from address and the message body.
            # Otherwise, several messages without message-id could be
            # considered duplicated erroneously.
            if not filtered_message['message-id']:
                msgid = self.make_msgid(filtered_message['from'],
                                        filtered_message['body'])
                filtered_message['message-id'] = msgid
                print >> sys.stderr, '=> message-id not present for:'
                print >> sys.stderr, message
                without_message_id += 1

            messages_list.append(filtered_message)

        fp.close()

        return messages_list, without_message_id

    def make_msgid(self, from_addr, message):
        try:
            domain = from_addr[0][1].split('@')[1]
        except:
            domain = u'mlstats.localdomain'

        m = hashlib.md5(message.encode('utf-8')).hexdigest()
        return u'<%s.mlstats@%s>' % (m, domain)


if __name__ == '__main__':
    import pprint
    from archives import MBoxArchive

    # Print analyzer's output to check manually the parsing. In can
    # be used with egrep to filter out specific fields.
    # The input is a mbox file location (local)
    filepath = sys.argv[1]
    archive = MBoxArchive(filepath)

    maa = MailArchiveAnalyzer(archive)

    for m in maa.get_messages()[0]:
        pprint.pprint(m)
