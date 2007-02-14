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
   Python: message_parser
   Author: Jorge Gascon Perez
   E-Mail: jgascon@gsyc.escet.urjc.es
'''

from parser import *
from mls_structures import email
import utils
from utils import debug



class message_parser(parser):
    '''
    From zch519 en gmail.com  Sun Oct  8 18:20:24 2006
    From: zch519 en gmail.com (Alice L.)
    Date: Sun Oct  8 17:27:48 2006
    Subject: [Libresoft-acad] Dinero extra en ratos libres
    Message-ID: <E4DF9CE3.AFE91E1@gmail.com>
    
    Texto del mensajeTexto del mensajeTexto del mensaje
    Texto del mensajeTexto del mensajeTexto del mensaje
    Texto del mensajeTexto del mensajeTexto del mensaje
    '''
    
    def __init__(self):
        #Constructor de la clase madre:
        parser.__init__(self)
        #Propiedades:
        self.last_file_descriptor = None
        self.last_filename = ""
        self.processing = ""
        self.actual_message = None
        self.result = None
        self.messages_in_this_file = 0
        self.total_number_messages = 0
        #Cadenas de tokens que debe reconocer nuestro parser.
        #From zch519 en gmail.com  Sun Oct  8 18:20:24 2006
        #From cartaoterra em terra.com.br  Wed May  4 20:37:08 2005
        self.load_expression(r"^From\ [\d\w\.\-\_\+]+ (em|en|at)\ [\d\w\.\-\_]+ .", self.process_begin_from)
        #From dang@gentoo.org  Wed May  3 12:27:49 2006
        self.load_expression(r"^From\ [\d\w\.\_\-\+]+\@+[\d\w\.\_\-]+\ .", self.process_begin_from)
        #From =?UTF-8?Q?=E0=A5=80=E0=A4=A3=E0=A5=8D_=E0=A4=8F_?=  Fri Dec 16 20:17:34 2005

        self.load_expression(r"^From\:\ [\d\w\.\_\(\)\-\=\?\@]+\ .", self.process_from)
        #From: zch519 en gmail.com (Alice L.)
        #From: nab at kernel.org (Nicholas A. Bellinger)
        #From: erkko.anttila at nokia.com (erkko.anttila@nokia.com)
        #From: tapani.palli at nokia.com (=?UTF-8?B?VGFwYW5pIFDDpGxsaQ==?=)
        self.load_expression(r"^From\:\ [\d\w\.\-\_]+\ (em|en|at)\ [\d\w\.\_\-]+\ \([\,\(\)\=\?\d\w\ \_\-\.\"\'\@]+\)$", self.process_from_alias)
        #From Maysa" <maysa@colorview.com.br  Tue Feb 11 20:15:06 2003
        self.load_expression(r"^From\:\ [\d\w\ \_\-\"\']+\<[\d\w\.\@]+\>? .", self.process_from)
        #From: Daniel Gryniewicz <dang@gentoo.org>
        self.load_expression(r"^From\:\ [\d\w\ ]+\<[\d\w\.\@]+\>", self.process_from_alias)
        #Date: Sun Oct  8 17:27:48 2006
        self.load_expression(r"Date\: .", self.process_date)
        self.load_expression(r"Sent\: .", self.process_date)
        #Subject: [Libresoft-acad] Dinero extra en ratos libres
        self.load_expression(r"Subject\:\ .", self.process_subject)
        #Message-ID: <E4DF9CE3.AFE91E1@gmail.com>
        self.load_expression(r"Message\-I[Dd]\:\ .", self.process_message_id)
        
        #List-Id: evince-list.gnome.org
        self.load_expression(r"List\-Id\:\ .", self.process_list_id)

        #
        self.load_expression(r"^\n$", self.process_begin_body)
        
        #Cc: evince-list@gnome.org
        self.load_expression(r"Cc\:\ .", self.process_carbon_copy)
        #Cc: "Daniel Gryniewicz" <dang@gentoo.org>
        self.load_expression(r"Cc\:\ \"[\d\w\ ]+\" .", self.process_carbon_copy)
        
        #To: "Daniel Gryniewicz" <dang@gentoo.org>
        self.load_expression(r"To\:\ \"[\d\w\ ]+\" .", self.process_to)
        #To: evince-list@gnome.org
        self.load_expression(r"To\:\ [\d\w\ \-\@\.]+", self.process_to)
        
        #References: <200605291526.35846.aj504@student.cs.york.ac.uk
        self.load_expression(r"X\-[\w\-]+\:\ .", self.process_strange_tag)

        #Content-Type: application/octet-stream; name="p59_1"
        self.load_expression(r"Content-Type: application/octet-stream;\ ", self.process_end_of_body)
        self.load_expression(r"Content-Disposition: attachment;", self.process_end_of_body)
        self.load_expression(r"Content-Type: text/x-log;", self.process_end_of_body)
        
        self.load_expression(r".", self.process_unknown)




    def process_begin_from (self, text):
        debug ("Processing Beggining FROM: " + text.replace("\n",""))
        self.messages_in_this_file += 1
        self.total_number_messages += 1

        '''
        # Esto es un capturador de cabeceras.
        f = open('/home/jgascon/prueba_mls.txt','a')
        f.write(text)
        f.close()
        '''
        
        # En primer lugar si aun no tenemos ningun objeto mensaje creamos uno.
        if self.actual_message == None:
            self.actual_message = email()
        else:
            # Si tenemos ya un objeto mensaje entonces lo cargamos al resultado
            # y creamos un nuevo objeto mensaje para procesar.
            self.result = self.actual_message
            self.actual_message = email()





    def process_from (self, text):
        #From zch519 en gmail.com  Sun Oct  8 18:20:24 2006
        #From dang@gentoo.org  Wed May  3 12:27:49 2006
        debug ("Processing FROM: " + text.replace("\n",""))
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace('"','')
        text = text.replace("From ","")

        if '@' in text:
            text = text.split(' ')
            self.actual_message.author_from = utils.purify_text(text.pop(0))
        else:
            text = text.split(' ')
            self.actual_message.author_from = utils.purify_text(text.pop(0))
            #Eliminando el "en" o el "at"
            text.pop(0)
            self.actual_message.author_from += "@"+utils.purify_text(text.pop(0))
        #self.actual_message.first_date = " ".join(text)
        #self.actual_message.first_date = utils.correct_date(self.actual_message.first_date)
        #Sun Oct  8 17:27:48 2006
        #Mon, 15 May 2006 17:37:00 -070
        self.processing = ""



    def process_from_alias (self, text):
        debug ("Processing FROM ALIAS: " + text.replace("\n",""))
        #From: zch519 en gmail.com (Alice L.)
        #From: Daniel Gryniewicz <dang@gentoo.org>
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace('"','')
        text = text.replace("From: ","")
        text = text.replace("From:","")
        text = text.replace("From","")
        # ------------------- Trozo del From normal ----------------------------

        if '@' in text:
            text = text.split(' ')
            self.actual_message.author_from = utils.purify_text(text.pop(0))
        else:
            text = text.split(' ')
            self.actual_message.author_from = utils.purify_text(text.pop(0))
            #Eliminando el "en" o el "at"
            text.pop(0)
            self.actual_message.author_from += "@"+utils.purify_text(text.pop(0))
        self.processing = ""
        # ----------------- FIN Trozo del From normal --------------------------
        try:
            if '(' in text:
                text = text.split('(')[1]
                text = text.rstrip(')')
                self.actual_message.author_alias = utils.purify_text(text)
            if '<' in text:
                text = text.replace('From: ','')
                text = text.replace('From ','')
                text = text.split('<')[0]
                text = text.strip(' ')
                self.actual_message.author_alias = utils.purify_text(text)
        except:
            print "ERROR producido al procesar un supuesto alias: ",text
            print "Se estaba procesando el fichero ",self.last_filename
            raise




    def process_date (self, text):
        #Date: Sun Oct  8 17:27:48 2006
        debug ("Processing DATE: " + text.replace("\n",""))
        text = text.replace("\n","")
        text = text.replace("Date: ","")
        #Sun Oct  8 17:27:48 2006
        #Mon, 15 May 2006 17:37:00 -0700
        #Fri Dec 16 20:09:03 2005
        try:
            self.actual_message.arrival_date = utils.correct_date(text)
        except:
            print "ERROR producido al procesar una supuesta fecha: ",text
            print "Se estaba procesando el fichero ",self.last_filename
            raise



    def process_subject (self, text):
        #Subject: [Libresoft-acad] Dinero extra en ratos libres
        debug ("Processing Subject: " + text.replace("\n",""))
        # Traceando mensajes.
        #self.debug_file.write(text)
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace("Subject: ","")
        self.actual_message.subject = utils.purify_text(text)



    def process_strange_tag (self, text):
        debug ("Processing unknown: " + text.replace("\n",""))



    def process_list_id (self, text):
        debug ("Processing list id: " + text.replace("\n",""))
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace("List-Id: ","")
        self.actual_message.mailing_list = text



    def process_begin_body (self, text):
        if self.actual_message != None:
            if self.processing == "BODY":
                debug ("            " + text.replace("\n",""))
            if self.processing == "DISPOSED BODY":
                debug ("DISPOSED:   " + text.replace("\n",""))
            else:
                self.processing = "BODY"
                debug ("Begin BODY: ")
                debug ("            " + text.replace("\n",""))
            self.actual_message.body += utils.purify_text(text)
            if len(self.actual_message.body) > 64000:
                self.actual_message.body = self.actual_message.body[:63999]



    def process_carbon_copy (self, text):
        debug ("Processing carbon copy: " + text.replace("\n",""))
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace("Cc: ","")
        text = text.split(',')
        self.actual_message.carbon_copy = text



    def process_to (self, text):
        debug ("Processing TO: " + text.replace("\n",""))
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace("To: ","")
        text = text.split(',')
        self.actual_message.to = text



    def process_message_id (self, text):
        debug ("Processing Message_id: " + text.replace("\n",""))
        #Message-ID: <E4DF9CE3.AFE91E1@gmail.com>
        text = text.replace("\n","")
        text = text.replace("'","''")
        text = text.replace("Message-ID: <","")
        text = text.replace("Message-Id: <","")
        text = text.replace(">","")
        self.actual_message.message_id = text



    def process_end_of_body (self, text):
        if self.processing == "BODY":
            debug ("TRUNCATING MESSAGE:")
            self.processing = "DISPOSED BODY"



    def process_unknown (self, text):
        if self.processing == "BODY":
            debug ("            " + text.replace("\n",""))
            self.actual_message.body += utils.purify_text(text)
            if len(self.actual_message.body) > 64000:
                self.actual_message.body = self.actual_message.body[:63999]
        else:
            debug ("Processing unknown: " + text.replace("\n",""))



    def get_result(self):
        '''
        Este metodo solamente funciona si hay un fichero del que se pueda leer.

        La primera vez que se lee no hay mensajes por leer, por lo que leemos
        lineas hasta que pon fin tenemos un mensaje complejo, es decir, que
        self.result != None

        Si llegamos a fin de fichero antes de que eso ocurra, entonces miramos
        en self.actual_message por si tenemos dentro un mensaje completo que
        podamos usar.
        '''
        read_line = " "
        if self.last_file_descriptor == None:
            return None

        # Leemos lineas hasta que tenemos algo en self.result o llegamos al
        # final del fichero.
        while True:
            read_line = self.last_file_descriptor.readline()

            if read_line == "":
                # Hemos llegado al fin de fichero, acabamos y devolvemos lo que
                # tengamos.
                self.finish()
                return self.actual_message
            else:
                # Aun hay lineas por leer, parseamos la linea leida
                self.match_string(read_line)
                # Miramos si hay algo en self.result y lo devolvemos en su caso
                if self.result != None:
                    myResult = self.result
                    self.result = None
                    return myResult




    def match_file(self, filename):
        # Inicializando datos
        self.processing = ""
        self.actual_message = None
        self.result = None
        # Inicializando el descriptor de fichero
        if self.last_file_descriptor != None:
            self.last_file_descriptor.close()
            self.last_file_descriptor = None
        try:
            self.last_file_descriptor = open(filename, "r", 2000000)
            self.last_filename = filename
            print "      Parsing: ",filename
        except:
            print "message_parser->imposible abrir el fichero ",filename
            self.last_file_descriptor = None



    #def __del__(self):
    #    #print "Cerrando el fichero de trazas"
    #    #self.debug_file.close()
    def finish(self):
        print "         - Parsed in this file a total of ",self.messages_in_this_file," messages."
        self.messages_in_this_file = 0
        print "         - Total of messages parsed ",self.total_number_messages
        if self.last_file_descriptor != None:
            self.last_file_descriptor.close()
            self.last_file_descriptor = None




#---------------------- UNITY TESTS ----------------------


def test():
    print "** UNITY TEST: message_parser.py **"
    my_log_parser = message_parser()
    # Ahora se procesa un mensaje basado en el RFC822
    my_log_parser.match_file("/usr/home/jgascon/Trabajos/Libresoft/Prototipos/mailingListStat-devel/Results/thanima/thanima-devel/temp/2005-October_txt/2005-October.txt")
    #my_log_parser.match_file("/usr/home/jgascon/vacio.txt")
    # Mostrando resultados
    result = my_log_parser.get_result()
    contador = 0
    while result != None:
        print result
        print "Movido"
        result = my_log_parser.get_result()
        contador += 1
    print "Procesados "+str(contador)+" mensajes."
        
        
if __name__ == "__main__":
    test()


