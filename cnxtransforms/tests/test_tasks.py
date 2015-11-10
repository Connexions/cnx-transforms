# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
import unittest

EPUB = None
CALLBACK = None

here = os.path.abspath(os.path.dirname(__file__))
TEST_DATA_DIR = os.path.join(here, 'data')
    
class MakeEpub(unittest.TestCase):
    @property
    def target(self):
        from ..tasks import make_styled_epub
        return make_styled_epub
        
    def test_makestyledepub(self):
        #sample epub directory
        epub = os.path.join(TEST_DATA_DIR, 'book')
        output_path = self.target(epub, CALLBACK)
        
        self.assertEqual(os.path.join(TEST_DATA_DIR, '9b0903d2-13c4-4ebe-9ffe-1ee79db28482-1.6.epub'), output_path[0])
        self.assertEqual(len(output_path), 1)
    

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

