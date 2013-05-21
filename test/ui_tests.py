import os
import unittest
import cffi
from . helpers import init_ffi
from FAUSTPy import PythonUI

#################################
# test PythonUI
#################################

class test_faustui(unittest.TestCase):

    def setUp(self):

        class empty(object):
            pass
        self.bla = empty()

        self.ffi, self.C, self.faust_float = init_ffi()

        self.addCleanup(
            cffi.verifier.cleanup_tmpdir,
            tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
        )

    def test_init(self):
        "Test initialisation of PythonUI objects."

        PythonUI(self.ffi, "", self.bla)

    # TODO: split up these tests and complete them
    def test_misc(self):
        "Test miscellanea."

        ui = PythonUI(self.ffi, "", self.bla).ui
        ui.openVerticalBox(self.ffi.NULL,b"bla")
        self.assertEqual(self.bla.b_bla.layout, "vertical")

        slider_val = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(slider_val[0], 1.0)

        ui.addHorizontalSlider(self.ffi.NULL, b"float", slider_val, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.bla.b_bla, "p_float"))
        self.assertEqual(self.bla.b_bla.p_float.zone, 0.0)
        self.assertEqual(self.bla.b_bla.p_float.type, "HorizontalSlider")

        self.bla.b_bla.p_float.zone = 0.5
        self.assertEqual(self.bla.b_bla.p_float.zone, slider_val[0])

        ui.closeBox(self.ffi.NULL)

        button_val = self.ffi.new("FAUSTFLOAT*", 1.0)
        ui.addButton(self.ffi.NULL, b"float", button_val)
        self.assertTrue(hasattr(self.bla, "p_float"))
        self.assertEqual(self.bla.p_float.zone, 0.0)
        self.assertEqual(self.bla.p_float.type, "Button")
