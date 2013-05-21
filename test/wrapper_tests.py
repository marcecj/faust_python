import os
import unittest
import cffi
import numpy as np
from FAUSTPy import FAUST

#################################
# test FAUST
#################################

class test_faustwrapper(unittest.TestCase):

    def setUp(self):

        self.addCleanup(
            cffi.verifier.cleanup_tmpdir,
            tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
        )

    def test_init(self):
        """Test initialisation of FAUST objects."""

        FAUST("dattorro_notch_cut_regalia.dsp", 48000)
        FAUST("dattorro_notch_cut_regalia.dsp", 48000, "float")
        FAUST("dattorro_notch_cut_regalia.dsp", 48000, "double")
        FAUST("dattorro_notch_cut_regalia.dsp", 48000, "long double")

    def test_init_inline_code(self):
        """Test initialisation of FAUST objects with inline FAUST code."""

        dsp = FAUST(b"process=_:*(0.5);", 48000)

        audio = np.zeros((dsp.dsp.num_in,48e3), dtype=dsp.dsp.dtype)
        audio[0,0] = 1

        out = dsp.compute(audio)

        self.assertEqual(out[0,0], audio[0,0]*0.5)

    def test_init_wrong_args(self):
        """Test initialisation of FAUST objects with bad arguments."""

        self.assertRaises(ValueError, FAUST, "dattorro_notch_cut_regalia.dsp", 48000, "l double")
