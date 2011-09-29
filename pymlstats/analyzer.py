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
		_, date_to_parse = unixfrom.split("  ", 1)
	    	parsed_date = parsedate_tz(date_to_parse)
		year, month, day, hour, minute, second, unused1, unused2, unused3, tz_secs = parsed_date
	        msgdate = datetime.datetime(year,
                                            month, 
                                            day,   
                                            hour,  
                                            minute,
                                            second)
                
                msgdate = msgdate.strftime("%Y-%m-%d %H:%M:%S")
            except:
                msgdate = None

            # Write it to filtered message before parsing headers
            filtered_message['received'] = msgdate
                
            for header in MailArchiveAnalyzer.accepted_headers:                
                if 'body' == header:
                    # The 'body' is not actually part of the headers,
                    # but it will be treated as any other header
                    field = self.__get_body(message)
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
                        filtered_message[header] = None  #[('','')]
                elif 'date' == header:
                    t = parsedate_tz(field)
                    try:
                        year, month, day, hour, minute, second, unused1, unused2, unused3, tz_secs = t
                    except:
                        year, month, day, hour, minute, second, unused1, unused2, unused3, tz_secs = (1979,2,4,0,0,0,0,0,0,0)

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
                                            
                elif 'received' != header:
                    # Some messages have a received header, but it is
                    # now being ignored by MLStats and substituted by
                    # the value of the Unix From field (first line of
                    # the message)
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
