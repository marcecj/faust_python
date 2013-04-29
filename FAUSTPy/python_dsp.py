import numpy as np
import ctypes

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

    def __del__(self):

        self.__C.deletemydsp(self.__dsp)

    def compute(self, audio):

        audio = np.atleast_2d(audio)

        count = audio.shape[1]
        num_chan = audio.shape[0]

        output = np.ndarray(audio.shape, dtype=audio.dtype)
        output_p = self.__ffi.new("FAUSTFLOAT*[]", num_chan)
        for i in range(num_chan):
            in_addr = ctypes.addressof(ctypes.c_float.from_buffer(output[i]))
            output_p[i] = self.__ffi.cast('FAUSTFLOAT *', in_addr)

        input_p  = self.__ffi.new("FAUSTFLOAT*[]", num_chan)
        for i in range(num_chan):
            out_addr = ctypes.addressof(ctypes.c_float.from_buffer(audio[i]))
            input_p[i] = self.__ffi.cast('FAUSTFLOAT *', out_addr)

        self.__C.computemydsp(self.__dsp, count, input_p, output_p)

        return output

    fs = property(fget=lambda s: s.__C.getSampleRatemydsp(s.__dsp))
    num_in = property(fget=lambda s: s.__C.getNumInputsmydsp(s.__dsp))
    num_out = property(fget=lambda s: s.__C.getNumOutputsmydsp(s.__dsp))
