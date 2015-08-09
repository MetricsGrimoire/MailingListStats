# -*- coding:utf-8 -*-
#
# Copyright (C) 2007-2010 Libresoft Research Group
# Copyright (C) 2015 Germán Poo-Caamaño
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
#           Germán Poo-Caamaño <gpoo@gnome.org>

import gzip
import os.path

from htmlparser import MyHTMLParser
from utils import find_current_month, create_dirs, fetch_remote_resource,\
    file_type
from archives import MBoxArchive, MailingList


GMANE_DOMAIN = 'gmane.org'
GMANE_URL = 'http://dir.gmane.org/'
GMANE_DOWNLOAD_URL = 'http://download.gmane.org/'
GMANE_LIMIT = 2000


class BaseArchive(object):
    """Base class to handle mailing lists archives.

    Used to process local and remote mailing lists archives via generators.
    An Archive class must have the following attributes:
    - mailing_list: (MailingList) a Mailing List object with its location.
    - be_quite: (boolean) tell if this class should not print any text
      indicating progress of a task (e.g. while downloading files).
    """
    def __init__(self, mailing_list, be_quiet=False):
        # Don't show messages when retrieveing and analyzing files
        self.be_quiet = be_quiet

        # URLs or local files to be analyzed
        self.url = mailing_list.location
        self.output_dir = mailing_list.compressed_dir

        self.mailing_list = mailing_list

    def _print_output(self, text):
        if not self.be_quiet:
            print text

    def _create_download_dirs(self):
        # Remote archives are retrieved and stored in output_dir.
        # Local compressed archives are left in their original location.
        if self.mailing_list.is_remote():
            create_dirs(self.mailing_list.compressed_dir)


class RemoteArchive(BaseArchive):
    """Generic class to handle remove mailing lists archives.

    Use this class to implement mechanisms to download mailing list archives
    from Internet.
    """
    def __init__(self, mailing_list, be_quiet=False, force=False,
                 web_user=None, web_password=None):
        super(RemoteArchive, self).__init__(mailing_list, be_quiet)

        # User and password to make login in case the archives
        # are set to private
        self.web_user = web_user
        self.web_password = web_password

        # Force to download and parse any link found in the given URL
        self.force = force

    def _retrieve_remote_file(self, url, destfilename=None):
        """Retrieve a file from a remote location.

        It logins in the archives private page if necessary.
        """

        # Creat a temporary file is no destination is given
        if not destfilename:
            destfilename = os.tmpnam()

        content = fetch_remote_resource(url, self.web_user, self.web_password)

        if file_type(content) is None:
            fd = gzip.GzipFile(destfilename, 'wb')
        else:
            fd = open(destfilename, 'wb')

        fd.write(content)
        fd.close()

        return destfilename, len(content)


class MailmanArchive(RemoteArchive):
    """Class to download mboxes from Mailman interface."""

    def fetch(self):
        """Get all the links listed in the Mailing List's URL.

        The archives are usually retrieved in descending chronological
        order (newest archives are always shown on the top of the archives).
        Reverse the list to analyze in chronological order.
        """

        mailing_list = self.mailing_list

        htmlparser = MyHTMLParser(mailing_list.location,
                                  self.web_user, self.web_password)
        links = htmlparser.get_mboxes_links(self.force)

        for link in links:
            basename = os.path.basename(link)
            destfilename = os.path.join(mailing_list.compressed_dir, basename)

            try:
                # If the URL is for the current month, always retrieve.
                # Otherwise, check visited status & local files first
                this_month = find_current_month(link)

                if this_month:
                    self._print_output(
                        'Current month detected: '
                        'Found substring %s in URL %s...' % (this_month, link))
                    self._print_output('Retrieving %s...' % link)
                    self._retrieve_remote_file(link, destfilename)
                elif os.path.exists(destfilename):
                    self._print_output('Already downloaded %s' % link)
                else:
                    self._print_output('Retrieving %s...' % link)
                    self._retrieve_remote_file(link, destfilename)
            except IOError:
                self._print_output("Unknown URL: " + link + ". Skipping.")
                continue

            yield MBoxArchive(destfilename, link)


class GmaneArchive(RemoteArchive):
    """Class to download mboxes from Gmane interface."""

    def __init__(self, mailing_list, be_quiet=False, force=False,
                 web_user=None, web_password=None, offset=0):
        super(GmaneArchive, self).__init__(mailing_list, be_quiet, force,
                                           web_user, web_password)
        self.offset = offset

    def fetch(self):
        """Get all the links listed in the Mailing List's URL.

        The archives are usually retrieved in descending chronological
        order (newest archives are always shown on the top of the archives).
        Reverse the list to analyze in chronological order.
        """

        mailing_list = self.mailing_list

        gmane_url = GMANE_DOWNLOAD_URL + mailing_list.alias
        from_msg = self.offset if self.offset else self.__get_gmane_offset()

        while True:
            to_msg = from_msg + GMANE_LIMIT
            url = gmane_url + '/' + str(from_msg) + '/' + str(to_msg)
            archive_url = gmane_url + '/' + str(from_msg)
            filename = os.path.join(mailing_list.compressed_dir, str(from_msg))

            self._print_output('Retrieving %s...' % url)
            fp, size = self._retrieve_remote_file(url, filename)

            # Check whether we have read the last message.
            # In Gmane, an empty page means we reached the last msg
            # Therefore, we also remove the file before leaving.
            if not size:
                os.unlink(fp)
                break

            from_msg = to_msg

            yield MBoxArchive(filename, archive_url)

    def __get_gmane_offset(self):
        offsets = [0]
        output_dir = self.mailing_list.compressed_dir

        _, _, files = os.walk(output_dir).next()
        for f in files:
            try:
                offsets.append(int(f))
            except ValueError:
                # We omit those files whose name is not a number (offset),
                # because for gmane mlstats names the files with the offset.
                pass

        return max(offsets)


class LocalArchive(BaseArchive):
    """Class to walk through mboxes stored locally."""

    def fetch(self):
        """Walk the mailing list directory looking for archives"""

        mailing_list = self.mailing_list

        if os.path.isfile(mailing_list.location):
            yield MBoxArchive(mailing_list.location, mailing_list.location)
        else:
            for root, dirs, files in os.walk(mailing_list.location):
                for filename in sorted(files):
                    location = os.path.join(root, filename)
                    yield MBoxArchive(location, location)


if __name__ == '__main__':
    import sys
    import pprint

    # Test case
    ml = MailingList(url_or_dirpath=sys.argv[1], compressed_dir=sys.argv[2])
    if ml.is_local():
        o = LocalArchive(ml)
    elif ml.location.startswith(GMANE_URL):
        o = GmaneArchive(ml)
    else:
        o = MailmanArchive(ml)

    o._create_download_dirs()

    for mla in o.fetch():
        pprint.pprint(mla.url)
