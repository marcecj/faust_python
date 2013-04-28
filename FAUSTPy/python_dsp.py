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

        output = np.ndarray(audio.shape, dtype=np.float32)
        # ctypes.c_float.from_buffer(output)
        output_p = self.__ffi.new("float*[]", audio.shape[0])
        output_p[0] = self.__ffi.cast('float *', ctypes.addressof(ctypes.c_float.from_buffer(output[0])))

        input_p  = self.__ffi.new("float*[]", audio.shape[0])
        input_p[0] = self.__ffi.cast('float *', ctypes.addressof(ctypes.c_float.from_buffer(audio[0])))

        self.__C.computemydsp(self.__dsp, count, input_p, output_p)

        return output

    fs = property(fget=lambda s: s.__C.getSampleRatemydsp(s.__dsp))
    num_in = property(fget=lambda s: s.__C.getNumInputsmydsp(s.__dsp))
    num_out = property(fget=lambda s: s.__C.getNumOutputsmydsp(s.__dsp))
