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


import mailbox
import email
from email.Utils import getaddresses, parsedate_tz
import datetime

class MailArchiveAnalyzer:

    accepted_headers = ['message-id','from', \
                        'to', \
                        'cc', \
                        'date', \
                        'received', \
                        'list-id', \
                        'in-reply-to', \
                        'subject', \
                        'body']

    def __init__(self, filepath=None):
        self.filepath = filepath

    def get_messages(self):

        messages_list = []
        mbox = mailbox.mbox(self.filepath)

        non_parsed = 0
        for message in mbox:
            filtered_message = {}

            # Read unix from before headers
            unixfrom = message.get_unixfrom()

            try:
                date_to_parse = unixfrom.split('  ', 1)[1]
                parsed_date = parsedate_tz(date_to_parse)
                msgdate = datetime.datetime(*parsed_date[:6]).isoformat(' ')
            except:
                msgdate = None

            # Some messages have a received header, but it is
            # now being ignored by MLStats and substituted by
            # the value of the Unix From field (first line of
            # the message)
            filtered_message['received'] = msgdate

            # The 'body' is not actually part of the headers,
            # but it will be treated as any other header
            filtered_message['body'] = self.__get_body(message)

            filtered_message['subject'] = message.get('subject') or ''
            filtered_message['list-id'] = message.get('list-id') or ''
            filtered_message['message-id']  = message.get('message-id') or ''
            filtered_message['in-reply-to'] = message.get('in-reply-to') or ''

            for header in ('from', 'to', 'cc'):
                header_content = message.get_all(header)

                # Check spam obscuring
                header_content = self.__check_spam_obscuring(header_content)
                try:
                    filtered_message[header] = getaddresses(header_content)
                except:
                    filtered_message[header] = None  #[('','')]

            msgdate, tz_secs = self.__get_date(message)
            filtered_message['date'] = msgdate.isoformat(' ')
            filtered_message['date_tz'] = str(tz_secs)

            # message.getaddrlist returns a list of tuples
            # Each one of the tuples is like this
            # (name,email_address)
            #
            # For instance, if the header is
            # To: Alice <alice@alice.com>, Bob <bob@bob.com>
            # it will return
            # [('Alice','alice@alice.com'), ('Bob','bob@bob.com')]
            #
            # If the header is 'from', this list will contain only
            # 1 element
            #
            # If the header is 'to' or 'cc', it may contain several
            # items (or it could be also an empty list if there is not such header
            # in the original message).

            messages_list.append(filtered_message)

        return messages_list, non_parsed

    def __get_body(self,msg):

        # Non multipart messages are easy
        if not msg.is_multipart():
            return msg.get_payload(decode=True)

        # Include all the attached texts if it is multipart        
        body = ""

        for m in msg.walk():

            if m.is_multipart():
                continue

            cp = m.get_content_type()

            if ("text" in cp) or ("message" in cp):
                body += "Begin attachment of type %s\n" % cp
                body += m.get_payload(decode=True)

        return body

    def __get_date(self, message):
        parsed_date = parsedate_tz(message.get('date'))

        if not parsed_date:
            msgdate = datetime.datetime(*(1979, 2, 4, 0, 0))
            tz_secs = 0
            return msgdate, tz_secs

        try:
            msgdate = datetime.datetime(*parsed_date[:6])
            if msgdate.year < 100:
                msgdate = msgdate.replace(year=msgdate.year+1900)
        except ValueError:
            msgdate = datetime.datetime(*(1979, 2, 4, 0, 0))

        tz_secs = parsed_date[-1] or 0

        return msgdate, tz_secs

    def __check_spam_obscuring(self,field):

        # Add more patterns here
        obscurers = [" at ","_at_"," en "]

        if not field:
            return field
        
        field = field[0]

        for pattern in obscurers:
            if field.find(pattern):
                return [field.replace(pattern,"@")]


if __name__ == '__main__':
    import sys
    from pprint import pprint

    # Print analyzer's output to check manually the parsing. In can
    # be used with egrep to filter out specific fields.
    # The input is a mbox file location (local)
    maa = MailArchiveAnalyzer()
    maa.filepath = sys.argv[1]
    for m in maa.get_messages()[0]:
        pprint(m)
