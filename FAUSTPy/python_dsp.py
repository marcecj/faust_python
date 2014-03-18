from numpy import atleast_2d, ndarray, float32, float64, float128


class PythonDSP(object):
    """A FAUST DSP wrapper.

    This class is more low-level than the FAUST class. It can be viewed as an
    abstraction that sits directly on top of the FAUST DSP struct.
    """

    def __init__(self, C, ffi, factory, dsp, fs):
        """Initialise a PythonDSP object.

        To instantiate this object, you create a cffi.FFI object that contains
        all required declarations (check the FAUSTPy.FAUST code for an
        example).  Then you compile the code via ffi.verify(), which creates an
        FFILibrary object.  Both of these are then passed to this constructor
        along with the other parameters specified below.

        Parameters:
        -----------

        C : cffi.FFILibrary
            The FFILibrary that represents the compiled code.
        ffi : cffi.FFI
            The CFFI instance that holds all the data type declarations.
        fs : int
            The sampling rate the FAUST DSP should be initialised with.
        """

        self.__C = C
        self.__ffi = ffi
        self.__faust_float = ffi.getctype("FAUSTFLOAT")
        self.__factory = factory
        self.__dsp = dsp
        self.metadata = {}

        if fs <= 0:
            raise ValueError("The sampling rate must have a positive value.")

        self.__fs = fs

        if self.__faust_float == "float":
            self.__dtype = float32
        elif self.__faust_float == "double":
            self.__dtype = float64
        elif self.__faust_float == "long double":
            self.__dtype = float128

        # calls both classInitCDSPInstance() and instanceInitCDSPInstance()
        C.initCDSPInstance(dsp, int(fs))

        # allocate the input and output pointers so that they are not
        # allocated/deallocated at every call to compute()
        # TODO: can the number of inputs/outputs change at run time?
        self.__input_p = self.__ffi.new("FAUSTFLOAT*[]", self.num_in)
        self.__output_p = self.__ffi.new("FAUSTFLOAT*[]", self.num_out)

    def __del__(self):

        self.__C.deleteCDSPInstance(self.__dsp)
        self.__C.deleteCDSPFactory(self.__factory)

    dsp = property(fget=lambda x: x.__dsp,
                   doc="The DSP struct that calls back to its parent object.")

    dtype = property(fget=lambda x: x.__dtype,
                     doc="A dtype corresponding to the value of FAUSTFLOAT.")

    faustfloat = property(fget=lambda x: x.__faust_float,
                          doc="The value of FAUSTFLOAT for this DSP.")

    fs = property(fget=lambda s: s.__fs,
                  doc="The sampling rate of the DSP.")

    num_in = property(fget=lambda s: s.__C.getNumInputsCDSPInstance(s.__dsp),
                      doc="The number of input channels.")

    num_out = property(fget=lambda s: s.__C.getNumOutputsCDSPInstance(s.__dsp),
                       doc="The number of output channels.")

    def compute(self, audio):
        """
        Process an ndarray with the FAUST DSP.

        Parameters:
        -----------

        The first argument depends on the type of DSP (synthesizer or effect):

        audio : numpy.ndarray
            If the DSP is an effect (i.e., it processes input data and produces
            output), the first argument is an audio signal to process.

        or

        count : int
            If the DSP is a synthesizer (i.e., it has zero inputs and produces
            output), the first argument is the number of output samples to
            produce

        Returns:
        --------

        out : numpy.ndarray
            The output of the DSP.

        Notes:
        ------

        This function uses the buffer protocol to avoid copying the input data.
        """

        if self.num_in > 0:
            # returns a view, so very little overhead
            audio = atleast_2d(audio)

            # Verify that audio.dtype == self.dtype, because a) Python
            # SEGFAULTs when audio.dtype < self.dtype and b) the computation is
            # garbage when audio.dtype > self.dtype.
            if audio.dtype != self.__dtype:
                raise ValueError("audio.dtype must be {}".format(self.__dtype))

            count = audio.shape[1]  # number of samples
            num_in = self.num_in    # number of input channels

            # set up the input pointers
            for i in range(num_in):
                self.__input_p[i] = self.__ffi.cast('FAUSTFLOAT *',
                                                    audio[i].ctypes.data)
        else:
            # special case for synthesizers: the input argument is the number
            # of samples
            count = audio

        num_out = self.num_out   # number of output channels

        # initialise the output array
        output = ndarray((num_out, count), dtype=self.__dtype)

        # set up the output pointers
        for i in range(num_out):
            self.__output_p[i] = self.__ffi.cast('FAUSTFLOAT *',
                                                 output[i].ctypes.data)

        # call the DSP
        self.__C.computeCDSPInstance(self.__dsp, count, self.__input_p,
                                     self.__output_p)

        return output

    # TODO: Run some more serious tests to check whether compute2() is worth
    # keeping, because with the bundled DSP the run-time is about 83 us for
    # 2x64 samples versus about 90 us for compute(), so only about 7 us
    # difference.
    def compute2(self, audio):
        """
        Process an ndarray with the FAUST DSP, like compute(), but without any
        safety checks.  NOTE: compute2() can crash Python if "audio" is an
        incompatible NumPy array!

        This function is only useful if the DSP is an effect since the checks
        not made here do not apply to synthesizers.

        Parameters:
        -----------

        audio : numpy.ndarray
            The audio signal to process.

        Returns:
        --------

        out : numpy.ndarray
            The output of the DSP.

        Notes:
        ------

        This function uses the buffer protocol to avoid copying the input data.
        """

        count = audio.shape[1]  # number of samples
        num_in = self.num_in    # number of input channels
        num_out = self.num_out  # number of output channels

        # initialise the output array
        output = ndarray((num_out, count), dtype=audio.dtype)

        # set up the output pointers
        for i in range(num_out):
            self.__output_p[i] = self.__ffi.cast('FAUSTFLOAT *',
                                                 output[i].ctypes.data)

        # set up the input pointers
        for i in range(num_in):
            self.__input_p[i] = self.__ffi.cast('FAUSTFLOAT *',
                                                audio[i].ctypes.data)

        # call the DSP
        self.__C.computeCDSPInstance(self.__dsp, count, self.__input_p,
                                     self.__output_p)

        return output
