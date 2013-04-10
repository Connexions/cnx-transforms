# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Conversion callables"""
import os
import io
import logging
import subprocess


here = os.path.abspath(os.path.dirname(__file__))
OOCONVERT = os.path.join(here, 'helper-scripts', 'ooconvert.py')
logger = logging.getLogger('cnxtransforms')


class File(io.FileIO):
    """file stream"""
    filename = None
    basepath = None

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.filename = os.path.basename(self.name)
        self.basepath = os.path.abspath(os.path.dirname(self.name))

    @classmethod
    def from_io(cls, open_input):
        open_input.seek(0)
        filepointer, filepath = tempfile.mkstemp()  ##suffix=extension)
        with open(filepath, 'wb') as f:
            f.write(open_input.read())
        return cls(filepath)

    def __repr__(self):
        return "<{} instance of '{}'>".format(self.__class__.__name__,
                                              self.filepath)

    @property
    def filepath(self):
        return os.path.join(self.basepath, self.filename)


def word_to_odt(input, output=None, server_address=None, page_count_limit=0):
    """MS Word document to OpenOffice.org (OOo) document.

    :param input: An IO object to be converted.
    :type input: cnxtransforms.File
    :param output: An IO object to send the output.
    :type output: io.BytesIO
    :param server_address: Host and port of running *Office server
    :type server_address: string
    :param page_count_limit: ???
    :type page_count_limit: integer
    :returns: The output object used to write to output to.
    :rtype: cnxtransforms.File

    """
    # Sending *office the name of the imported word file (saved
    #  locally).
    file = input
    command = [OOCONVERT, file.filepath]
    if server_address:
        command.extend(['--address', server_address])
    if page_count_limit:
        command.extend(['--pagecount', page_count_limit])
    logger.info("Invoking converter: {}".format(' '.join(command)))

    if output is None:
        output = io.BytesIO()

    # TODO Send the document as binary via the input pipe,
    #      like how the result is returned.
    #      We are prevented from doing this now, because the ooconvert
    #      script is setup to accept a file rather than stdin.
    proc = subprocess.Popen(command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    # TODO A timeout parameter was added to communicate in Python 3.3.
    #      ...communicate(timeout=seconds)
    stdout, stderr = proc.communicate(file.read())
    output.write(stdout)

    if output.tell() == 0:
        logger.warning("*Office did returned nothing. "
                       "The *Office server may not be running.")
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

def odt_to_cnxml(input, output=None):
    """OpenOffice Document Text (ODT) conversion to Connexions XML (CNXML).

    :param input: An IO object to be converted.
    :type input: cnxtransforms.File
    :param output: An IO object to send the output.
    :type output: io.StringIO
    :returns: The output object used to write to output to.
    :rtype: io.StringIO

    """
    if output is None:
        output = io.StringIO()

    file = input
    if not isinstance(file, File):
        file = File.from_io(input)

    xml, resources, errors = odt2cnxml.transform(file.filepath)
    output.write(unicode(lxml.etree.tostring(xml)))
    for resource in resources:
        raise NotImplementedError

    return output
