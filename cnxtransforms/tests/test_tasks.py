import unittest
import zipfile
import pdb

EPUB = None
CALLBACK = None

class MakeEpub(unittest.TestCase):
    @property
    def target(self):
        from ..tasks import make_epub
        return make_epub
            
    def test_makeepub(self):
        epub = "cnxtransforms/tests/data/simultaneous-equations-1.1.epub"
        better_epub = self.target(epub, CALLBACK)
        #zipped_epub = zipfile.ZipFile(epub, "r")
        
        
    


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

