# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2014, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
from .main import app


__all__ = (
    'make_epub', 'make_pdf', 'make_zip',
    )


@app.task
def make_epub(epub, callback=None):
    """Creates a human readable EPUB (EPUB3/EPUB2) artifact."""
    raise NotImplementedError()

@app.task
def make_pdf(epub, callback=None):
    """Creates a PDF artifact."""
    raise NotImplementedError()

@app.task
def make_zip(epub, callback=None):
    """Creates a legacy zip artifact (a.k.a. complete or offline zip)."""
    raise NotImplementedError()
