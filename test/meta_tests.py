import os
import unittest
import cffi
from . helpers import init_ffi, empty
from FAUSTPy import PythonMeta

#################################
# test PythonMeta
#################################

def tearDownModule():
    cffi.verifier.cleanup_tmpdir(
        tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
    )

class test_faustmeta(unittest.TestCase):

    def setUp(self):

        self.bla = empty()
        self.ffi, self.C = init_ffi()

        # grab the C object from the PythonMeta instance
        self.meta = PythonMeta(self.ffi, self.bla)

    def test_attributes(self):
        "Verify presence of various attributes."

        self.assertTrue(hasattr(self.meta, "meta"))
        self.assertTrue(hasattr(self.bla, "metadata"))

    def test_declare(self):
        "Test the declare() C callback."

        c_meta = self.meta.meta

        c_meta.declare(c_meta.mInterface, b"foo", b"bar")
        self.assertDictEqual(self.bla.metadata, {b"foo": b"bar"})
        c_meta.declare(c_meta.mInterface, b"baz", b"biz")
        self.assertDictEqual(self.bla.metadata, {b"foo": b"bar",
                                                 b"baz": b"biz"})
