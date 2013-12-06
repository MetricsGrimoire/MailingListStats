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

"""
This module contains a stricter mbox parser.  It is stricter to
determine when a new mail starts.  The default mailbox.mbox support
mboxo format, which fails to process some multipart archives.

@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import mailbox
import os
import re
from pymlstats.utils import EMAIL_OBFUSCATION_PATTERNS


class strict_mbox(mailbox.mbox):
    _fromlinepattern = (r'From \s*[^\s]+\s+\w\w\w\s+\w\w\w\s+\d?\d\s+'
                        r'\d?\d:\d\d(:\d\d)?(\s+[^\s]+)?\s+\d\d\d\d\s*'
                        r'[^\s]*\s*'
                        r'$')
    _regexp = None

    def __init__(self, path, factory=None, create=True):
        """Initialize an mbox mailbox."""
        self._message_factory = mailbox.mboxMessage
        mailbox.mbox.__init__(self, path, factory, create)

    def _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        while True:
            line_pos = self._file.tell()
            line = self._file.readline()
            if line.startswith('From ') and self._strict_isrealfromline(line):
                if len(stops) < len(starts):
                    stops.append(line_pos - len(os.linesep))
                starts.append(line_pos)
            elif line == '':
                stops.append(line_pos)
                break
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()

    def _strict_isrealfromline(self, line):
        if not self._regexp:
            self._regexp = re.compile(self._fromlinepattern)
        return self._regexp.match(self._check_spam_obscuring(line))

    def _check_spam_obscuring(self, line):
        if not line:
            return line

        for pattern in EMAIL_OBFUSCATION_PATTERNS:
            if line.find(pattern) != -1:
                return line.replace(pattern, '@')

        return line
