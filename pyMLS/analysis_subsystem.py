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

import os, time
from threading import *
from config_manager import *
import utils
from parser_factory import parser_factory
import data_manager

class analysis_subsystem:

    def __init__(self, config):
        #print "Creado el analysis subsystem"
        # Tomando el tiempo de inicio
        self.config = config
        self.mail_parser = parser_factory.get_parser("MESSAGE")
        self.m_data_manager = data_manager.data_manager()



    def run (self, path):
        #print "Comenzando a trabajar en ",path
        utils.for_every_file (path, self.analyze_file)
        #print "    - Parsed a total of ",self.mail_parser.number_messages," messages."



    def analyze_file (self, filename):
        #print "Analizando el fichero "+filename
        self.mail_parser.match_file(filename)
        result = self.mail_parser.get_result()
        while result != None:
            self.m_data_manager.store_email (result, filename)
            result = self.mail_parser.get_result()
        
      
    