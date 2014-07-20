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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02111-1301, USA.
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

import bz2
import gzip
import zipfile

import os.path
import datetime
import urlparse
import logging

from analyzer import MailArchiveAnalyzer
from htmlparser import MyHTMLParser
from utils import find_current_month, create_dirs, mlstats_dot_dir,\
    retrieve_remote_file, check_compressed_file

from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

from db.session import Database
from db.report import Report

datetimefmt = '%Y-%m-%d %H:%M:%S'


COMPRESSED_DIR = os.path.join(mlstats_dot_dir(), 'compressed')
GMANE_DOMAIN = 'gmane.org'
GMANE_URL = 'http://dir.gmane.org/'
GMANE_DOWNLOAD_URL = 'http://download.gmane.org/'
GMANE_LIMIT = 2000


class MailingList(object):

    def __init__(self, url_or_dirpath):
        rpath = url_or_dirpath.rstrip(os.path.sep)

        url = urlparse.urlparse(rpath)
        lpath = url.path.rstrip(os.path.sep)

        self._local = url.scheme == 'file' or len(url.scheme) == 0
        self._location = os.path.realpath(lpath) if self._local else rpath
        self._alias = os.path.basename(self._location) or url.netloc

        # Define local directories to store mboxes archives
        target = os.path.join(url.netloc, lpath.lstrip(os.path.sep))
        target = target.rstrip(os.path.sep)

        self._compressed_dir = os.path.join(COMPRESSED_DIR, target)

    @property
    def location(self):
        return self._location

    @property
    def alias(self):
        return self._alias

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
    def container(self):
        if not self.is_compressed():
            return open(self.filepath, 'rb')

        if self.compressed_type == 'gz':
            return gzip.GzipFile(self.filepath, mode='rb')
        elif self.compressed_type == 'bz2':
            return bz2.BZ2File(self.filepath, mode='rb')
        elif self.compressed_type == 'zip':
            return zipfile.ZipFile(self.filepath, mode='rb')

    @property
    def compressed_type(self):
        return self._compressed

    def is_compressed(self):
        return self._compressed is not None


class Application(object):
    def __init__(self, driver, user, password, dbname, host,
                 url_list, report_filename, make_report, be_quiet,
                 force, web_user, web_password):

        self.mail_parser = MailArchiveAnalyzer()

        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

        drv = url.URL(driver, user, password, host, database=dbname)
        engine = create_engine(drv, encoding='utf8', convert_unicode=True)
        Database.create_tables(engine, checkfirst=True)

        Session = sessionmaker()
        Session.configure(bind=engine)

        session = Session()

        self.db = Database()
        self.db.set_session(session)

        # User and password to make login in case the archives
        # are set to private
        self.web_user = web_user
        self.web_password = web_password

        # Don't show messages when retrieveing and analyzing files
        self.be_quiet = be_quiet

        # Force to download and parse any link found in the given URL
        self.force = force

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
                            (stored_messages, dbname))
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
            report = Report()
            report.set_session(session)
            report.print_brief_report()

        session.close()

    def __print_output(self, text):
        if not self.be_quiet:
            print text

    def __analyze_mailing_list(self, url_or_dirpath):
        """Look for mbox archives, retrieve, uncompress and analyze them"""

        mailing_list = MailingList(url_or_dirpath)

        # Check if mailing list already in database
        # today = datetime.datetime.today().strftime(datetimefmt)
        today = datetime.datetime.today()
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

        if os.path.isfile(mailing_list.location):
            archives.append(MBoxArchive(mailing_list.location,
                                        mailing_list.location))
        else:
            for root, dirs, files in os.walk(mailing_list.location):
                for filename in sorted(files):
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
            fp, size = retrieve_remote_file(url, filename,
                                            self.web_user, self.web_password)

            # Check whether we have read the last message.
            # In Gmane, an empty page means we reached the last msg
            if not size:
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
        links = htmlparser.get_mboxes_links(self.force)

        archives = []

        for link in links:
            basename = os.path.basename(link)
            destfilename = os.path.join(mailing_list.compressed_dir, basename)

            try:
                # If the URL is for the current month, always retrieve.
                # Otherwise, check visited status & local files first
                this_month = find_current_month(link)

                if this_month:
                    self.__print_output('Current month detected: Found substring %s in URL %s...' % (this_month, link))
                    self.__print_output('Retrieving %s...' % link)
                    retrieve_remote_file(link, destfilename,
                                         self.web_user, self.web_password)
                elif os.path.exists(destfilename):
                    self.__print_output('Already downloaded %s' % link)
                else:
                    self.__print_output('Retrieving %s...' % link)
                    retrieve_remote_file(link, destfilename,
                                         self.web_user, self.web_password)
            except IOError:
                self.__print_output("Unknown URL: " + link + ". Skipping.")
                continue

            archives.append(MBoxArchive(destfilename, link))
        return archives

    def __set_archives_to_analyze(self, mailing_list, archives):
        today = datetime.datetime.today().strftime(datetimefmt)

        # If the given list only includes one archive, force to
        # analyze it.
        if len(archives) == 1:
            archive = archives[0]
            self.db.set_visited_url(archive.url, mailing_list.location,
                                    today, self.db.NEW)
            return [archive]

        archives_to_analyze = []

        for archive in archives:
            # Always set Gmane archives to analyze
            if archive.url.find(GMANE_DOMAIN) == -1:
                # Check if already analyzed
                status = self.db.check_compressed_file(archive.url)

                this_month = find_current_month(archive.url)

                # If the file is for the current month, re-import to update.
                # If already visited, ignore it.
                if status == self.db.VISITED and not this_month:
                    self.__print_output('Already analyzed %s' %
                                        archive.url)
                    continue

            self.db.set_visited_url(archive.url, mailing_list.location,
                                    today, self.db.NEW)
            archives_to_analyze.append(archive)

        return archives_to_analyze

    def __analyze_list_of_files(self, mailing_list, archives_to_analyze):
        """Analyze a list of given files"""

        total_messages_url = 0
        stored_messages_url = 0
        non_parsed_messages_url = 0

        for archive in archives_to_analyze:
            self.__print_output('Analyzing %s' % archive.filepath)

            self.mail_parser.archive = archive

            try:
                messages, non_parsed_messages = self.mail_parser.get_messages()
            except IOError, e:
                self.__print_output("Invalid file: %s - %s. Skipping."
                                    % (archive.filepath, str(e)))
                continue

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

            # today = datetime.datetime.today().strftime(datetimefmt)
            today = datetime.datetime.today()
            self.db.set_visited_url(archive.url, mailing_list.location, today,
                                    self.db.VISITED)

        return total_messages_url, stored_messages_url, non_parsed_messages_url

    def __get_gmane_total_count(self, mailing_list_url, download_url):
        """Return the total count of messages from gmane mailing list"""
        mboxes = self.db.get_compressed_files(mailing_list_url)

        if not mboxes:
            return 0

        # Select the minimum offset of messages that are not
        # analyzed. This includes those downloaded and set
        # to NEW.
        # If all of these were analyzed, select the maximum offset
        # to restart the analysis from that point.
        import sys

        min_new = sys.maxint
        max_visited = 0

        for mbox in mboxes:
            msg_id = int(mbox.url.replace(download_url, '').strip('/'))

            if mbox.status == self.db.NEW:
                min_new = min(min_new, msg_id)
            else:
                max_visited = max(max_visited, msg_id)

        offset = min(min_new, max_visited)

        return offset

    def __check_mlstats_dirs(self):
        '''Check if the mlstats directories exist'''
        create_dirs(COMPRESSED_DIR)

    def __create_download_dirs(self, mailing_list):
        # Remote archives are retrieved and stored in compressed_dir.
        # Local compressed archives are left in their original location.
        if mailing_list.is_remote():
            create_dirs(mailing_list.compressed_dir)
