# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Conversion callables"""
import os
import logging
import subprocess
from io import FileIO

here = os.path.abspath(os.path.dirname(__file__))
OOCONVERT = os.path.join(here, 'helper-scripts', 'ooconvert.py')
logger = logging.getLogger('cnxtransforms')


class File(FileIO):
    """file stream"""
    filename = None
    basepath = None

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.filename = os.path.basename(self.name)
        self.basepath = os.path.abspath(os.path.dirname(self.name))

    def __repr__(self):
        return "<{} instance of '{}'>".format(self.__class__.__name__,
                                              self.filepath)

    @property
    def filepath(self):
        return os.path.join(self.basepath, self.filename)


def word_to_ooo(file, output=None, server_address=None, page_count_limit=0):
    """MS Word document to OpenOffice.org (OOo) document.

    :param file: The file object to be converted.
    :type file: cnxtransforms.Input
    :param server_address: Host and port of running *Office server
    :type server_address: string
    :param page_count_limit: ???
    :type page_count_limit: integer
    :returns: The output object used to write to output to.
    :rtype: cnxtransforms.File

    """
    # Quote the file name to prevent shell script expansion of any
    #   special characters in the file name.
    # Sending office the name of the imported word file (saved locally).
    command = [OOCONVERT, file.filepath]
    if server_address:
        command.extend(['--address', server_address])
    if page_count_limit:
        command.extend(['--pagecount', page_count_limit])
    logger.info("Invoking converter: {}".format(' '.join(command)))

    if output is None:
        output = File("{}.odt".format(file.filepath), 'w')

    # TODO Send the document as binary via the input pipe,
    #      like how the result is returned.
    proc = subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=output,
                            stderr=subprocess.PIPE,
                            )
    # TODO A timeout parameter was added to communicate in Python 3.3.
    #      ...communicate(timeout=seconds)
    junk, stderr = proc.communicate()
    del junk

    if proc.returncode != 0:
        raise Exception("Failed with stderr:\n{}".format(stderr))

    return output
