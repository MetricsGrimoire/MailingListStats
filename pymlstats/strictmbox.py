#-*- coding:utf-8 -*-
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
import email
from pymlstats.utils import EMAIL_OBFUSCATION_PATTERNS


class CustomMailbox(mailbox.UnixMailbox):
    """
        Custom mbox that can detect obscured email addressed at
        the beggining of each message.

        caveats: The class UnixMailbox has been deprecated and it
        is not available in 3.x. To add support for Python 3.x,
        copy the relevant code here.  It was deprecated because
        the class does not allow to modify the mbox, something
        that MLStats does not need."
    """
    def __init__(self, fp, factory=email.message_from_file):
        mailbox.UnixMailbox.__init__(self, fp, factory)

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

    _isrealfromline = _strict_isrealfromline
