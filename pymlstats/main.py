# -*- coding:utf-8 -*-
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

import datetime
import logging

from analyzer import MailArchiveAnalyzer
from utils import find_current_month, create_dirs

from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker

from db.session import Database
from db.report import Report

from archives import MailingList, COMPRESSED_DIR
from backends import LocalArchive, GmaneArchive, MailmanArchive,\
    GMANE_URL, GMANE_DOMAIN, GMANE_DOWNLOAD_URL

datetimefmt = '%Y-%m-%d %H:%M:%S'


class Application(object):
    def __init__(self, driver, user, password, dbname, host,
                 url_list, report_filename, make_report, be_quiet,
                 force, web_user, web_password, compressed_dir=None):

        # If no "--compressed-dir" parameter is set, use default
        if compressed_dir is None:
            compressed_dir = COMPRESSED_DIR

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

        self.__check_mlstats_dirs(compressed_dir)

        total_messages = 0
        stored_messages = 0
        non_parsed = 0
        for url_ml in url_list:
            t, s, np = self.__analyze_mailing_list(url_ml, compressed_dir)

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
            report.print_brief_report(report_filename=report_filename)

        session.close()

    def __print_output(self, text):
        if not self.be_quiet:
            print text

    def __analyze_mailing_list(self, url_or_dirpath, compressed_dir):
        """Look for mbox archives, retrieve, uncompress and analyze them"""

        mailing_list = MailingList(url_or_dirpath, compressed_dir)

        # Check if mailing list already in database
        # today = datetime.datetime.today().strftime(datetimefmt)
        today = datetime.datetime.today()
        self.db.update_mailing_list(mailing_list.location,
                                    mailing_list.alias,
                                    today)

        total, stored, non_parsed = (0, 0, 0)

        if mailing_list.is_local():
            mla = LocalArchive(mailing_list)
        elif mailing_list.location.startswith(GMANE_URL):
            gmane_url = GMANE_DOWNLOAD_URL + mailing_list.alias
            offset = self.__get_gmane_total_count(mailing_list.location,
                                                  gmane_url)
            mla = GmaneArchive(mailing_list, self.be_quiet, self.force,
                               self.web_user, self.web_password, offset)
        else:
            mla = MailmanArchive(mailing_list, self.be_quiet, self.force,
                               self.web_user, self.web_password)

        mla._create_download_dirs()

        try:
            archives = [a for a in mla.fetch()]
            archives_to_analyze = self.__set_archives_to_analyze(mailing_list,
                                                                 archives)
            total, stored, non_parsed = self.__analyze_list_of_files(mailing_list, archives_to_analyze)
        except IOError:
            self.__print_output("Unknown URL or directory: " +
                                url_or_dirpath + ". Skipping.")

        return total, stored, non_parsed

    def __set_archives_to_analyze(self, mailing_list, archives):
        # today = datetime.datetime.today().strftime(datetimefmt)
        today = datetime.datetime.today()

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
            stored_messages, \
                duplicated_messages, \
                error_messages = self.db.store_messages(messages,
                                                        mailing_list.location)
            difference = total_messages-stored_messages
            if difference > 0:
                self.__print_output("   ***WARNING: %d messages (out of %d) "
                                    "parsed but not stored "
                                    "(%d duplicate, %d errors)***" %
                                    (difference, total_messages,
                                     duplicated_messages, error_messages))
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

    def __check_mlstats_dirs(self, compressed_dir):
        '''Check if the mlstats directories exist'''
        create_dirs(compressed_dir)
