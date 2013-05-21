import os
import unittest
import cffi
from . helpers import init_ffi
from FAUSTPy import PythonMeta

#################################
# test PythonMeta
#################################

class test_faustmeta(unittest.TestCase):

    def setUp(self):

        class empty(object):
            pass
        self.bla = empty()

        self.ffi, self.C = init_ffi()

        self.addCleanup(
            cffi.verifier.cleanup_tmpdir,
            tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
        )

        # grab the C object from the PythonMeta instance
        self.meta = PythonMeta(self.ffi, self.bla)

    def test_attributes(self):
        "Verify presence of various attributes."

        self.assertTrue(hasattr(self.meta, "meta"))
        self.assertTrue(hasattr(self.bla, "metadata"))

    def test_declare(self):
        "Test the declare() C callback."

        c_meta = self.meta.meta

        c_meta.declare(self.ffi.NULL, b"foo", b"bar")
        self.assertDictEqual(self.bla.metadata, {b"foo": b"bar"})
        c_meta.declare(self.ffi.NULL, b"baz", b"biz")
        self.assertDictEqual(self.bla.metadata, {b"foo": b"bar",
                                                 b"baz": b"biz"})
