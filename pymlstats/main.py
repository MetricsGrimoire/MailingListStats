# Copyright (C) 2007-2009 Libresoft Research Group
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
Main funcion of mlstats. Fun starts here!

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

from database import *
from analyzer import *
from htmlparser import *
from utils import (retrieve_remote_file, check_compressed_file,
                   uncompress_file, mlstats_dot_dir)
import os.path
import pwd
import sys
import datetime

datetimefmt = '%Y-%m-%d %H:%M:%S'

class Application:
    
    MBOX_DIR = os.path.join(mlstats_dot_dir(),'mbox')
    COMPRESSED_DIR = os.path.join(mlstats_dot_dir(),'compressed')


    def __init__(self,user,password,dbname,host,admin_user,admin_password,url_list,report_filename,make_report,be_quiet,web_user,web_password):

        self.mail_parser = MailArchiveAnalyzer()

        self.db = Database()
        self.db.name = dbname
        self.db.user = user
        self.db.password = password
        self.db.host = host
        self.db.admin_user = admin_user
        self.db.admin_password = admin_password

        # Connect to database if exists, otherwise create it and connect
        self.db.connect()

        # User and password to make login in case the archives are set to private
        self.web_user = web_user
        self.web_password = web_password

        # Don't show messages when retrieveing and analyzing files
        self.be_quiet = be_quiet

        # URLs to be analyzed
        self.url_list = url_list

        self.__check_mlstats_dirs()

        # Temporary variable to store the directory names for each mailing list
        self.__mbox_directory = None
        self.__compressed_directory = None

        total_messages = 0
        stored_messages = 0
        non_parsed = 0
        for url in url_list:
            t,s,np = self.__analyze_url(url)

            total_messages += t
            stored_messages += s
            non_parsed += np

        self.__print_output("%d messages analyzed" % total_messages)
        self.__print_output("%d messages stored in database %s" % (stored_messages,self.db.name))
        self.__print_output("%d messages ignored by the parser" % non_parsed)

        difference = total_messages - stored_messages
        if difference == 0 and non_parsed == 0:
            self.__print_output("INFO: Everything seems to be ok.")

        if difference > 0:
            self.__print_output("WARNING: Some messages were parsed but not stored")

        if non_parsed > 0:
            self.__print_output("WARNING: Some messages were ignored by the parser (probably because they were ill formed messages)")

        if make_report:
            self.__print_brief_report(report_filename)

    def __print_output(self,text):
        if not self.be_quiet:
            print text

    def __print_brief_report(self,report_filename):

        total_lists = self.db.get_num_of_mailing_lists()
        messages_by_domain = self.db.get_messages_by_domain()
        people_by_domain = self.db.get_people_by_domain()
        messages_by_tld = self.db.get_messages_by_tld()
        people_by_tld = self.db.get_people_by_tld()
        messages_by_year = self.db.get_messages_by_year()
        people_by_year = self.db.get_people_by_year()
        messages_by_people = self.db.get_messages_by_people()
        total_people = self.db.get_total_people()
        total_messages = self.db.get_total_messages()

        output =  "MLStats report\n"
        output += "--------------\n"

        output += "\n\nTotal messages by domain name (only top 10 per list):\n"
        output += "Mailing list    \tDomain name\t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in messages_by_domain:
            ml = r[0].rstrip("/").split('/')[-1]
            domain = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(domain)+'\t'+str(num)+'\n'

        output += "\n\nTotal people posting by domain name (only top 10 per list):\n"
        output += "Mailing list    \tDomain name\t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in people_by_domain:
            ml = r[0].rstrip("/").split('/')[-1]
            domain = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(domain)+'\t'+str(num)+'\n'
        
        output += "\n\nTotal messages by top level domain(only top 10 per list):\n"
        output += "Mailing list    \t    TLD    \t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in messages_by_tld:
            ml = r[0].rstrip("/").split('/')[-1]
            tld = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(tld)+'\t'+str(num)+'\n'
        
        output += "\n\nTotal people posting by top level domain(only top 10 per list):\n"
        output += "Mailing list    \t    TLD    \t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in people_by_tld:
            ml = r[0].rstrip("/").split('/')[-1]
            tld = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(tld)+'\t'+str(num)+'\n'

        output += "\n\nTotal messages by year:\n"
        output += "Mailing list    \t    Year   \t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in messages_by_year:
            ml = r[0].rstrip("/").split('/')[-1]
            year = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(year)+'\t'+str(num)+'\n'

        output += "\n\nTotal people posting by year:\n"
        output += "Mailing list    \t    Year   \t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in people_by_year:
            ml = r[0].rstrip("/").split('/')[-1]
            year = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(year)+'\t'+str(num)+'\n'

        output += "\n\nTotal messages by email address (only top 10 per list):\n"
        output += "Mailing list    \t   Email   \t #  \n"
        output += "----------------\t-----------\t----\n"        
        for r in messages_by_people:
            ml = r[0].rstrip("/").split('/')[-1]
            email = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(email)+'\t'+str(num)+'\n'

        output += "\n\nTotal people posting in each list:\n"
        output += "Mailing list    \t #  \n"
        output += "----------------\t----\n"        
        for r in total_people:
            ml = r[0].rstrip("/").split('/')[-1]
            num = r[1]
            output += str(ml)+'\t'+str(num)+'\n'

        output += "\n\nTotal messages in each list:\n"
        output += "Mailing list    \t #  \n"
        output += "----------------\t----\n"        
        for r in total_messages:
            ml = r[0].rstrip("/").split('/')[-1]
            num = r[1]
            output += str(ml)+'\t'+str(num)+'\n'

        output += "\n\n\nMLStats, Copyright (C) 2007-2009 Libresoft Research Group\n"
        output += "MLStats is Open Source Software/Free Software, licensed under the GNU GPL.\n"
        output += "MLStats comes with ABSOLUTELY NO WARRANTY, and you are welcome to\n"
        output += "redistribute it under certain conditions as specified by the GNU GPL license;\n"
        output += "see the documentation for details.\n"
        output += 'Please credit this data as "generated using Libresoft\'s \'MLStats\'."'

        if '' == report_filename:
            print output
        else:
            print "Report written to "+report_filename
            fileobj = open(report_filename,'w')
            fileobj.write(output)
            fileobj.close()

    def __analyze_url(self,url):
        """Check the type of url (directory, remote), and call
        the appropiate function"""

        # Check if mailing list already in database
        today = datetime.datetime.today().strftime(datetimefmt)
        name = os.path.basename(url)
        self.db.update_mailing_list(url,name,today)

        total, stored, non_parsed = (0,0,0)
        # Check if directory exists
        if os.path.exists(url):
            total, stored, non_parsed = self.__analyze_non_remote(url)
        # If not, assume it is remote
        else:
            try:
                total, stored, non_parsed = self.__analyze_remote(url)
            except IOError:
                self.__print_output("Unknown URL or directory: "+url+". Skipping.")                

        return total, stored, non_parsed

    def __analyze_remote(self,url):
        """Download the archives from the remote url, stores and parses them."""

        # Check directories to stored the archives
        self.__compressed_directory = os.path.join(Application.COMPRESSED_DIR,url.lstrip("http://").lstrip("https://").lstrip("ftp://").lstrip("ftps://"))
        self.__mbox_directory = os.path.join(Application.MBOX_DIR,url.lstrip("http://").lstrip("https://").lstrip("ftp://").lstrip("ftps://"))
        if not os.path.exists(self.__compressed_directory):
            os.makedirs(self.__compressed_directory)
        if not os.path.exists(self.__mbox_directory):
            os.makedirs(self.__mbox_directory)

        # Get all the links listed in the URL
        htmlparser = MyHTMLParser(url, self.web_user, self.web_password)
        links = htmlparser.get_mboxes_links()

        # First retrieve, then analyze files
        files_to_analyze = []
        for link in links:
            basename = os.path.basename(link)
            destfilename = os.path.join(self.__compressed_directory,basename)

            # If already visited, ignore
            # FIXME: Should not this check the date of the last analysis?
            status = self.db.check_compressed_file(link)
            if 'visited' == status:
                self.__print_output("Already analyzed "+link)
                continue

            # Check if already downloaded
            if os.path.exists(destfilename):
                self.__print_output("Already downloaded "+link)
            else:
                self.__print_output("Retrieving "+link+"...")
                retrieve_remote_file(link,destfilename,self.web_user, self.web_password)
                
            # If not, set visited
            # (before uncompressing, otherwise the db will point towards
            # the uncompressed temporary file)
            today = datetime.datetime.today().strftime(datetimefmt)
            self.db.set_visited_url(link,url,today)

            # Check if compressed
            extension = check_compressed_file(destfilename)
            if extension:
                # If compressed, uncompress and get the raw filepath
                filepaths = uncompress_file(destfilename,extension, self.__mbox_directory)
                # __uncompress_file returns a list containing
                # the path to all the uncompressed files
                # (for instance, a tar file may contain more than one file)
                files_to_analyze += filepaths
            else:
                # File was not uncompressed, so there is only
                # one file to append
                files_to_analyze.append(destfilename)

        # The archives are usually retrieved in descending
        # chronological order (because the newest archives are always
        # shown on the top of the archives)

        # So we will analyze the list of files in the order inversed
        # to the order in they were retrieved
        files_to_analyze.reverse()

        return self.__analyze_list_of_files(url,files_to_analyze)
        
    def __analyze_list_of_files(self,mailing_list_url,filepath_list):
        """Analyze a list of given files"""

        total_messages_url = 0
        stored_messages_url = 0
        non_parsed_messages_url = 0

        for filepath in filepath_list:
            self.__print_output("Analyzing "+filepath)                    
            self.mail_parser.filepath = filepath
            messages, non_parsed_messages = self.mail_parser.get_messages()
            total_messages = len(messages)
            stored_messages = self.db.store_messages(messages,mailing_list_url)
            difference = total_messages-stored_messages
            if difference > 0:
                self.__print_output("   ***WARNING: %d messages (out of %d) parsed but not stored***" % (difference,total_messages))
            if non_parsed_messages > 0:
                self.__print_output("   ***WARNING: %d messages (out of %d) were ignored by the parser***" % (non_parsed_messages,total_messages+non_parsed_messages))

            total_messages_url += total_messages
            stored_messages_url += stored_messages
            non_parsed_messages_url += non_parsed_messages

        return total_messages_url, stored_messages_url, non_parsed_messages_url
        
    def __analyze_non_remote(self,dirname):
        """Walk recursively the directory looking for files,
        and uncompress them. Then __analyze_local_directory is called."""

        # Check if directory to stored uncompressed files already exists
        self.__mbox_directory = os.path.join(Application.MBOX_DIR,dirname.lstrip('/'))
        if not os.path.exists(self.__mbox_directory):
            os.makedirs(self.__mbox_directory)
        # Compressed files are left in their original location,
        # because they can be uncompressed from that location

        filepaths = []
        for root, dirs, files in os.walk(dirname):
            filepaths += [os.path.join(root,filename) for filename in files]

        
        filepaths_to_analyze = []
        for filepath in filepaths:

            # Check if already analyzed
            status = self.db.check_compressed_file(filepath)

            # If already visited, ignore
            # FIXME: Should not this check the date of the last analysis?
            if 'visited' == status:
                self.__print_output("Already analyzed "+filepath)
                continue
            
            # If not, set visited
            # (before uncompressing, otherwise the db will point towards
            # the uncompressed temporary file)
            today = datetime.datetime.today().strftime(datetimefmt)
            self.db.set_visited_url(filepath,dirname,today)

            # Check if compressed
            extension = check_compressed_file(filepath)
            if extension:
                # If compressed, uncompress and get the raw filepath
                filepaths = uncompress_file(filepath,extension, self.__mbox_directory)
                # __uncompress_file returns a list containing
                # the path to all the uncompressed files
                # (for instance, a tar file may contain more than one file)
                filepaths_to_analyze += filepaths
            else:
                # File was not uncompressed, so there is only
                # one file to append
                filepaths_to_analyze.append(filepath)
            
        return self.__analyze_list_of_files(dirname,filepaths_to_analyze)



    def __check_mlstats_dirs(self):
        """Check if the mlstats directories exist
        in the home directory of the user who
        is running the program"""

        mbox_dir = Application.MBOX_DIR
        compressed_dir = Application.COMPRESSED_DIR
        
        if not os.path.exists(mbox_dir):
            os.makedirs(mbox_dir)

        if not os.path.exists(compressed_dir):
            os.makedirs(compressed_dir)
                        
