#!/usr/bin/env python

# Copyright (C) 2006 Jorge Gascon Perez
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
# Authors : Jorge Gascon <jgascon@gsyc.escet.urjc.es>

import md5
import utils


class email:
    def __init__(self):
        self.message_id   = ""
        self.author_from  = ""
        self.author_alias = ""
        self.mailing_list = ""
        self.to           = []
        self.carbon_copy  = []
        self.first_date   = ""
        self.arrival_date = ""
        self.subject      = ""
        self.body         = ""



    def generate_unique_id (self):
        m = md5.new()
        m.update(str(self.author_from) + str(self.to) +\
                 str(self.carbon_copy) + str(self.first_date) + str(self.arrival_date))
        self.message_id = m.hexdigest()
        return self.message_id
    

  
    def __str__(self):
        text  = "From        : "+self.author_from+"\n"
        text += "Alias       : "+self.author_alias+"\n"
        text += "Mailing List: "+self.mailing_list+"\n"
        text += "To          : "+str(self.to)+"\n"
        text += "Cc          : "+str(self.carbon_copy)+"\n"
        text += "First Date  : "+self.first_date+"\n"
        text += "Arrival Date: "+self.arrival_date+"\n"
        text += "Subject     : "+self.subject+"\n"
        text += "BODY        : ["+self.body+"]\n"
        return text




class person:
    def __init__(self, email, alias, mailing_list, associated_message="", type_recipient="From"):
        self.email_address = utils.purify_text(email.strip(' '))
        self.alias         = utils.purify_text(alias.strip(' '))
        self.mailing_list  = utils.purify_text(mailing_list.strip(' '))
        self.associated_message_id = utils.purify_text(associated_message.strip(' '))
        self.type_recipient = utils.purify_text(type_recipient.strip(' '))

        
    def __str__(self):
        text  = "Email       : "+self.email_address+"\n"
        text += "Alias       : "+self.alias+"\n"
        text += "Mailing List: "+self.mailing_list+"\n"
        return text




