# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os.path
import zipfile
import tempfile
import shutil
import contextlib

import cnxepub

from .main import app


__all__ = (
    'make_epub', 'make_pdf', 'make_zip',
    )

@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)
    
@app.task
def make_epub(epub, callback=None):
    """Creates a human readable EPUB (EPUB3/EPUB2) artifact."""
    
    output_file = "my-epub.epub"
    output_dir = ""
    
    with make_temp_directory() as build_dir:
        cnxepub.epub.unpack_epub(epub, build_dir)
            
        # move into the temporary directory to work on the book, here is where we can do things like add CSS...
        os.chdir(build_dir)
        
        
        # repackage the book with the cnxepub library
        cnxepub.epub.pack_epub(build_dir, output_file)
    
        # move this to it's final resting place or return it
        #shutil.copy(os.path.join(build_dir, output_file), output_dir)
        
        return []

@app.task
def make_pdf(epub, callback=None):
    """Creates a PDF artifact."""
    raise NotImplementedError()

@app.task
def make_zip(epub, callback=None):
    """Creates a legacy zip artifact (a.k.a. complete or offline zip)."""
    raise NotImplementedError()
