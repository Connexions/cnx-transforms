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

    :param file: An IO object to be converted.
    :type file: cnxtransforms.File
    :param output: An IO object to send the output.
    :type output: cnxtransforms.File
    :param server_address: Host and port of running *Office server
    :type server_address: string
    :param page_count_limit: ???
    :type page_count_limit: integer
    :returns: The output object used to write to output to.
    :rtype: cnxtransforms.File

    """
    # Sending *office the name of the imported word file (saved locally).
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
        # Check to see if the document was too big.
        if stderr.startswith('Error (<class uno.com.sun.star.uno.Exception'):
            # sniff X for:  Input document has X pages which exceeeds
            #   the page count limit of Y.
            if re.match('.*Input document has ', stderr):
                msg = stderr[re.match('.*Input document has ', stderr).end():]
                if len(msg) > 0:
                    actual_page_count = msg.split(' ')[0]
                    if actual_page_count != msg:

                        raise Exception("Input word document contains {} "
                            "pages which exceeds the page count limit of {}. "
                            "The way forward (and best practice) is to "
                            "divide your doccument into smaller chunks. For "
                            "reference, the page count of an average word "
                            "import is about 5 pages." \
                            .format(actual_page_count, page_count_limit))
            raise Exception("Unknown error, stderr:\n{}".format(stderr))
        else:
            raise Exception("Unknown error, stderr:\n{}".format(stderr))

    return output
