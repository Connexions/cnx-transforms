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

from .main import app


__all__ = (
    'make_epub', 'make_pdf', 'make_zip',
    )


@app.task
def make_epub(epub, callback=None):
    """Creates a human readable EPUB (EPUB3/EPUB2) artifact."""
    build_dir = tempfile.gettempdir()
    output_file = "my-epub.epub"
    output_dir = ""
    
    # extract the existing book
    with zipfile.ZipFile(epub, "r") as cnx_epub:
        files = cnx_epub.namelist()
        files_to_extract = [m for m in files]
        #extract book into our temporary directory
        cnx_epub.extractall(build_dir, files_to_extract)
        
    # move into the temporary directory to work on the book
    os.chdir(build_dir)
    
    # here is where we will be modifying the contents (like adding CSS)
    with zipfile.ZipFile(output_file, 'w') as epub:
    
        # add mimetype (must be first!)
        with open("mimetype", "r") as mime:
            epub.writestr("mimetype", mime.read().replace('\n', ''))
    
        # add META information
        with open("META-INF/container.xml", "r") as meta:
            epub.writestr("META-INF/container.xml", meta.read())
    
        # content
        for (root, dirs, files) in os.walk('content'):
            for file in files:
                file_path = os.path.join(root, file)
                epub.write(file_path)
    
        #resources
        for (root, dirs, files) in os.walk('resources'):
            for file in files:
                file_path = os.path.join(root, file)
                epub.write(file_path)
    
    # move this to it's final resting place
    # make sure temp data dir is removed, or the data that was created is removed?
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
