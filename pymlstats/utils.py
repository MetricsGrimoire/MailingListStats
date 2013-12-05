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
Some utils functions for MLStats

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

from fileextractor import *
import os.path
import tempfile
import urllib
import urllib2
import shutil
import datetime

COMPRESSED_TYPES = ['.gz', '.bz2', '.zip', '.tar', '.tar.gz', '.tar.bz2', '.tgz', '.tbz']
ACCEPTED_TYPES = ['.mbox', '.txt']
EMAIL_OBFUSCATION_PATTERNS = [' at ', '_at_', ' en ']
MAILMAN_DATE_FORMAT = '%Y-%B'


def current_month():
    """Get the current month"""
    # Assuming this is run daily, it's better to take yesterday's date,
    # to ensure we get all of last month's email when the month rolls over.
    yesterday = datetime.datetime.today() + datetime.timedelta(days=-1)
    this_month = yesterday.strftime(MAILMAN_DATE_FORMAT)
    return this_month


def create_dirs(dirpath):
    """Wrapper to make directories"""
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def check_compressed_file(filename):
    """Check if filename contains one of the extensions
    recognized as compressed file."""

    recognized_exts = COMPRESSED_TYPES
    
    # Check the two last extensions
    # (to recognize also composed extensions such as tar.gz)
    filename_noext, ext = os.path.splitext(filename)
    long_ext = ''.join([os.path.splitext(filename_noext)[1], ext])

    if long_ext in recognized_exts:
        return long_ext

    if ext in recognized_exts:
        return ext

    return None

def retrieve_remote_file(url, destfilename=None, web_user=None, web_password=None):
    """Retrieve a file from a remote location. It logins in the
    archives private page if necessary."""

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 ' \
                 '(KHTML, like Gecko) Ubuntu/11.04 Chromium/15.0.871.0 ' \
                 'Chrome/15.0.871.0 Safari/535.2'
    headers = { 'User-Agent': user_agent }

    # If not dest dir, then store file in a temp file
    if not destfilename:
        destfilename = os.tmpnam()

    postdata = None
    if web_user:
        postdata = urllib.urlencode({'username': web_user,
                                     'password': web_password})

    request = urllib2.Request(url, postdata, headers)
    response = urllib2.urlopen(request)
    subtype = response.info().getsubtype()
 
    if url.endswith ('.gz') and subtype and subtype.endswith('plain'):
        fd = gzip.GzipFile(destfilename, 'wb')
    else:
        fd = open(destfilename, 'wb')
        
    fd.write(response.read())
    fd.close()
    response.close ()

    return destfilename

def uncompress_file(filepath,extension, output_dir = None):
    """This function uncompress the file, and return
    the extension for the uncompressed file."""

    if not output_dir:
        output_dir = tempfile.mkdtemp()
    
    basename = os.path.basename(filepath)
    # Remove extension from filename
    basename_noext = basename.rstrip(extension)
    # Get new path to the uncompressed file
    new_filepath = os.path.join(output_dir,basename)
    new_filepath_noext = os.path.join(output_dir,basename_noext)

    extractor = FileExtractor()
    files = []

    if extension in COMPRESSED_TYPES:
        shutil.copy(filepath,output_dir)

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

def get_home_dir ():
    try:
        return _dirs['home']
    except KeyError:
        pass
    
    home_dir = None
    
    if 'HOME' in os.environ:
        home_dir = os.environ.get ('HOME')
    else:
        if os.name == 'posix':
            import pwd
            home_dir = pwd.getpwuid (os.getuid ()).pw_dir
        else:
            if 'USERPROFILE' in os.environ:
                home_dir = os.environ.get ('USERPROFILE')
            elif 'HOMEPATH' in os.environ:
                try:
                    drive = os.environ.get ('HOMEDRIVE')
                except KeyError:
                    drive = ''
                home_dir = os.path.join (drive, os.environ.get ('HOMEPATH'))
                
    assert home_dir is not None

    _dirs['home'] = home_dir
    
    return home_dir

def mlstats_dot_dir ():
    try:
        return _dirs['dot']
    except KeyError:
        _dirs['dot'] = os.path.join(get_home_dir (), '.mlstats')
        return _dirs['dot']

if __name__ == '__main__':
    print "mlstats dot dir: %s" % (mlstats_dot_dir ())
