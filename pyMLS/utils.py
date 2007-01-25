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

# If you use another Database system, change "MySQLdb" by other database module
from MySQLdb import *

import urllib, os, re
from sgmllib import SGMLParser

def debug (text):
    #print text
    return


class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []
    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)



def get_mailing_list_file_links (MyUrl):
    valid_Urls = []
    try:
        usock = urllib.urlopen(MyUrl)
    except:
        print "ERROR: No se pudo acceder a "+MyUrl
        return []
    parser = URLLister()
    parser.feed(usock.read())
    usock.close()
    parser.close()
    for url in parser.urls:
        if ".txt" in url:
            if "http://" not in url and "https://" not in url:
                valid_Urls.append (MyUrl + "/" + url)
    return valid_Urls



def download_url_to (url, filename):
    try:
        urllib.urlretrieve(url, filename)
        return True
    except:
        print "ERROR: No se pudo descargar "+url
        return False




def for_every_file (path, method):
    #print "for_every_file ["+path+"]"
    try:
        os.chdir(path)
    except:
        #Si no puede acceder al directorio entonces finaliza
        print "Fallo en ",path
        return
    #Obteniendo lista de ficheros y directorios
    lista_cosas = os.popen3('ls')[1].read()
    lista_cosas = lista_cosas.split('\n')
    #En la variable lista_cosas hay una mezcla de ficheros y directorios
    for cosa in lista_cosas:
        if cosa != '':
            #Si cosa es un directorio entonces se debera recorrer recursivamente
            if os.path.isdir(cosa):
                #print "rec_file_search: make dir: "+hfs_path+'/'+cosa
                for_every_file(path+'/'+cosa, method)
                os.chdir(path)
            if os.path.isfile(cosa):
                method(path+'/'+cosa)




def decompress_file (filename, clean=False):
    if ".zip" in filename.lower():
        os.system("unzip -f "+filename)
    if ".tar.bz2" in filename.lower():
        os.system("tar xjf "+filename)
    if ".tar.gz" in filename.lower():
        os.system("tar xjf "+filename)
    if ".tar" in filename.lower():
        os.system("tar xf "+filename)
    if ".gz" in filename.lower():
        os.system("gunzip -f "+filename)
    if ".bz2" in filename.lower():
        os.system("bunzip2 "+filename)
    if ".rar" in filename.lower():
        os.system("unrar e "+filename)
    if clean == True:
        os.system("rm -f "+ filename)



def correct_date(a_date):
    #Sun Oct  8 17:27:48 2006
    #Tue Aug  1 06:40:17 2006
    #Mon, 15 May 2006 17:37:00 -070
    #Fri, 1 Apr 2005 12:20:18 -0500
    #01 Apr 2005 14:26:14 -0500
    #Fri Dec 16 20:09:03 2005
    a_date = a_date.replace('  ',' ')
    debug("Correcting date 1: "+str(a_date))
    month = '00'
    m=re.search('Jan|Feb|Mar|Apr|May|Jun|Jul|Ago|Sep|Oct|Nov|Dec', a_date)
    if m != None:
        month = m.group(0)
        if month=='Jan':
            month = '01';
        if month=='Feb':
            month = '02';
        if month=='Mar':
            month = '03'
        if month=='Apr':
            month = '04'
        if month=='May':
            month = '05'
        if month=='Jun':
            month = '06'
        if month=='Jul':
            month = '07'
        if month=='Ago':
            month = '08'
        if month=='Sep':
            month = '09'
        if month=='Oct':
            month = '10'
        if month=='Nov':
            month = '11'
        if month=='Dec':
            month = '12'
          
    year = '0000'
    m=re.search('\ \d\d\d\d\ ?', a_date)
    if m != None:
        year = m.group(0)
        year = year.strip(' ')
    
    day = '00'
    m=re.search('\ ?[0123\ ]\d\ ', a_date)
    if m != None:
        day = m.group(0)
        day = day.strip(' ')

    hour = '00:00:00'
    m=re.search('\ \d\d\:\d\d\:\d\d\ ', a_date)
    if m != None:
        hour = m.group(0)
        hour = hour.strip(' ')
    #'YYYY-MM-DD HH:MM:SS'
    debug("Correcting date 2: "+year+'-'+month+'-'+day+' '+hour)
    return year+'-'+month+'-'+day+' '+hour




def latin1_to_ascii (unicrap):
    """This takes a UNICODE string and replaces Latin-1 characters with
        something equivalent in 7-bit ASCII. It returns a plain ASCII string. 
        This function makes a best effort to convert Latin-1 characters into 
        ASCII equivalents. It does not just strip out the Latin-1 characters.
        All characters in the standard 7-bit ASCII range are preserved. 
        In the 8th bit range all the Latin-1 accented letters are converted 
        to unaccented equivalents. Most symbol characters are converted to 
        something meaningful. Anything not converted is deleted.
    """
    xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'A', 0xc5:'A',
        0xc6:'Ae', 0xc7:'C',
        0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
        0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
        0xd0:'Th', 0xd1:'N',
        0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
        0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
        0xdd:'Y', 0xde:'th', 0xdf:'ss',
        0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
        0xe6:'ae', 0xe7:'c',
        0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
        0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
        0xf0:'th', 0xf1:'n',
        0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
        0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
        0xfd:'y', 0xfe:'th', 0xff:'y',
        0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
        0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
        0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
        0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
        0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 
        0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
        0xd7:'*', 0xf7:'/'
        }
    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += str(i)
    return r





def purify_text(text):
    text = latin1_to_ascii (text)
    text = text.replace("\'","")
    text = text.replace("'","''")
    return text
          
          


def is_valid_url(url):
    if 'http://' in url or \
       'https://' in url:
        return True
    return False


        
#---------------------- UNITY TESTS ----------------------

def test():
    print "** UNITY TEST: http_utils.py **"
    print "Probando la apertura de distintos ficheros "
    ficheros = ["/home/jgascon/test/prueba.txt",\
                "/home/jgascon/test/prueba.txt.ZIP",\
                "/home/jgascon/test/prueba.txt.bz2",\
                "/home/jgascon/test/prueba.txt.gz",\
                "/home/jgascon/test/prueba.txt.tar",\
                "/home/jgascon/test/prueba.txt.tar.bz2",\
                "/home/jgascon/test/prueba.txt.tar.gz"]

    for file in ficheros:
        print "Probando la apertura de "+file      
        f = open_mailing_list_file(file)
        if f != None:
            print "Resultado:  "
            line = f.readline()
            while line != "":
                line = line.replace('\n','')
                print "    "+line
                line = f.readline()
            f.close()
        else:
            print "    No se pudo abrir "+file


if __name__ == "__main__":
    test()

