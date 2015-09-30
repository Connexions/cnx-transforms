# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import sys
import subprocess
import zipfile
import tempfile
import shutil
import contextlib

from cnxepub import EPUB

here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(here, 'data')

from .main import app


__all__ = (
    'make_epub', 'make_pdf', 'make_zip',
    )   
    
# Context manager to make temporary folders to work with files, magically removes it when used properly 
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
    output_dir = "/home/vagrant/"
    
    epub = EPUB.from_file(epub)

    # Create a temporary directory to work in...
    with make_temp_directory() as build_dir:
        # Acquire the collection's data in a collection directory format.
        pkg_name = epub._packages[0].metadata['title']
        version = epub._packages[0].metadata["title"].split("@")[1]
        #collection_dir = os.path.join(pkg_name, version)

        # Run the oer.exports script against the collection data.
        build_script = os.path.join(oerexports_dir, 'content2epub.py')
        result_filename = '{0}.epub'.format(pkg_name)
        result_filepath = os.path.join(build_dir, result_filename)
        
        epub.to_file(epub, result_filepath)

        command = [python_executable, build_script, pkg_name,
                   # The follow are not optional, values must be supplied.
                   '-t', 'collection',
                   '-c', os.path.join(oerexports_dir, 'static', 'content.css'),
                   '-e', os.path.join(oerexports_dir, 'xsl', 'dbk2epub.xsl'),
                   '-o', result_filepath,
                   ]
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=build_dir)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            # Something went wrong...
            print "Something went wrong with the transform."
    
        # Move the file to it's final destination.
        shutil.copy2(result_filepath, output_dir)
        output_filepath = os.path.join(output_dir, result_filename)

    
    return [output_filepath]
    

@app.task
def make_pdf(epub, callback=None):
    """Creates a PDF artifact."""
    raise NotImplementedError()

@app.task
def make_zip(epub, callback=None):
    """Creates a legacy zip artifact (a.k.a. complete or offline zip)."""
    raise NotImplementedError()
