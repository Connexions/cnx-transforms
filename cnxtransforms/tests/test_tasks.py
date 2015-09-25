# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import unittest
import zipfile
import pdb

EPUB = None
CALLBACK = None

here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(here, 'data')

class MakeEpub(unittest.TestCase):
    def make_one(self, file):
        from cnxepub import Package
        return Package.from_file(file)
    
    @property
    def target(self):
        from ..tasks import make_styled_epub
        return make_styled_epub
            
    def test_get_metadata(self):
        package_filepath = os.path.join(
            TEST_DATA_DIR, 'book',
            "9b0903d2-13c4-4ebe-9ffe-1ee79db28482@1.6.opf")
        package = self.make_one(package_filepath)
        
        expected_metadata = {
            'publisher': "Connexions",
            'publication_message': u'Nueva Versión',
            'identifier': "org.cnx.contents.9b0903d2-13c4-4ebe-9ffe-1ee79db28482@1.6",
            'title': "9b0903d2-13c4-4ebe-9ffe-1ee79db28482@1.6",
            'language': "en-us",
            'publisher': "Connexions",
            'license_text': "This work is shared with the public using the Attribution 3.0 Unported (CC BY 3.0) license.",
            'license_url': "http://creativecommons.org/licenses/by/3.0/",
            }
        self.assertEqual(package.metadata, expected_metadata)
        
    def test_makestyledepub(self):
        output_file = "my-epub.epub"
        epub = os.path.join(
            TEST_DATA_DIR, 'book',
            "simultaneous-equations-1.1.epub")
        styled_epub = self.target(epub, output_file, CALLBACK)
        
        
    


class MakePDF(unittest.TestCase):
    @property
    def target(self):
        from ..tasks import make_pdf
        return make_pdf
    
    def test_target(self):
        with self.assertRaises(NotImplementedError):
            self.target(EPUB,CALLBACK)

class MakeZip(unittest.TestCase):
    @property
    def target(self):
        from ..tasks import make_zip
        return make_zip
    
    def test_target(self):
        with self.assertRaises(NotImplementedError):
            self.target(EPUB,CALLBACK)

