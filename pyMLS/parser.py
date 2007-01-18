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
Generic Parser, all your parsers have to
inherit from this class.
'''

import re, string, utils

class parser:

    '''
        La clase parser sirve para procesar rapidamente
        cadenas de caracteres o bien ficheros completos.

        Una vez definidas las expresiones a identificar el parser
        analiza el texto introducido buscando "linea por linea" intentando
        ver si cada linea concuerda con alguna expresion establecida
        (ojo! la linea entera debe coincidir con alguna de las expresiones)
        cuando ello sucede, se invoca al metodo que tiene asignada dicha
        expresion.

        La forma mas limpia de trabajar con esta clase es heredar de ella,
        redefiniendo el constructor e introducciendo las expresiones en el
        nuevo constructor.

        Consultar en el directorio de HOWTO para mas informacion y ejemplos.
    '''

    #Atributos:

    #Un resultado es una estructura que contiene
    # - Text  : El texto del string que ha coincidido con la expresion.
    # - Rule  : El numero de expresion que se ha cumplido.
    # - Detail: La expresion al completo.
    # - Method: El metodo a invocar si la expresion coincide.

    ########################### FUNCIONES AUXILIARES ########################


    #Esta funcion es la encargada de
    def match_expressions(self, text):
        text = utils.latin1_to_ascii(text)
        #print "Mirando la expresion: ",text
        index = 0
        while index < len(self.m_compiled_expressions):
            #comprobando esta expresion
            expr = self.m_compiled_expressions[index]
            result = None
            try:
                result = expr.match(text)
            except AttributeError:
                #Si se produce un error significa que el texto no
                #coincide con la expresion probada, hay que probar con
                #la siguiente.
                print "No coincide ",text," con la expresion ",\
                self.m_expressions[index]

            if result != None:
                #print "Mirando la expresion: ",text
                #Se ejecuta el metodo por el cual el indice coincidio
                metodo = self.m_methods[index]
                return metodo(text)

            index+=1


    #Metodo de depurado, simplemente muestra
    #informacion de la expresion encontrada.
    def debug(self, text):
        if text != None:
            print "parser.debug: " + text
        else:
            print "parser.debug: None"


    ####################### FUNCIONES USADAS POR EL USUARIO #################

    #Diccionario que contiene las expresiones y el metodo a llamar
    #en caso de que se encuentre la expresion.
    def __init__(self):
        self.m_expressions = []
        self.m_methods     = []
        self.m_compiled_expressions = []
        self.total_lines_processed = 0



    #Carga en el parser una expresion y el metodo a
    #ejecutar si esta es concordada.
    def load_expression(self, expression, method_invoked=None):
        '''
            Este metodo debe utilizarse en la inicializacion
            del parser, ya que sirve para introducir las expresiones
            que queremos que se analicen.
            Ademas de la expresion tambien hay que introducir como
            parametro el metodo que queremos que se invoque cuando
            la expresion coincida con algun texto introducido.

            ejemplo)
            def procesaNumeros(texto):
            # ... Aqui se procesa el numero identificado ...

            nuevo_parser = parser()
            #cuando se identifique un numero real se llamara
            #automaticamente al metodo "procesaNumeros"
            nuevo_parser.load_expression("[0-9]+.[0-9]+",procesaNumeros)
            nuevo_parser.match_string("123.5")
        '''

        #Se pone el metodo por defecto si al usuario se le olvido
        #introducir un metodo.
        if method_invoked == None:
            method_invoked = self.debug
        #Se busca la expresion no sea que ya exista
        if expression in self.m_expressions and method_invoked != None:
            i = self.m_expressions.index(expression)
            self.m_methods[i] = method_invoked
        else:
            #Las expresiones se introducen en orden, las mas largas primero.
            #Se va recorriendo el array de las expresiones en toda su longitud,
            #cuando se encuentre una expresion mas corta se insertara ahi
            #nuestra nueva expresion y terminaremos, en otro caso insertamos
            #nuestra expresion al final.
            index = 0
            while index < len(self.m_expressions):
                if len(expression) >= len(self.m_expressions[index]):
                    self.m_expressions.insert(index,expression)
                    self.m_methods.insert(index,method_invoked)
                    self.m_compiled_expressions.insert(index, \
                                                       re.compile(expression))
                    #print "Esquema de las expresiones ", self.m_expressions
                    #print "Esquema de los metodos ", self.m_methods
                    return
                index += 1

            #Si no se introdujo la introduciremos al final
            self.m_expressions.append(expression)
            self.m_methods.append(method_invoked)
            self.m_compiled_expressions.append(re.compile(expression))
            #print "Esquema de las expresiones ", self.m_expressions
            #print "Esquema de los metodos ", self.m_methods



    #Dado un string lo procesa buscando las expresiones que coinciden
    #totalmente con el, se usa con strings cortos, como de una linea
    #de largo, por ejemplo.
    def match_string(self, text):
        '''
            Dada una cadena de caracteres el parser comprueba si
            coincide completamente con alguna de las expresiones
            que tiene el parser.
            Si coincide, automaticamente se invoca al metodo asociado
            a dicha expresion, pasandole como parametro el texto
            reconocido.

            ejemplo)
                nuevo_parser.match_string("123.5")
        '''
        self.total_lines_processed += 1
        self.match_expressions(text)





    #Dado un nombre de archivo, lo abre y linea a linea trata
    #de que alguna expresion concuerde totalmente con cada linea.
    def match_file(self, filename):
        '''
            Dado un nombre de fichero el parser intenta abrirlo,
            si lo abre con exito lo analiza linea a linea, para
            cada linea que coincide completamente con alguna de las
            expresiones el parser invoca al metodo asociado a dicha
            expresion.

            ejemplo)
                nuevo_parser.match_file("myFile.txt")
        '''
        try:
            f = open(filename, "r", 1000000)
        except:
            print "parser.match_file: Imposible abrir el fichero ",filename
            return
        self.match_file_descriptor(f)
        self.finish()




    def match_file_descriptor (self, file_descriptor):
        line = file_descriptor.readline()
        while line != "":
            self.match_string(line)
            line = file_descriptor.readline()
        file_descriptor.close()
        #for line in file_descriptor.readlines():
        #    self.match_string(line)
        #file_descriptor.close()



    def get_result(self):
        print "Parser: get_result not implemented here"



    def finish(self):
        print "Parser: finish not implemented here"


