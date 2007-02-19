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
   Python: stats_subsystem
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from transformer_factory import transformer_factory
from observer_pattern import observer_pattern
from config_manager import *


#Subsistema encargado de conseguir estadisticas a partir de los resultados anteriores.

class stats_subsystem:

    def __init__(self, config):
        self.my_config = config
        self.base_destiny_directory = self.my_config.get_value("results_directory")
        self.my_observer = observer_pattern()
        self.projects = []
        for database in self.my_config.get_value('databases'):
            database = database.replace('mailingliststat_','')
            if database not in self.projects:
                self.projects.append(database)

        

    def run(self):
        # Se averiguan los transformadores que tienen que crearse.
        # Se subscriben los transformadores que se van creando.
        tranformers = self.my_config.get_keys_that_contain("transformer")
        # Se activan los transformadores que mande la configuracion
        for tran in tranformers:
            if self.my_config.get_value(tran) == "YES":
                print "   - Enabling transformer: ",tran
                new_transformer = transformer_factory.get_transformer(tran,\
                                                        self.my_config,\
                                                        "")
                # Se suscribe el transformador a la lista de transformadores
                if new_transformer != None:
                    self.my_observer.subscribe(new_transformer)
        # Para cada transformador elegido se instancia
        for project in self.projects:
            self.my_observer.announce(\
                [self.base_destiny_directory+'/'+project + '/', \
                 'mailingliststat_'+project])
        # Finishing
        self.my_observer.finish()




#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: stats_subsystem.py **"


if __name__ == "__main__":
    test()

