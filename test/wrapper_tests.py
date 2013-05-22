import os
import unittest
import cffi
import numpy as np
from FAUSTPy import FAUST

#################################
# test FAUST
#################################

def tearDownClass():
    cffi.verifier.cleanup_tmpdir(
        tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
    )

class test_faustwrapper_init(unittest.TestCase):

    def test_init(self):
        """Test initialisation of FAUST objects."""

        FAUST("dattorro_notch_cut_regalia.dsp", 48000)
        FAUST("dattorro_notch_cut_regalia.dsp", 48000, "float")
        FAUST("dattorro_notch_cut_regalia.dsp", 48000, "double")
        FAUST("dattorro_notch_cut_regalia.dsp", 48000, "long double")

    def test_init_inline_code(self):
        """Test initialisation of FAUST objects with inline FAUST code."""

        dsp = FAUST(b"process=*(0.5);", 48000)
        dsp = FAUST(b"process=*(0.5);", 48000, "float")
        dsp = FAUST(b"process=*(0.5);", 48000, "double")
        dsp = FAUST(b"process=*(0.5);", 48000, "long double")

    def test_init_wrong_args(self):
        """Test initialisation of FAUST objects with bad arguments."""

        self.assertRaises(ValueError, FAUST, "dattorro_notch_cut_regalia.dsp", 48000, "l double")

class test_faustwrapper(unittest.TestCase):

    def setUp(self):

        self.dsp1 = FAUST("dattorro_notch_cut_regalia.dsp", 48000)

        dsp_code = b"""
        declare name "Inline Test";
        declare author "Some Guy";

        process = *(0.5);
        """
        self.dsp2 = FAUST(dsp_code, 48000)

    def test_compute(self):
        """Test the compute() method."""

        audio = np.zeros((self.dsp2.dsp.num_in,48e3), dtype=self.dsp2.dsp.dtype)
        audio[0,0] = 1

        out = self.dsp2.compute(audio)

        self.assertEqual(out[0,0], audio[0,0]*0.5)
