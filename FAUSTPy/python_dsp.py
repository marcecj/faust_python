from numpy import atleast_2d, ndarray, float32, float64, float128

FAUSTFLOATS = frozenset(("float", "double", "long double"))

class FAUSTDsp(object):
    """A FAUST DSP wrapper.

    This class is more low-level than the FAUST class. It can be viewed as an
    abstraction that sits directly on top of the FAUST DSP struct.
    """

    def __init__(self, C, ffi, faust_float, fs, faust_ui):
        """Initialise a FAUSTDsp object.

        To instantiate this object, you create a cffi.FFI object that contains
        all required declarations (check the FAUSTPy.FAUST code for an example).
        Then you compile the code via ffi.verfiy(), which creates an FFILibrary
        object.  Both of these are then passed to this constructor along with
        the other parameters specified below.

        Parameters:
        -----------

        C : cffi.FFILibrary
            The FFILibrary that represents the compiled code.
        ffi : cffi.FFI
            The CFFI instance that holds all the data type declarations.
        faust_float : string
            The value of the FAUSTFLOAT type.  This is used internally by FAUST
            to generalise to different precisions. Possible values are "float",
            "double" or "long double".
        fs : int
            The sampling rate the FAUST DSP should be initialised with.
        faust_ui : FAUSTPy.PythonUI-like
            A class that implements the UIGlue C type.
        """

        if faust_float not in FAUSTFLOATS:
            raise ValueError("Invalid value for faust_float!")

        self.__C   = C
        self.__ffi = ffi
        self.__faust_float = faust_float
        self.__dsp = C.newmydsp()

        if   faust_float == "float":
            self.__dtype = float32
        elif faust_float == "double":
            self.__dtype = float64
        elif faust_float == "long double":
            self.__dtype = float128

        # calls both classInitmydsp() and instanceInitmydsp()
        C.initmydsp(self.__dsp, fs)
        UI = faust_ui(self.__ffi, self)
        C.buildUserInterfacemydsp(self.__dsp, UI.ui)

        # self.__meta = MetaGlue()
        # self._metadata = C.metadatamydsp(meta)

        # allocate the input and output pointers so that they are not
        # allocated/deallocated at every call to compute()
        # TODO: can the number of inputs/outputs change at run time?
        self.__input_p  = self.__ffi.new("FAUSTFLOAT*[]", self.num_in)
        self.__output_p = self.__ffi.new("FAUSTFLOAT*[]", self.num_out)

    def __del__(self):
        """Deallocate the FAUST DSP object.

        This method makes sure to properly deallocate the internal C data
        structures (as required).
        """

        self.__C.deletemydsp(self.__dsp)

    def compute(self, audio):
        """
        Process an ndarray with the FAUST DSP.

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

        # returns a view, so very little overhead
        audio = atleast_2d(audio)

        # Verify that audio.dtype == self.dtype, because a) Python SEGFAULTs
        # when audio.dtype < self.dtype and b) the computation is garbage when
        # audio.dtype > self.dtype.
        if audio.dtype != self.__dtype:
            raise ValueError("audio.dtype must be {}".format(self.__dtype))

        count   = audio.shape[1] # number of samples
        num_in  = self.num_in    # number of input channels
        num_out = self.num_out   # number of output channels

        # initialise the output array
        output = ndarray((num_out,count), dtype=audio.dtype)

        # set up the output pointers
        for i in range(num_out):
            self.__output_p[i] = self.__ffi.cast('FAUSTFLOAT *',
                                                 output[i].ctypes.data)

        # set up the input pointers
        for i in range(num_in):
            self.__input_p[i] = self.__ffi.cast('FAUSTFLOAT *',
                                                audio[i].ctypes.data)

        # call the DSP
        self.__C.computemydsp(self.__dsp, count, self.__input_p, self.__output_p)

        return output

    dtype = property(fget=lambda x: x.__dtype,
                     doc="A dtype corresponding to the value of FAUSTFLOAT.")
    faustfloat = property(fget=lambda x: x.__faust_float,
                          doc="The value of FAUSTFLOAT for this DSP.")
    fs = property(fget=lambda s: s.__C.getSampleRatemydsp(s.__dsp),
                 doc="The sampling rate of the DSP.")
    num_in = property(fget=lambda s: s.__C.getNumInputsmydsp(s.__dsp),
                      doc="The number of input channels.")
    num_out = property(fget=lambda s: s.__C.getNumOutputsmydsp(s.__dsp),
                       doc="The number of output channels.")
