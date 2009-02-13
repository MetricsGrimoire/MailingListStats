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
Some utils functions for MLStats

@author:       Israel Herraiz
@organization: Libresoft Research Group, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

COMPRESSED_TYPES = ['.gz','.bz2','.zip','.tar','.tar.gz','.tar.bz2','.tgz','.tbz']
ACCEPTED_TYPES = ['.mbox','.txt']

from fileextractor import *
import os
import os.path
import tempfile
import urllib
import gzip
import bz2
import zipfile
import tarfile
import shutil


def check_compressed_file(filename):
    """Check if filename contains one of the extensions
    recognized as compressed file."""

    recognized_exts = COMPRESSED_TYPES
    
    # Check the two last extensions
    # (to recognize also composed extensions such as tar.gz)
    filename_noext1, ext1 = os.path.splitext(filename)
    filename_noexts, ext2 = os.path.splitext(filename_noext1)
    
    if ext2+"."+ext1 in recognized_exts:
        return ext2+"."+ext1

    if ext1 in recognized_exts:
        return ext1

    return None

def retrieve_remote_file(url,destfilename = None, web_user = None, web_password = None):
    """Retrieve a file from a remote location. It logins in the
    archives private page if necessary."""

    # If not dest dir, then store file in a temp file
    if not destfilename:
        destfilename = os.tmpnam()

    postdata = None
    if not web_user:
        urllib.urlretrieve(url,destfilename)
    else:
        postdata = urllib.urlencode( \
            {'username':web_user, \
            'password':web_password})
        
    urllib.urlretrieve(url,destfilename,data=postdata)

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

    # If destination already exists, assume it has been uncompressed before
    if os.path.exists(new_filepath_noext):
        # Return a list with only 1 element
        return [new_filepath_noext]

    extractor = FileExtractor()

    if '.zip' == extension:
        shutil.copy(filepath,output_dir)
        # Return a list of all the uncopressed files
        return extractor.zipExtraction(new_filepath)
    elif '.tar' == extension or \
            '.tar.gz' == extension or \
            '.tgz' == extension or \
            '.tar.bz2' == extension or \
            '.tbz' == extension:
        shutil.copy(filepath,output_dir)
        # Return a list of all the uncopressed files
        return extractor.tarExtraction(new_filepath)
    elif '.gz' == extension:
        shutil.copy(filepath,output_dir)
        # Return a list with only 1 element
        # (the method returns a string)
        return [extractor.gzExtraction(new_filepath)]
    elif '.bz2' == extension:
        shutil.copy(filepath,output_dir)
        # Return a list with only 1 element
        # (the method returns a string)
        return [extractor.bz2Extraction(new_filepath)]

    # Nothing extracted (file extension not recognized)
    return []
