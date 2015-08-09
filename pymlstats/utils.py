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
Some utils functions for MLStats

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

from fileextractor import FileExtractor
import gzip
import os.path
import tempfile
import urllib
import urllib2
import shutil
import datetime
import cStringIO

COMPRESSED_TYPES = ['.gz', '.bz2', '.zip', '.tar',
                    '.tar.gz', '.tar.bz2', '.tgz', '.tbz']
ACCEPTED_TYPES = ['.mbox', '.txt']
EMAIL_OBFUSCATION_PATTERNS = [' at ', '_at_', ' en ']
MAILMAN_DATE_FORMAT = '%Y-%B'
MAILMAN_ALT_DATE_FORMAT = '%Y-%m'
MOD_MBOX_DATE_FORMAT = '%Y%m'


def current_month():
    """Get a tuple containing the current month in different formats"""
    # Assuming this is run daily, it's better to take yesterday's date,
    # to ensure we get all of last month's email when the month rolls over.
    yesterday = datetime.datetime.today() + datetime.timedelta(days=-1)

    this_month_mailman = yesterday.strftime(MAILMAN_DATE_FORMAT)
    this_month_mailman_alt = yesterday.strftime(MAILMAN_ALT_DATE_FORMAT)
    this_month_mod_mox = yesterday.strftime(MOD_MBOX_DATE_FORMAT)
    this_month = (this_month_mailman, this_month_mailman_alt,
                  this_month_mod_mox, )

    return this_month


def find_current_month(s):
    """Find the current month in the given string.

    If the month is found, the function will return a string
    containing the current month. Otherwise returns None."""
    for this_month in current_month():
        idx = s.find(this_month)
        if idx > -1:
            return this_month
    return None


def create_dirs(dirpath):
    """Wrapper to make directories"""
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def check_compressed_file(filename):
    """Check if filename is a compressed file supported by the tool.
    This function uses magic numbers to determine the type of the file.
    """
    # Reading the four fist bytes should be enough to
    # guess the file type.
    with open(filename) as f:
        magic_number = f.read(4)
    return file_type(magic_number)


def fetch_remote_resource(url, user=None, password=None):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 ' \
                 '(KHTML, like Gecko) Ubuntu/11.04 Chromium/15.0.871.0 ' \
                 'Chrome/15.0.871.0 Safari/535.2'
    headers = {'User-Agent': user_agent,
               'Accept-Encoding': 'gzip, deflate'}

    postdata = None
    if user:
        postdata = urllib.urlencode({'username': user, 'password': password})

    request = urllib2.Request(url, postdata, headers)
    response = urllib2.urlopen(request)
    data = response.read()

    if response.info().getheader('content-encoding') == 'gzip':
        data = cStringIO.StringIO(data)
        content = gzip.GzipFile(mode='r', compresslevel=0,
                                fileobj=data).read()
    else:
        content = data

    response.close()

    return content


def file_type(content):
    magic_dict = {
        '\x1f\x8b\x08': 'gz',
        '\x42\x5a\x68': 'bz2',
        '\x50\x4b\x03\x04': 'zip'
    }

    for magic, filetype in magic_dict.items():
        if content.startswith(magic):
            return filetype

    return None


def uncompress_file(filepath, extension, output_dir=None):
    """This function uncompress the file, and return
    the extension for the uncompressed file."""

    if not output_dir:
        output_dir = tempfile.mkdtemp()

    basename = os.path.basename(filepath)
    # Get new path to the uncompressed file
    new_filepath = os.path.join(output_dir, basename)

    extractor = FileExtractor()
    files = []

    if extension in COMPRESSED_TYPES:
        shutil.copy(filepath, output_dir)

    # Return a list of all the uncompressed files
    if '.zip' == extension:
        files = extractor.zipExtraction(new_filepath)
    elif extension in ['.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz']:
        files = extractor.tarExtraction(new_filepath)
    elif '.gz' == extension:
        # Return a list with only 1 element (the method returns a string)
        files = [extractor.gzExtraction(new_filepath)]
    elif '.bz2' == extension:
        # Return a list with only 1 element (the method returns a string)
        files = [extractor.bz2Extraction(new_filepath)]

    # We copied the compressed file to outputdir to uncompress it,
    # now we need to remove it and leave only the uncompressed file(s)
    if os.path.exists(new_filepath):
        os.unlink(new_filepath)

    return files

_dirs = {}


def get_home_dir():
    try:
        return _dirs['home']
    except KeyError:
        pass

    home_dir = None

    if 'HOME' in os.environ:
        home_dir = os.environ.get('HOME')
    else:
        if os.name == 'posix':
            import pwd
            home_dir = pwd.getpwuid(os.getuid()).pw_dir
        else:
            if 'USERPROFILE' in os.environ:
                home_dir = os.environ.get('USERPROFILE')
            elif 'HOMEPATH' in os.environ:
                try:
                    drive = os.environ.get('HOMEDRIVE')
                except KeyError:
                    drive = ''
                home_dir = os.path.join(drive, os.environ.get('HOMEPATH'))

    assert home_dir is not None

    _dirs['home'] = home_dir

    return home_dir


def mlstats_dot_dir():
    try:
        return _dirs['dot']
    except KeyError:
        _dirs['dot'] = os.path.join(get_home_dir(), '.mlstats')
        return _dirs['dot']

if __name__ == '__main__':
    print "mlstats dot dir: %s" % (mlstats_dot_dir())
