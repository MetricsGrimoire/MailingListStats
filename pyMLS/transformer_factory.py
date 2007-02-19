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
    Factoria de transformers:
    Contiene la lista de todos los transformers creados
    y crea uno segun nuestras necesidades.
'''

# En esta parte se ocupa de importar todos los transformers creados hasta la fecha.
import transformer


class transformer_factory:

    def get_transformer(type_of_transformer, config_object, output_directory):

        # ----------------- PUT YOUR TRANSFORMER CODE -------------------------
        if type_of_transformer.lower() == "seal_xml_transformer":
            import seal_xml_transformer
            return seal_xml_transformer.seal_xml_transformer(config_object, output_directory)

        if type_of_transformer.lower() == "basic_transformer":
            import basic_transformer
            return basic_transformer.basic_transformer(config_object, output_directory)

        if type_of_transformer.lower() == "dump_db_transformer":
            import dump_db_transformer
            return dump_db_transformer.dump_db_transformer(config_object, output_directory)

        if type_of_transformer.lower() == "most_active_transformer":
            import most_active_transformer
            return most_active_transformer.most_active_transformer(config_object, output_directory)

        if type_of_transformer.lower() == "libresoft_big_database_transformer":
            import libresoft_big_database_transformer
            return libresoft_big_database_transformer.libresoft_big_database_transformer(config_object, output_directory)

        if type_of_transformer.lower() == "latex_country_report_transformer":
            import latex_country_report_transformer
            return latex_country_report_transformer.latex_country_report_transformer(config_object, output_directory)

        # ------------- END OF PUT YOUR TRANSFORMER CODE -----------------------

        print "ERROR: Transformer_Factory->"+type_of_transformer.lower()+" no present."
        #print "Building generic transformer"
        return None

    #Next line avoids to create a "transformer_factory" instance.
    get_transformer = staticmethod(get_transformer)





#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: transformer_factory.py **"


if __name__ == "__main__":
    test()


