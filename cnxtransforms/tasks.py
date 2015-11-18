# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import contextlib
import os
import shutil
import subprocess
import tempfile

from cnxepub import EPUB

from .main import app

####
## Test data directory for output, this will be changed in the future.
####
here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(here, 'tests/data')

__all__ = (
    'make_epub', 'make_pdf', 'make_zip',
    )   
    
# Context manager to make temporary folders to work with files, 
# magically removes it when used properly 
# (eg. with make_temp_directory() as dir:)
@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)
    
@app.task
def make_styled_epub(epub, callback=None):
    """Creates a human readable EPUB (EPUB3/EPUB2) artifact. Takes an EPUB instance from cnxepub."""
    
    python_executable = 'python'
    oerexports_dir = "/home/vagrant/production/oer.exports"
    output_dir = TEST_DATA_DIR
    
    epub = EPUB.from_file(epub)

    # Create a temporary directory to work in...
    with make_temp_directory() as build_dir:
        # Acquire the collection's data in a collection directory format.
        uuid = epub._packages[0].metadata['title'].split("@")[0]
        version = epub._packages[0].metadata["title"].split("@")[1]

        # Run the oer.exports script against the collection data.
        build_script = os.path.join(oerexports_dir, 'content2epub.py')
        result_filename = '{0}-{1}.epub'.format(uuid, version)
        result_filepath = os.path.join(build_dir, result_filename)
        output_filepath = os.path.join(output_dir, result_filename)
        
        epub.to_file(epub, result_filepath)

        command = [python_executable, build_script, uuid,
                   # The follow are not optional, values must be supplied.
                   '-t', 'collection',
                   '-c', os.path.join(oerexports_dir, 'static', 'content.css'),
                   '-e', os.path.join(oerexports_dir, 'xsl', 'dbk2epub.xsl'),
                   '-o', output_filepath,
                   ]
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=build_dir)
        stdout, stderr = process.communicate()
    
        # Move the file to it's final destination.
        shutil.copy2(result_filepath, output_dir)
        

    
    return [output_filepath]
    

@app.task
def make_pdf(epub, callback=None):
    """Creates a PDF artifact."""

    """rbit extension to interface with the oer.exports epub code.
    Available settings:
    - **output-dir** - Directory where the produced file is stuck.
    - **oer.exports-dir** - Defines the location of the oer.exports package.
    - **pdf-generator** - Executable location for wkhtml2pdf or princexml.
    - **python** - Defines which python executable should be used.
    """
    python_executable = settings.get('python', sys.executable)
    oerexports_dir = settings['oer.exports-dir']
    output_dir = settings['output-dir']
    pdf_generator_executable = settings['pdf-generator']

    # Create a temporary directory to work in...
    build_dir = tempfile.mkdtemp()
    logger.debug("Working in '{0}'.".format(build_dir))

    # Acquire the collection's data in a collection directory format.
    pkg_name = build_request.get_package()
    version = build_request.get_version()
    base_uri = build_request.transport.uri
    collection_dir = utils.get_offlinezip(pkg_name, version, base_uri,
                                           build_dir)
    collection_dir = os.path.join(build_dir, collection_dir, 'content')

    # FIXME We need to grab the version from the unpacked directory
    #       name because 'latest' is only a symbolic name that will
    #       not be used in the resulting filename.
    if version == 'latest':
        # Using the unpacked complete zip filename, with the structure
        #   <id>_<version>_complete, we can parse the version.
        version = collection_dir.split('_')[1]

    #Extract the print-style from the collection.xml
    printstyle_xsl = os.path.join(oerexports_dir,'xsl','collxml-print-style.xsl')
    collxml_path = os.path.join(collection_dir,'collection.xml')
    xslt = etree.XSLT(etree.parse(printstyle_xsl))
    collxml = etree.parse(collxml_path)
    printstyle = str(xslt(collxml)).strip()
    
    
    # Run the oer.exports script against the collection data.
    build_script = os.path.join(oerexports_dir, 'collectiondbk2pdf.py')
    result_filename = '{0}-{1}.pdf'.format(build_request.get_package(),
                                           version)
    result_filepath = os.path.join(build_dir, result_filename)
    command = [python_executable, build_script,
               '-p', pdf_generator_executable,
               '-d', collection_dir,
               # XXX We need a place to input this option...
               '-s', printstyle,
               result_filepath,
               ]
    logger.debug("Running: " + ' '.join(command))
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               cwd=build_dir)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        # Something went wrong...
        raise coyote.Failed("Unknown issue: \n" + stderr)
        return
    else:
        msg = "PDF created, moving contents to final destination..."
        logger.debug(msg)

    # Move the file to it's final destination.
    shutil.copy2(result_filepath, output_dir)
    output_filepath = os.path.join(output_dir, result_filename)

    # Remove the temporary build directory
    shutil.rmtree(build_dir)

    return [output_filepath]


@app.task
def make_zip(epub, callback=None):
    """Creates a legacy zip artifact (a.k.a. complete or offline zip)."""
    raise NotImplementedError()
