# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Conversion callables"""
import os
import sys
import io
import subprocess
import tempfile
import zipfile
try:
    from collections.abc import MutableSequence
except ImportError:
    # Pre Python 3.3
    from collections import MutableSequence

import magic
import lxml.etree
import rhaptos.cnxmlutils
import rhaptos.cnxmlutils.utils

from .reporting import logger


here = os.path.abspath(os.path.dirname(__file__))
OOCONVERT = os.path.join(here, 'helper-scripts', 'ooconvert.py')


# magic.Magic instances for specific mime-type and mime-encoding
#   discovery. This is necessary because the mime-type and
#   mime-encoding appear to be mutually exclusive in use.
_mime_type_magic = None
_mime_encoding_magic = None

def guess_mime_type(buf):
    """Like mimetypes.guess_type but accepts a buffer instead of a filepath.

    """
    global _mime_type_magic
    if _mime_type_magic is None:
        _mime_type_magic = magic.Magic(mime=True)
    try:
        return _mime_type_magic.from_buffer(buf.read())
    except AttributeError:
        return _mime_type_magic.from_buffer(buf)

def guess_mime_encoding(buf):
    """Guesses the encoding type for the given buffer."""
    global _mime_encoding_magic
    if _mime_encoding_magic is None:
        _mime_encoding_magic = magic.Magic(mime_encoding=True)
    try:
        return _mime_encoding_magic.from_buffer(buf.read())
    except AttributeError:
        return _mime_encoding_magic.from_buffer(buf)


class String(io.StringIO):
    """String buffer"""

    def __init__(self, data=None, name=None):
        super(String, self).__init__(data)
        self.name = name

    def __repr__(self):
        if self.name is not None:
            return "<{} instance of '{}'>".format(self.__class__.__name__,
                                                  self.name)
        else:
            return super(self.__class__, self).__repr__()


class Bytes(io.BytesIO):
    """Bytes buffer"""

    def __init__(self, data=None, name=None):
        super(Bytes, self).__init__(data)
        self.name = name

    def __repr__(self):
        if self.name is not None:
            return "<{} instance of '{}'>".format(self.__class__.__name__,
                                                  self.name)
        else:
            return super(self.__class__, self).__repr__()


def make_buffer(data, name):
    """Using the provided IO object, determine it's encoding to then create
    the buffer that corresponds with its encoding type.

    """
    encoding = guess_mime_encoding(data)
    if encoding == 'binary':
        buf = Bytes(data, name)
    else:
        if isinstance(data, str):
            data = unicode(data)
        buf = String(data, name)
    return buf


class File(io.FileIO):
    """File buffer"""
    filename = None
    basepath = None

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.filename = os.path.basename(self.name)
        self.basepath = os.path.abspath(os.path.dirname(self.name))

    @classmethod
    def from_io(cls, open_input):
        try:
            open_input.seek(0)
        except IOError:  # Caused by reading from sys.stdin
            pass
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


class FileSequence(MutableSequence):
    """Sequence of File buffers"""

    def __init__(self, file_sequence=()):
        """Can be initialized with a sequence of File objects."""
        self._seq = list(file_sequence)

    def __repr__(self):
        return repr(self._seq)

    @classmethod
    def from_zipfile(cls, zfile):
        """Given a ``zipfile.ZipFile`` as ``file`` produce a
        FileSequence instance.

        :param file: A zipfile
        :type file: zipfile.ZipFile

        """
        file_sequence = cls()
        for zinfo in zfile.infolist():
            # FIXME This is horrible, but nothing can be done about it
            #       because the zipfile implementation is lacking. In
            #       order to fix this raw data toss around bit,
            #       we'd need to redesign the zipfile library. =/
            buf = make_buffer(zfile.read(zinfo), zinfo.filename)
            file_sequence.append(buf)
        return file_sequence

    ###
    # MutableSequence abstraction methods
    ###

    def __getitem__(self, key):
        if not isinstance(key, (int, slice)):
            raise TypeError(key)
        return self._seq[key]

    def __setitem__(self, key, value):
        if not isinstance(key, (int, slice)):
            raise TypeError(key)
        self._seq[key] = value

    def __delitem__(self, key):
        if not isinstance(key, (int, slice)):
            raise TypeError(key)
        del self._seq[key]

    def __len__(self):
        return len(self._seq)

    def insert(self, index, value):
        self._seq.insert(index, value)

    def __next__(self):
        for v in self.seq:
            yield v
        raise StopIteration

    def __contains__(self, item):
        return item in self._seq


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
    if not isinstance(file, File):
        file = File.from_io(file)
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

    if output is not sys.stdout and output.tell() == 0:
        logger.warning("*Office returned nothing. "
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

def odt_to_cnxml(input, output=None, cnxml_index=0):
    """OpenOffice Document Text (ODT) conversion to Connexions XML (CNXML).

    :param input: An IO object to be converted.
    :type input: io.Bytes or cnxtransforms.File
    :param output: A sequence that has io capable elements
    :type output: cnxtransforms.FileSequence

    :param cnxml_index: index value of the index.cnxml document in the output
                        if the a designated output has been selected in the
                        sequence, defaults to 0
    :type cnxml_index: int

    :returns: A sequence that has io capable elements
    :rtype: cnxtransforms.FileSequence

    """
    # The rhaptos.cnxmlutils.odt2cnxml.transform function requires a
    #   file, so we make the input a file before moving forward.
    file = input
    if not isinstance(file, File):
        file = File.from_io(file)

    make_blank_cnxml_obj = lambda: String(name='index.cnxml')
    if output is None:
        cnxml = make_blank_cnxml_obj()
        output = FileSequence((cnxml,))
        cnxml_index = output.index(cnxml)
    elif not isinstance(output, FileSequence):
        raise TypeError("Output must be a FileSequence. '{}' of type "
                        "'{}' was given".format(output, type(output)))
    else:
        try:
            cnxml = output[cnxml_index]
        except IndexError:
            logger.warning("Couldn't find the specified output object "
                           "defined. Creating one and moving forward.")
            cnxml = make_blank_cnxml_obj()
            output.append(cnxml)
            cnxml_index = output.index(cnxml)

    transform = rhaptos.cnxmlutils.odt2cnxml.transform
    xml, resources, errors = transform(file.filepath)
    cnxml.write(unicode(lxml.etree.tostring(xml)))
    for name, data in resources.iteritems():
        output.append(Bytes(data, name=name))

    return output

def cnxml_to_html(input, output=None, cnxml_index=0, html_index=0):
    """Connexions XML (CNXML) conversion to HTML5.

    :param input: An io-like object or sequence containing io elements
    :type input: io.IOBase, cnxtransforms.String, cnxtransforms.File
                 or cnxtransforms.FileSequence
    :param output: A sequence that has io capable elements
    :type output: cnxtransforms.FileSequence

    :param cnxml_index: index value of the index.cnxml document in the input
                        if the a designated input has been selected in the
                        sequence, defaults to 0
    :type cnxml_index: int
    :param html_index: index value of the index.html document in the output
                       if the designated output has been slected in the
                       sequence, defaults to 0
    :type html_index: int

    :returns: A sequence that has io capable elements
    :rtype: cnxtransforms.FileSequence

    """
    # Handle multiple input formats
    if isinstance(input, file):
        cnxml = File.from_io(input)
    elif isinstance(input, io.IOBase):
        cnxml = input
    elif isinstance(input, FileSequence):
        cnxml = input[cnxml_index]
    else:
        raise TypeError("Input must be an IO or FileSequence object. '{}' "
                        "of type '{}' was given".format(input, type(input)))

    # Handle the output.
    make_blank_html_obj = lambda: String(name='index.html')
    if output is None:
        html = make_blank_html_obj()
        output = FileSequence((html,))
        html_index = output.index(html)
    elif not isinstance(output, FileSequence):
        raise TypeError("Output must be a FileSequence. '{}' of type "
                        "'{}' was given".format(output, type(output)))
    else:
        try:
            html = output[html_index]
        except IndexError:
            logger.warning("Couldn't find the specified output object "
                           "defined. Creating one and moving forward.")
            html = make_blank_html_obj()
            output.append(html)
            html_index = output.index(html)
    [output.append(b) for b in input if b is not cnxml]

    # Do the conversion
    xml = rhaptos.cnxmlutils.utils.cnxml_to_html(cnxml.read())
    html.write(unicode(xml))

    return output

def to_zipfile(input, output=None):
    """Take the input and zip it up! If you want a file writen, output must
    be an open file-like object.

    :param input: A cnxtransforms IO object
    :type input: cnxtransform.{String, Bytes, File} or
                 cnxtransforms.FileSequence
    :param output: An io object
    :type output: any io-like object

    :returns: A IO object containing zip data
    :rtype: io.BytesIO

    """
    if output is None:
        output = io.BytesIO

    allowed_io_types = (str, bytes, io.IOBase)
    allowed_container_types = (list, tuple, set, FileSequence)
    if isinstance(input, allowed_io_types):
        # Make it something we can iterate over.
        input = (input,)
    elif not isinstance(input, allowed_container_types):
        raise TypeError("Can't process the input object '{}' of type '{}'." \
                        .format(repr(input), type(input)))
    # else, we're good. :)

    # Note: It's not documented, but you can give a zipfile.ZipFile
    #       instance an open io-like object.
    with zipfile.ZipFile(output, 'w') as zip_file:
        for buf in input:
            # FIXME Need to make the name (or path) relative to the other
            #       contents for linking purposes.
            zip_info = zipfile.ZipInfo(buf.name)
            zip_info.external_attr = 0755 << 16L
            zip_file.writestr(zip_info, buf.getvalue())
    return output
