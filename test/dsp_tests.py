import os
import unittest
import cffi
import numpy as np
from . helpers import init_ffi
from FAUSTPy import PythonDSP

#################################
# test PythonDSP
#################################

class test_faustdsp(unittest.TestCase):

    def setUp(self):

        self.ffi, self.C, self.faust_float = init_ffi()

        self.addCleanup(
            cffi.verifier.cleanup_tmpdir,
            tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
        )

    def test_init(self):
        "Test initialisation of PythonDSP objects."

        # TODO: how best to keep this test separate, yet in this class, without
        # recompiling the DSP in every test. Maybe I can just set self.dsp if
        # the method order of unittest is equal to the definition order.
        PythonDSP(self.C,self.ffi,self.faust_float,48000)

    def test_attributes(self):
        "Verify presence of various attributes."

        dsp = PythonDSP(self.C,self.ffi,self.faust_float,48000)
        self.assertTrue(hasattr(dsp, "fs"))
        self.assertTrue(hasattr(dsp, "num_in"))
        self.assertTrue(hasattr(dsp, "num_out"))
        self.assertTrue(hasattr(dsp, "faustfloat"))
        self.assertTrue(hasattr(dsp, "dtype"))

    def test_compute(self):
        "Test the compute() method."

        dsp = PythonDSP(self.C,self.ffi,self.faust_float,48000)
        audio = np.zeros((dsp.num_in,48e3), dtype=dsp.dtype)
        audio[:,0] = 1
        out = dsp.compute(audio)
