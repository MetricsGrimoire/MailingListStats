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


'''
    Factoria de parsers:
    Contiene la lista de todos los parsers creados
    y crea uno segun nuestras necesidades.
'''

# En esta parte se ocupa de importar todos los parsers creados hasta la fecha.
import parser
#In future svn_parser and arch_parser will be added.


class parser_factory:

    def get_parser(type_of_message):
        if type_of_message.upper() == "MESSAGE":
            import message_parser
            return message_parser.message_parser()

        if type_of_message.upper() == "CONFIG":
            import config_parser
            return config_parser.config_parser()

        #print "Building generic parser"
        return parser.parser()

    #Next line avoids to create a "parser_factory" instance.
    get_parser = staticmethod(get_parser)

