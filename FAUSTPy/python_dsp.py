from numpy import atleast_2d, ndarray
from ctypes import addressof, c_void_p

class FAUSTDsp(object):

    def __init__(self, C, ffi, fs, faust_ui):

        self.__C   = C
        self.__ffi = ffi
        self.__dsp = C.newmydsp()

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

        self.__C.deletemydsp(self.__dsp)

    def compute(self, audio):

        audio = atleast_2d(audio)

        count   = audio.shape[1] # number of samples
        num_in  = self.num_in
        num_out = self.num_out

        output = ndarray((num_out,count), dtype=audio.dtype)
        for i in range(num_out):
            in_addr = addressof(c_void_p.from_buffer(output[i]))
            self.__output_p[i] = self.__ffi.cast('FAUSTFLOAT *', in_addr)

        for i in range(num_in):
            out_addr = addressof(c_void_p.from_buffer(audio[i]))
            self.__input_p[i] = self.__ffi.cast('FAUSTFLOAT *', out_addr)

        self.__C.computemydsp(self.__dsp, count, self.__input_p, self.__output_p)

        return output

    fs = property(fget=lambda s: s.__C.getSampleRatemydsp(s.__dsp))
    num_in = property(fget=lambda s: s.__C.getNumInputsmydsp(s.__dsp))
    num_out = property(fget=lambda s: s.__C.getNumOutputsmydsp(s.__dsp))
