import os
import unittest
import cffi
import numpy as np
from . helpers import init_ffi
from FAUSTPy import PythonDSP

#################################
# test PythonDSP
#################################

def tearDownModule():
    cffi.verifier.cleanup_tmpdir(
        tmpdir=os.sep.join([os.path.dirname(__file__), "__pycache__"])
    )

class test_faustdsp_init(unittest.TestCase):

    def setUp(self):

        self.ffi, self.C = zip(*[init_ffi(faust_float=ff) for ff in
                                 ("float", "double", "long double")])

    def test_init_different_fs(self):
        """
        Test initialisation of PythonDSP objects with different values for the
        sampling rate.
        """

        # just try various sampling rates
        PythonDSP(self.C[0],self.ffi[0],32000)
        PythonDSP(self.C[0],self.ffi[0],44100)
        PythonDSP(self.C[0],self.ffi[0],48000)
        self.assertRaises(ValueError, PythonDSP, self.C[0], self.ffi[0], 0)
        self.assertRaises(ValueError, PythonDSP, self.C[0], self.ffi[0], -1)

    def test_init_different_faustfloats(self):
        """
        Test initialisation of PythonDSP objects with different values of
        FAUSTFLOAT.
        """

        # this should not do anything
        PythonDSP(self.C[0],self.ffi[0],48000)
        PythonDSP(self.C[1],self.ffi[1],48000)
        PythonDSP(self.C[2],self.ffi[2],48000)

    def test_init_bad_ffi_combos(self):
        """
        Test initialisation and .compute() of PythonDSP objects with
        incompatible compinations of FFILibrary and FFI objects.
        """

        # pairs of incompatible FFILibrary and FFI objects
        ffis = [(self.C[0], self.ffi[1]),
                (self.C[0], self.ffi[2]),
                (self.C[1], self.ffi[0]),
                (self.C[1], self.ffi[2]),
                (self.C[2], self.ffi[0]),
                (self.C[2], self.ffi[1])]

        # the init itself won't fail, but the type checking in later compute()'s
        # will; this is due to the fact that you cannot tell whether a
        # FFILibrary object come from a given FFI object or not
        for C, ffi in ffis:
            dsp = PythonDSP(C,ffi,48000)
            audio = np.zeros((dsp.num_in,48e3), dtype=dsp.dtype)
            audio[:,0] = 1
            self.assertRaises(TypeError, dsp.compute, audio)

class test_faustdsp(unittest.TestCase):

    def setUp(self):

        self.ffi1, self.C1 = init_ffi()
        self.ffi2, self.C2 = init_ffi(faust_dsp="test_synth.dsp")

        self.dsp   = PythonDSP(self.C1,self.ffi1,48000)
        self.synth = PythonDSP(self.C2,self.ffi2,48000)

    def tearDown(self):

        # TODO: for some reason, this prevents strange errors along the line of
        #
        # "Exception TypeError: "initializer for ctype 'struct $mydsp *' must be
        # a pointer to same type, not cdata 'struct $mydsp *'" in <bound method
        # PythonDSP.__del__ of <FAUSTPy.python_dsp.PythonDSP object at
        # 0x16cae50>> ignored"
        #
        # Find out why!
        del self.dsp
        del self.synth

    def test_attributes(self):
        "Verify presence of various attributes."

        self.assertTrue(hasattr(self.dsp, "dsp"))
        self.assertTrue(hasattr(self.dsp, "fs"))
        self.assertTrue(hasattr(self.dsp, "num_in"))
        self.assertTrue(hasattr(self.dsp, "num_out"))
        self.assertTrue(hasattr(self.dsp, "faustfloat"))
        self.assertTrue(hasattr(self.dsp, "dtype"))

    def test_compute(self):
        "Test the compute() method."

        audio = np.zeros((self.dsp.num_in,48e3), dtype=self.dsp.dtype)
        audio[:,0] = 1
        out = self.dsp.compute(audio)

    def test_compute_empty_input(self):
        "Test the compute() method with zero input samples."

        audio = np.zeros((self.dsp.num_in,0), dtype=self.dsp.dtype)
        out = self.dsp.compute(audio)
        self.assertEquals(out.size,0)

    def test_compute_bad_dtype(self):
        "Test the compute() method with inputs of incorrect dtype."

        for dtype in ("float64", "float128"):
            audio = np.zeros((self.dsp.num_in,48e3), dtype=dtype)
            audio[:,0] = 1
            self.assertRaises(ValueError, self.dsp.compute, audio)

    def test_compute_synth(self):
        "Test the compute() for synthesizer effects."

        count = 128
        ref = np.zeros((self.synth.num_out,count), dtype=self.synth.dtype)
        ref[:,::2] = 1
        out = self.synth.compute(count)
        self.assertTrue(np.all(ref==out))

    def test_compute_synth_zero_count(self):
        "Test the compute() for synthesizer effects with zero output samples."

        out = self.synth.compute(0)
        self.assertEquals(out.size, 0)

    def test_compute_synth_neg_count(self):
        """
        Test the compute() for synthesizer effects with negative output samples.
        """

        self.assertRaises(ValueError, self.synth.compute, -1)
