import os
import unittest
import cffi
from . helpers import init_ffi, empty
from FAUSTPy import PythonUI

#################################
# test PythonUI
#################################

def tearDownModule():
    cffi.verifier.cleanup_tmpdir(
        tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
    )

class test_faustui(unittest.TestCase):

    def setUp(self):

        self.bla = empty()
        self.ffi, self.C = init_ffi()

        # grab the C object from the PythonUI instance
        self.ui = PythonUI(self.ffi, "", self.bla)

    def test_attributes(self):

        self.assertTrue(hasattr(self.ui, "ui"))

    def test_openVerticalBox(self):
        "Test the openVerticalBox C callback."

        c_ui = self.ui.ui

        c_ui.openVerticalBox(c_ui.uiInterface, b"foo")
        self.assertTrue(hasattr(self.bla, "b_foo"))
        self.assertEqual(self.bla.b_foo.layout, "vertical")
        self.assertEqual(self.bla.b_foo.label, b"foo")
        c_ui.closeBox(c_ui.uiInterface)

    def test_openHorizontalBox(self):
        "Test the openHorizontalBox C callback."

        c_ui = self.ui.ui

        c_ui.openHorizontalBox(c_ui.uiInterface, b"bar")
        self.assertTrue(hasattr(self.bla, "b_bar"))
        self.assertEqual(self.bla.b_bar.layout, "horizontal")
        self.assertEqual(self.bla.b_bar.label, b"bar")
        c_ui.closeBox(c_ui.uiInterface)

    def test_openTabBox(self):
        "Test the openTabBox C callback."

        c_ui = self.ui.ui

        c_ui.openTabBox(c_ui.uiInterface, b"baz")
        self.assertTrue(hasattr(self.bla, "b_baz"))
        self.assertEqual(self.bla.b_baz.layout, "tab")
        self.assertEqual(self.bla.b_baz.label, b"baz")
        c_ui.closeBox(c_ui.uiInterface)

    def test_closeBox(self):
        "Test the closeBox C callback."

        c_ui = self.ui.ui

        c_ui.openVerticalBox(c_ui.uiInterface, b"box1")
        c_ui.openHorizontalBox(c_ui.uiInterface, b"box2")
        c_ui.closeBox(c_ui.uiInterface)
        c_ui.openTabBox(c_ui.uiInterface, b"box3")
        c_ui.closeBox(c_ui.uiInterface)
        c_ui.closeBox(c_ui.uiInterface)
        c_ui.openTabBox(c_ui.uiInterface, b"box4")
        c_ui.closeBox(c_ui.uiInterface)

        self.assertTrue(hasattr(self.bla        , "b_box1"))
        self.assertTrue(hasattr(self.bla.b_box1 , "b_box2"))
        self.assertTrue(hasattr(self.bla.b_box1 , "b_box3"))
        self.assertTrue(hasattr(self.bla        , "b_box4"))

    def test_addHorizontalSlider(self):
        "Test the addHorizontalSlider C callback."

        c_ui = self.ui.ui

        slider_val0 = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(slider_val0[0], 1.0)

        c_ui.addHorizontalSlider(c_ui.uiInterface, b"slider0", slider_val0, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.bla, "p_slider0"))
        self.assertEqual(self.bla.p_slider0.label, b"slider0")
        self.assertEqual(self.bla.p_slider0.zone, 0.0)
        self.assertEqual(self.bla.p_slider0.min, 0.0)
        self.assertEqual(self.bla.p_slider0.max, 2.0)
        self.assertAlmostEqual(self.bla.p_slider0.step, 0.1, 8)
        self.assertEqual(self.bla.p_slider0.default, 0.0)
        self.assertEqual(self.bla.p_slider0.metadata, {})
        self.assertEqual(self.bla.p_slider0.type, "HorizontalSlider")

        self.bla.p_slider0.zone = 0.5
        self.assertEqual(self.bla.p_slider0.zone, slider_val0[0])

    def test_addVerticalSlider(self):
        "Test the addVerticalSlider C callback."

        c_ui = self.ui.ui

        slider_val1 = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(slider_val1[0], 1.0)

        c_ui.addVerticalSlider(c_ui.uiInterface, b"slider1", slider_val1, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.bla, "p_slider1"))
        self.assertEqual(self.bla.p_slider1.label, b"slider1")
        self.assertEqual(self.bla.p_slider1.zone, 0.0)
        self.assertEqual(self.bla.p_slider1.min, 0.0)
        self.assertEqual(self.bla.p_slider1.max, 2.0)
        self.assertAlmostEqual(self.bla.p_slider1.step, 0.1, 8)
        self.assertEqual(self.bla.p_slider1.default, 0.0)
        self.assertEqual(self.bla.p_slider1.metadata, {})
        self.assertEqual(self.bla.p_slider1.type, "VerticalSlider")

        self.bla.p_slider1.zone = 0.5
        self.assertEqual(self.bla.p_slider1.zone, slider_val1[0])

    def test_addNumEntry(self):
        "Test the addNumEntry C callback."

        c_ui = self.ui.ui

        slider_val2 = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(slider_val2[0], 1.0)

        c_ui.addNumEntry(c_ui.uiInterface, b"slider2", slider_val2, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.bla, "p_slider2"))
        self.assertEqual(self.bla.p_slider2.label, b"slider2")
        self.assertEqual(self.bla.p_slider2.zone, 0.0)
        self.assertEqual(self.bla.p_slider2.min, 0.0)
        self.assertEqual(self.bla.p_slider2.max, 2.0)
        self.assertAlmostEqual(self.bla.p_slider2.step, 0.1, 8)
        self.assertEqual(self.bla.p_slider2.default, 0.0)
        self.assertEqual(self.bla.p_slider2.metadata, {})
        self.assertEqual(self.bla.p_slider2.type, "NumEntry")

        self.bla.p_slider2.zone = 0.5
        self.assertEqual(self.bla.p_slider2.zone, slider_val2[0])

    def test_addButton(self):
        "Test the addButton C callback."

        c_ui = self.ui.ui

        button_val0 = self.ffi.new("FAUSTFLOAT*", 1.0)
        c_ui.addButton(c_ui.uiInterface, b"but0", button_val0)
        self.assertTrue(hasattr(self.bla, "p_but0"))
        self.assertEqual(self.bla.p_but0.label, b"but0")
        self.assertEqual(self.bla.p_but0.zone, 0.0)
        self.assertEqual(self.bla.p_but0.min, 0.0)
        self.assertEqual(self.bla.p_but0.max, 1.0)
        self.assertEqual(self.bla.p_but0.step, 1)
        self.assertEqual(self.bla.p_but0.default, 0.0)
        self.assertEqual(self.bla.p_but0.metadata, {})
        self.assertEqual(self.bla.p_but0.type, "Button")

        self.bla.p_but0.zone = 1
        self.assertEqual(self.bla.p_but0.zone, button_val0[0])

    def test_addToggleButton(self):
        "Test the addToggleButton C callback."

        c_ui = self.ui.ui

        button_val1 = self.ffi.new("FAUSTFLOAT*", 1.0)
        c_ui.addToggleButton(c_ui.uiInterface, b"but1", button_val1)
        self.assertTrue(hasattr(self.bla, "p_but1"))
        self.assertEqual(self.bla.p_but1.label, b"but1")
        self.assertEqual(self.bla.p_but1.zone, 0.0)
        self.assertEqual(self.bla.p_but1.min, 0.0)
        self.assertEqual(self.bla.p_but1.max, 1.0)
        self.assertEqual(self.bla.p_but1.step, 1)
        self.assertEqual(self.bla.p_but1.default, 0.0)
        self.assertEqual(self.bla.p_but1.metadata, {})
        self.assertEqual(self.bla.p_but1.type, "ToggleButton")

        self.bla.p_but1.zone = 1
        self.assertEqual(self.bla.p_but1.zone, button_val1[0])

    def test_addCheckButton(self):
        "Test the addCheckButton C callback."

        c_ui = self.ui.ui

        button_val2 = self.ffi.new("FAUSTFLOAT*", 1.0)
        c_ui.addCheckButton(c_ui.uiInterface, b"but2", button_val2)
        self.assertTrue(hasattr(self.bla, "p_but2"))
        self.assertEqual(self.bla.p_but2.label, b"but2")
        self.assertEqual(self.bla.p_but2.zone, 0.0)
        self.assertEqual(self.bla.p_but2.min, 0.0)
        self.assertEqual(self.bla.p_but2.max, 1.0)
        self.assertEqual(self.bla.p_but2.step, 1)
        self.assertEqual(self.bla.p_but2.default, 0.0)
        self.assertEqual(self.bla.p_but2.metadata, {})
        self.assertEqual(self.bla.p_but2.type, "CheckButton")

        self.bla.p_but2.zone = 1
        self.assertEqual(self.bla.p_but2.zone, button_val2[0])
