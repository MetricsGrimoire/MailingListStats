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

import bz2
import gzip
import zipfile

import os.path
import urlparse

from htmlparser import MyHTMLParser
from utils import mlstats_dot_dir, check_compressed_file


COMPRESSED_DIR = os.path.join(mlstats_dot_dir(), 'compressed')


class MailingList(object):
    def __init__(self, url_or_dirpath, compressed_dir=COMPRESSED_DIR):
        rpath = url_or_dirpath.rstrip(os.path.sep)

        url = urlparse.urlparse(rpath)
        lpath = url.path.rstrip(os.path.sep)

        self._local = url.scheme == 'file' or len(url.scheme) == 0
        self._location = os.path.realpath(lpath) if self._local else rpath
        self._alias = os.path.basename(self._location) or url.netloc

        # Define local directories to store mboxes archives
        target = os.path.join(url.netloc, lpath.lstrip(os.path.sep))
        target = target.rstrip(os.path.sep)

        self._compressed_dir = os.path.join(compressed_dir, target)

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
