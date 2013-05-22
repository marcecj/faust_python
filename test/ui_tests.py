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

        self.obj = empty()
        self.ffi, self.C = init_ffi()

        # grab the C object from the PythonUI instance
        self.ui = PythonUI(self.ffi, "", self.obj)

    def test_attributes(self):
        "Verify presence of various attributes."

        self.assertTrue(hasattr(self.ui, "ui"))

    def test_openVerticalBox(self):
        "Test the openVerticalBox C callback."

        c_ui = self.ui.ui

        c_ui.openVerticalBox(c_ui.uiInterface, b"box")
        c_ui.closeBox(c_ui.uiInterface)

        self.assertTrue(hasattr(self.obj, "b_box"))
        self.assertEqual(self.obj.b_box.layout, "vertical")
        self.assertEqual(self.obj.b_box.label, b"box")

    def test_openHorizontalBox(self):
        "Test the openHorizontalBox C callback."

        c_ui = self.ui.ui

        c_ui.openHorizontalBox(c_ui.uiInterface, b"box")
        c_ui.closeBox(c_ui.uiInterface)

        self.assertTrue(hasattr(self.obj, "b_box"))
        self.assertEqual(self.obj.b_box.layout, "horizontal")
        self.assertEqual(self.obj.b_box.label, b"box")

    def test_openTabBox(self):
        "Test the openTabBox C callback."

        c_ui = self.ui.ui

        c_ui.openTabBox(c_ui.uiInterface, b"box")
        c_ui.closeBox(c_ui.uiInterface)

        self.assertTrue(hasattr(self.obj, "b_box"))
        self.assertEqual(self.obj.b_box.layout, "tab")
        self.assertEqual(self.obj.b_box.label, b"box")

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

        self.assertTrue(hasattr(self.obj        , "b_box1"))
        self.assertTrue(hasattr(self.obj.b_box1 , "b_box2"))
        self.assertTrue(hasattr(self.obj.b_box1 , "b_box3"))
        self.assertTrue(hasattr(self.obj        , "b_box4"))

    def test_addHorizontalSlider(self):
        "Test the addHorizontalSlider C callback."

        c_ui = self.ui.ui

        param = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(param[0], 1.0)

        c_ui.addHorizontalSlider(c_ui.uiInterface, b"slider", param, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.obj, "p_slider"))
        self.assertEqual(self.obj.p_slider.label, b"slider")
        self.assertEqual(self.obj.p_slider.zone, 0.0)
        self.assertEqual(self.obj.p_slider.min, 0.0)
        self.assertEqual(self.obj.p_slider.max, 2.0)
        self.assertAlmostEqual(self.obj.p_slider.step, 0.1, 8)
        self.assertEqual(self.obj.p_slider.default, 0.0)
        self.assertEqual(self.obj.p_slider.metadata, {})
        self.assertEqual(self.obj.p_slider.type, "HorizontalSlider")

        self.obj.p_slider.zone = 0.5
        self.assertEqual(self.obj.p_slider.zone, param[0])

    def test_addVerticalSlider(self):
        "Test the addVerticalSlider C callback."

        c_ui = self.ui.ui

        param = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(param[0], 1.0)

        c_ui.addVerticalSlider(c_ui.uiInterface, b"slider", param, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.obj, "p_slider"))
        self.assertEqual(self.obj.p_slider.label, b"slider")
        self.assertEqual(self.obj.p_slider.zone, 0.0)
        self.assertEqual(self.obj.p_slider.min, 0.0)
        self.assertEqual(self.obj.p_slider.max, 2.0)
        self.assertAlmostEqual(self.obj.p_slider.step, 0.1, 8)
        self.assertEqual(self.obj.p_slider.default, 0.0)
        self.assertEqual(self.obj.p_slider.metadata, {})
        self.assertEqual(self.obj.p_slider.type, "VerticalSlider")

        self.obj.p_slider.zone = 0.5
        self.assertEqual(self.obj.p_slider.zone, param[0])

    def test_addNumEntry(self):
        "Test the addNumEntry C callback."

        c_ui = self.ui.ui

        param = self.ffi.new("FAUSTFLOAT*", 1.0)
        self.assertEqual(param[0], 1.0)

        c_ui.addNumEntry(c_ui.uiInterface, b"numentry", param, 0.0, 0.0, 2.0, 0.1)
        self.assertTrue(hasattr(self.obj, "p_numentry"))
        self.assertEqual(self.obj.p_numentry.label, b"numentry")
        self.assertEqual(self.obj.p_numentry.zone, 0.0)
        self.assertEqual(self.obj.p_numentry.min, 0.0)
        self.assertEqual(self.obj.p_numentry.max, 2.0)
        self.assertAlmostEqual(self.obj.p_numentry.step, 0.1, 8)
        self.assertEqual(self.obj.p_numentry.default, 0.0)
        self.assertEqual(self.obj.p_numentry.metadata, {})
        self.assertEqual(self.obj.p_numentry.type, "NumEntry")

        self.obj.p_numentry.zone = 0.5
        self.assertEqual(self.obj.p_numentry.zone, param[0])

    def test_addButton(self):
        "Test the addButton C callback."

        c_ui = self.ui.ui

        param = self.ffi.new("FAUSTFLOAT*", 1.0)
        c_ui.addButton(c_ui.uiInterface, b"button", param)
        self.assertTrue(hasattr(self.obj, "p_button"))
        self.assertEqual(self.obj.p_button.label, b"button")
        self.assertEqual(self.obj.p_button.zone, 0.0)
        self.assertEqual(self.obj.p_button.min, 0.0)
        self.assertEqual(self.obj.p_button.max, 1.0)
        self.assertEqual(self.obj.p_button.step, 1)
        self.assertEqual(self.obj.p_button.default, 0.0)
        self.assertEqual(self.obj.p_button.metadata, {})
        self.assertEqual(self.obj.p_button.type, "Button")

        self.obj.p_button.zone = 1
        self.assertEqual(self.obj.p_button.zone, param[0])

    def test_addToggleButton(self):
        "Test the addToggleButton C callback."

        c_ui = self.ui.ui

        param = self.ffi.new("FAUSTFLOAT*", 1.0)
        c_ui.addToggleButton(c_ui.uiInterface, b"button", param)
        self.assertTrue(hasattr(self.obj, "p_button"))
        self.assertEqual(self.obj.p_button.label, b"button")
        self.assertEqual(self.obj.p_button.zone, 0.0)
        self.assertEqual(self.obj.p_button.min, 0.0)
        self.assertEqual(self.obj.p_button.max, 1.0)
        self.assertEqual(self.obj.p_button.step, 1)
        self.assertEqual(self.obj.p_button.default, 0.0)
        self.assertEqual(self.obj.p_button.metadata, {})
        self.assertEqual(self.obj.p_button.type, "ToggleButton")

        self.obj.p_button.zone = 1
        self.assertEqual(self.obj.p_button.zone, param[0])

    def test_addCheckButton(self):
        "Test the addCheckButton C callback."

        c_ui = self.ui.ui

        param = self.ffi.new("FAUSTFLOAT*", 1.0)
        c_ui.addCheckButton(c_ui.uiInterface, b"button", param)
        self.assertTrue(hasattr(self.obj, "p_button"))
        self.assertEqual(self.obj.p_button.label, b"button")
        self.assertEqual(self.obj.p_button.zone, 0.0)
        self.assertEqual(self.obj.p_button.min, 0.0)
        self.assertEqual(self.obj.p_button.max, 1.0)
        self.assertEqual(self.obj.p_button.step, 1)
        self.assertEqual(self.obj.p_button.default, 0.0)
        self.assertEqual(self.obj.p_button.metadata, {})
        self.assertEqual(self.obj.p_button.type, "CheckButton")

        self.obj.p_button.zone = 1
        self.assertEqual(self.obj.p_button.zone, param[0])
