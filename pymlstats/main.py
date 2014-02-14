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
Main funcion of mlstats. Fun starts here!

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import os.path
import re
import datetime

from database import create_database
from analyzer import MailArchiveAnalyzer
from htmlparser import MyHTMLParser
from utils import current_month, create_dirs, mlstats_dot_dir,\
    retrieve_remote_file, check_compressed_file, uncompress_file


datetimefmt = '%Y-%m-%d %H:%M:%S'


MBOX_DIR = os.path.join(mlstats_dot_dir(), 'mbox')
COMPRESSED_DIR = os.path.join(mlstats_dot_dir(), 'compressed')
GMANE_DOMAIN = 'gmane.org'
GMANE_URL = 'http://dir.gmane.org/'
GMANE_DOWNLOAD_URL = 'http://download.gmane.org/'
GMANE_LIMIT = 2000


class MailingList(object):

    def __init__(self, url_or_dirpath):
        self._location = url_or_dirpath
        self._alias = os.path.basename(self._location)

        # Check if directory exists, if not, assume it is remote
        if os.path.exists(self._location):
            self._local = True
            target = self._location.lstrip('/')
        else:
            self._local = False
            target = re.sub('^(http|ftp)[s]{0,1}://', '', self._location)

        # Define local directories to store mboxes archives
        self._mbox_dir = os.path.join(MBOX_DIR, target)
        self._compressed_dir = os.path.join(COMPRESSED_DIR, target)

    @property
    def location(self):
        return self._location

    @property
    def alias(self):
        return self._alias

    @property
    def mbox_dir(self):
        return self._mbox_dir

    @property
    def compressed_dir(self):
        return self._compressed_dir

    def is_local(self):
        return self._local

    def is_remote(self):
        return not self.is_local()


class MBoxArchive(object):

    def __init__(self, filepath, url=None):
        self._filepath = filepath
        self.url = url
        self._compressed = check_compressed_file(filepath)

    @property
    def filepath(self):
        return self._filepath

    @property
    def compressed_type(self):
        return self._compressed

    def is_compressed(self):
        return self._compressed is not None


class Application:

    def __init__(self, driver, user, password, dbname, host,
                 admin_user, admin_password, url_list, report_filename,
                 make_report, be_quiet, web_user, web_password):

        self.mail_parser = MailArchiveAnalyzer()

        self.db = create_database(driver=driver, dbname=dbname, username=user,
                                  password=password, hostname=host,
                                  admin_user=admin_user,
                                  admin_password=admin_password)

        # Connect to database if exists, otherwise create it and connect
        self.db.connect()

        # User and password to make login in case the archives
        # are set to private
        self.web_user = web_user
        self.web_password = web_password

        # Don't show messages when retrieveing and analyzing files
        self.be_quiet = be_quiet

        # URLs or local files to be analyzed
        self.url_list = url_list

        self.__check_mlstats_dirs()

        total_messages = 0
        stored_messages = 0
        non_parsed = 0
        for mailing_list in url_list:
            t, s, np = self.__analyze_mailing_list(mailing_list)

            total_messages += t
            stored_messages += s
            non_parsed += np

        self.__print_output("%d messages analyzed" % total_messages)
        self.__print_output("%d messages stored in database %s" %
                            (stored_messages, self.db.name))
        self.__print_output("%d messages ignored by the parser" % non_parsed)

        difference = total_messages - stored_messages
        if difference == 0 and non_parsed == 0:
            self.__print_output("INFO: Everything seems to be ok.")

        if difference > 0:
            self.__print_output("WARNING: Some messages were parsed but "
                                "not stored")

        if non_parsed > 0:
            self.__print_output("WARNING: Some messages were ignored by "
                                "the parser (probably because they were "
                                "ill formed messages)")

        if make_report:
            self.__print_brief_report(report_filename)

    def __print_output(self, text):
        if not self.be_quiet:
            print text

    def __print_brief_report(self, report_filename):

        # total_lists = self.db.get_num_of_mailing_lists()
        messages_by_domain = self.db.get_messages_by_domain()
        people_by_domain = self.db.get_people_by_domain()
        messages_by_tld = self.db.get_messages_by_tld()
        people_by_tld = self.db.get_people_by_tld()
        messages_by_year = self.db.get_messages_by_year()
        people_by_year = self.db.get_people_by_year()
        messages_by_people = self.db.get_messages_by_people()
        total_people = self.db.get_total_people()
        total_messages = self.db.get_total_messages()

        output = "MLStats report\n"
        output += "--------------\n"

        output += "\n\nTotal messages by domain name (only top 10 per list):\n"
        output += "Mailing list    \tDomain name\t #  \n"
        output += "----------------\t-----------\t----\n"
        for r in messages_by_domain:
            ml = r[0].rstrip("/").split('/')[-1]
            domain = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(domain)+'\t'+str(num)+'\n'

        output += "\n\n" \
                  "Total people posting by domain name " \
                  "(only top 10 per list):\n"
        output += "Mailing list    \tDomain name\t #  \n"
        output += "----------------\t-----------\t----\n"
        for r in people_by_domain:
            ml = r[0].rstrip("/").split('/')[-1]
            domain = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(domain)+'\t'+str(num)+'\n'

        output += "\n\n"
        output += "Total messages by top level domain(only top 10 per list):\n"
        output += "Mailing list    \t    TLD    \t #  \n"
        output += "----------------\t-----------\t----\n"
        for r in messages_by_tld:
            ml = r[0].rstrip("/").split('/')[-1]
            tld = r[1]
            num = r[2]
            output += str(ml)+'\t'+str(tld)+'\t'+str(num)+'\n'

        output += "\n\n"
        output += "Total people posting by top level domain" \
                  "(only top 10 per list):\n"
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
            year = int(r[1])
            num = r[2]
            output += str(ml)+'\t'+str(year)+'\t'+str(num)+'\n'

        output += "\n\nTotal people posting by year:\n"
        output += "Mailing list    \t    Year   \t #  \n"
        output += "----------------\t-----------\t----\n"
        for r in people_by_year:
            ml = r[0].rstrip("/").split('/')[-1]
            year = int(r[1])
            num = r[2]
            output += str(ml)+'\t'+str(year)+'\t'+str(num)+'\n'

        output += "\n\n"
        output += "Total messages by email address (only top 10 in total):\n"
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

        output += """\n\n\n
           MLStats, Copyright (C) 2007-2010 Libresoft Research Group\n
           MLStats is Open Source Software/Free Software, licensed under
           the GNU GPL.\n"
           MLStats comes with ABSOLUTELY NO WARRANTY, and you are welcome
           to\n
           redistribute it under certain conditions as specified by
           the GNU GPL license;\n"
           see the documentation for details.\n
           Please credit this data as "generated using Libresoft's 'MLStats'.
           """

        if '' == report_filename:
            print output
        else:
            print "Report written to "+report_filename
            fileobj = open(report_filename, 'w')
            fileobj.write(output)
            fileobj.close()

    def __analyze_mailing_list(self, url_or_dirpath):
        """Look for mbox archives, retrieve, uncompress and analyze them"""

        mailing_list = MailingList(url_or_dirpath)

        # Check if mailing list already in database
        today = datetime.datetime.today().strftime(datetimefmt)
        self.db.update_mailing_list(mailing_list.location,
                                    mailing_list.alias,
                                    today)

        total, stored, non_parsed = (0, 0, 0)

        try:
            archives = self.__retrieve_mailing_list_archives(mailing_list)
            archives_to_analyze = self.__set_archives_to_analyze(mailing_list,
                                                                 archives)
            total, stored, non_parsed = self.__analyze_list_of_files(mailing_list, archives_to_analyze)
        except IOError:
            self.__print_output("Unknown URL or directory: " +
                                url_or_dirpath + ". Skipping.")

        return total, stored, non_parsed

    def __retrieve_mailing_list_archives(self, mailing_list):
        self.__create_download_dirs(mailing_list)

        if mailing_list.is_local():
            archives = self.__retrieve_local_archives(mailing_list)
        else:
            archives = self.__retrieve_remote_archives(mailing_list)
        return archives

    def __retrieve_local_archives(self, mailing_list):
        """Walk the mailing list directory looking for archives"""
        archives = []
        for root, dirs, files in os.walk(mailing_list.location):
            files.sort()
            for filename in files:
                location = os.path.join(root, filename)
                archives.append(MBoxArchive(location, location))
        return archives

    def __retrieve_remote_archives(self, mailing_list):
        """Download mboxes archives from the remote mailing list"""

        if (mailing_list.location.startswith(GMANE_URL)):
            archives = self.__retrieve_from_gmane(mailing_list)
        else:
            archives = self.__retrieve_from_mailman(mailing_list)
        return archives

    def __retrieve_from_gmane(self, mailing_list):
        """Download mboxes from gmane interface"""

        gmane_url = GMANE_DOWNLOAD_URL + mailing_list.alias
        from_msg = self.__get_gmane_total_count(mailing_list.location,
                                                gmane_url)

        archives = []

        while(True):
            to_msg = from_msg + GMANE_LIMIT
            url = gmane_url + '/' + str(from_msg) + '/' + str(to_msg)
            arch_url = gmane_url + '/' + str(from_msg)
            filename = os.path.join(mailing_list.compressed_dir, str(from_msg))

            self.__print_output('Retrieving %s...' % url)
            retrieve_remote_file(url, filename,
                                 self.web_user, self.web_password)

            # Check whether we have read the last message.
            # In Gmane, an empty page means we reached the last msg
            with open(filename, 'r') as f:
                content = f.read()
            if not content:
                break

            from_msg = to_msg

            archives.append(MBoxArchive(filename, arch_url))
        return archives

    def __retrieve_from_mailman(self, mailing_list):
        """Download mboxes from mailman interface"""
        # Get all the links listed in the URL
        #
        # The archives are usually retrieved in descending
        # chronological order (newest archives are always
        # shown on the top of the archives). Reverse the list
        # to analyze in chronological order.
        htmlparser = MyHTMLParser(mailing_list.location,
                                  self.web_user, self.web_password)
        links = htmlparser.get_mboxes_links()
        links.reverse()

        this_month = current_month()

        archives = []

        for link in links:
            basename = os.path.basename(link)
            destfilename = os.path.join(mailing_list.compressed_dir, basename)

            # If the URL is for the current month, always retrieve.
            # Otherwise, check visited status & local files first
            if link.find(this_month) >= 0:
                self.__print_output('Found substring %s in URL %s...' %
                                    (this_month, link))
                self.__print_output('Retrieving %s...' % link)
                retrieve_remote_file(link, destfilename,
                                     self.web_user, self.web_password)
            elif os.path.exists(destfilename):
                self.__print_output('Already downloaded %s' % link)
            else:
                self.__print_output('Retrieving %s...' % link)
                retrieve_remote_file(link, destfilename,
                                     self.web_user, self.web_password)
            archives.append(MBoxArchive(destfilename, link))
        return archives

    def __set_archives_to_analyze(self, mailing_list, archives):
        archives_to_analyze = []

        for archive in archives:
            # Always set Gmane archives to analyze
            if not archive.filepath.find(GMANE_DOMAIN):
                # Check if already analyzed
                status = self.db.check_compressed_file(archive.filepath)

                # If the file is for the current month, re-import to update
                this_month = -1 != archive.filepath.find(current_month())
                if this_month:
                    self.__print_output('Found substring %s in URL %s...' %
                                        (this_month, archive.filepath))

                # If already visited, ignore, unless it's for the current month
                if status == self.db.VISITED and not this_month:
                    self.__print_output('Already analyzed %s' %
                                        archive.filepath)
                    continue

            # If not, set visited
            # (before uncompressing, otherwise the db will point towards
            # the uncompressed temporary file)
            today = datetime.datetime.today().strftime(datetimefmt)
            self.db.set_visited_url(archive.url, mailing_list.location,
                                    today, self.db.NEW)

            if archive.is_compressed():
                # Uncompress and get the raw filepaths
                filepaths = uncompress_file(archive.filepath,
                                            archive.compressed_type,
                                            mailing_list.mbox_dir)
                uncompressed_mboxes = [MBoxArchive(fp, archive.url)
                                       for fp in filepaths]
                archives_to_analyze.extend(uncompressed_mboxes)
            else:
                archives_to_analyze.append(archive)

        return archives_to_analyze

    def __analyze_list_of_files(self, mailing_list, archives_to_analyze):
        """Analyze a list of given files"""

        total_messages_url = 0
        stored_messages_url = 0
        non_parsed_messages_url = 0

        for archive in archives_to_analyze:
            filepath = archive.filepath
            self.__print_output('Analyzing %s' % filepath)
            self.mail_parser.filepath = filepath
            messages, non_parsed_messages = self.mail_parser.get_messages()
            total_messages = len(messages)
            stored_messages = self.db.store_messages(messages,
                                                     mailing_list.location)
            difference = total_messages-stored_messages
            if difference > 0:
                self.__print_output("   ***WARNING: %d messages (out of %d) "
                                    "parsed but not stored***" %
                                    (difference, total_messages))
            if non_parsed_messages > 0:
                self.__print_output("   ***WARNING: %d messages (out of %d) "
                                    "were ignored by the parser***" %
                                    (non_parsed_messages,
                                     total_messages + non_parsed_messages))

            total_messages_url += total_messages
            stored_messages_url += stored_messages
            non_parsed_messages_url += non_parsed_messages

            today = datetime.datetime.today().strftime(datetimefmt)
            self.db.set_visited_url(archive.url, mailing_list.location, today,
                                    self.db.VISITED)

        return total_messages_url, stored_messages_url, non_parsed_messages_url

    def __get_gmane_total_count(self, mailing_list_url, download_url):
        """Return the total count of messages from gmane mailing list"""
        mboxes = self.db.get_compressed_files(mailing_list_url)

        ids = []
        for mbox in mboxes:
            msg_id = mbox.replace(download_url, '').strip('/')
            msg_id = int(msg_id)
            ids.append(msg_id)

        if not ids:
            return 0
        return max(ids)

    def __check_mlstats_dirs(self):
        '''Check if the mlstats directories exist'''
        create_dirs(MBOX_DIR)
        create_dirs(COMPRESSED_DIR)

    def __create_download_dirs(self, mailing_list):
        # Remote archives are retrieved and stored in compressed_dir.
        # Local compressed archives are left in their original location.
        if mailing_list.is_remote():
            create_dirs(mailing_list.compressed_dir)

        create_dirs(mailing_list.mbox_dir)
