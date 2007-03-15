# Copyright (C) 2007 Libresoft Research Group
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
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
@contact:      herraiz@gsyc.escet.urjc.es
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

    # This wrapper is defensive against ill-formed MIME messages in the mailbox
    # See http://www.python.org/doc/2.4.4/lib/module-mailbox.html for details
    def msgfactory(fp):
        try:            
            return email.message_from_file(fp)
        except email.Errors.MessageParseError:
            # Don't return None since that will
            # stop the mailbox iterator
            return ''

    msgfactory = staticmethod(msgfactory)


    def __init__(self):
        self.filepath = None

    def get_messages(self):

        fileobj = open(self.filepath,'r')
        messages_list = []
        mbox = mailbox.PortableUnixMailbox(fileobj,MailArchiveAnalyzer.msgfactory)

        message = mbox.next()

        while message:

            if '' == message:
                message = mbox.next()
                continue
            
            filtered_message = {}

            for header in MailArchiveAnalyzer.accepted_headers:                
                if 'body' == header:
                    # The 'body' is not actually part of the headers,
                    # but it will be treated as any other header
                    field = str(message.get_payload())
                else:                    
                    field = message[header]
                    if field:
                        field = str(field)
                    else:
                        field = ""
                
                if 'from' == header or 'to' == header or 'cc' == header:
                    header_content = message.get_all(header)

                    # Check spam obscuring
                    header_content = self.__check_spam_obscuring(header_content)
                    try:
                        filtered_message[header] = getaddresses(header_content)
                    except:
                        filtered_message[header] = [('','')]
                elif 'date' == header or 'received' == header:
                    t = parsedate_tz(field)
                    try:
                        year, month, day, hour, minute, second, unused1, unused2, unused3, tz_secs = t
                    except:
                        year, month, day, hour, minute, second, unused1, unused2, unused3, tz_secs = (1979,2,4,0,0,0,0,0,0,0)

                    #print (year,month,day,hour,minute,second,tz_secs)

                    try:
                        msgdate = datetime.datetime(year,  
                                                month, 
                                                day,   
                                                hour,  
                                                minute,
                                                second)

                        msgdate = msgdate.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        year, month, day, hour, minute, second, unused1, unused2, unused3, tz_secs = (1979,2,4,0,0,0,0,0,0,0)

                        msgdate = datetime.datetime(year,  
                                                month, 
                                                day,   
                                                hour,  
                                                minute,
                                                second)

                        msgdate = msgdate.strftime("%Y-%m-%d %H:%M:%S")

                    filtered_message[header] = msgdate
                    if not tz_secs:
                        tz_secs = 0
                        
                    filtered_message[header+"_tz"] = str(tz_secs)
                                            
                else:
                    filtered_message[header] = field

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

            message = mbox.next()

        fileobj.close()

        return messages_list

    def __check_spam_obscuring(self,field):

        # Add more patterns here
        obscurers = [" at ","_at_"]

        if not field:
            return field
        
        field = field[0]

        for pattern in obscurers:
            if field.find(pattern):
                return [field.replace(pattern,"@")]
