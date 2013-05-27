import cffi
import os
from . import python_ui, python_meta, python_dsp
from . libfaust import LibFaust

FAUSTFLOATS = frozenset(("float", "double", "long double"))

class FAUST(object):
    """Wraps a FAUST DSP using the CFFI.  The DSP file is compiled to C, which
    is then compiled and linked to the running Python interpreter by the CFFI.
    It exposes the compute() function of the DSP along with some other
    attributes (see below).
    """

    def __init__(self, faust_dsp, fs,
                 faust_float = "float",
                 faust_flags = [],
                 dsp_class   = python_dsp.PythonDSP,
                 ui_class    = python_ui.PythonUI,
                 meta_class  = python_meta.PythonMeta,
                **kwargs):
        """
        Initialise a FAUST object.

        Parameters:
        -----------

        faust_dsp : string / bytes
            This can be either the path to a FAUST DSP file (which should end in
            ".dsp") or a string of FAUST code.  Note that in Python 3 a code
            string must be of type "bytes".
        fs : int
            The sampling rate the FAUST DSP should be initialised with.
        faust_float : string (optional)
            The value of the FAUSTFLOAT type.  This is used internally by FAUST
            to generalise to different precisions. Possible values are "float",
            "double" or "long double".
        faust_flags : list of strings (optional)
            A list of additional flags to pass to the FAUST compiler, which are
            appended to "-lang c" (since FAUSTPy requires the FAUST C backend).

        And in case you want to write your own DSP/UI/Meta class (for whatever
        reason), you can override any of the following arguments:

        dsp_class : PythonDSP-like (optional)
            The constructor of a DSP wrapper.
        ui_class : PythonUI-like (optional)
            The constructor of a UIGlue wrapper.
        meta_class : PythonMeta-like (optional)
            The constructor of a MetaGlue wrapper.

        You may also pass additional keyword arguments, which will get passed
        directly to cffi.FFI.verify().  This lets you override the compiler
        flags, for example.

        Notes:
        ------

        You can override the C compiler (at least on Unix-like systems) by
        overriding the ``CC`` and ``LDSHARED`` environment variables, which you
        can verify by viewing the output of the test suite when called via
        setup.py, for example using clang::

            CC=clang LDSHARED="clang -pthreads -shared" python setup.py test

        The default compiler flags are "-std=c99 -march=native -O3".  The
        reasons for this are:

        - compilation happens at run time, so -march=native should be safe,
        - FAUST programs usually profit from -O3, especially since it activates
        auto-vectorisation, and
        - since additional flags are appended to this default, you *can*
        override it in situations where it is unsuitable.
        """

        if faust_float not in FAUSTFLOATS:
            raise ValueError("Invalid value for faust_float!")

        self.FAUST_FLAGS = faust_flags

        # Two things:
        #
        # 1.) In Python 3, in-line code *has* to be a byte array, so if
        # faust_dsp is a string the test is short-circuited and we assume
        # that it represents a file name.
        #
        # 2.) In Python 2, string literals are all byte arrays, so also
        # check whether the string ends with ".dsp", in which case we assume
        # that it represents a file name, otherwise it must be a code block.
        if type(faust_dsp) is bytes and not faust_dsp.endswith(b".dsp"):
            # if the DSP is from an inline code string we set the DSP file name
            # to something predictable so that the caching mechanism of the CFFI
            # still works, but make it somewhat unusual to reduce the likelihood
            # of a name clash; add a "." so that str.rpartition('.') returns
            # "123first_box" as the first element instead of ""
            dsp_code = faust_dsp
            dsp_fname = "123first_box."
        else:
            with open(faust_dsp, 'rb') as f:
                dsp_code = f.read()
            dsp_fname = faust_dsp

        # create a libfaust wrapper and use it to compile the FAUST code; store
        # the llvm_dsp_factory instance since it is required to delete the
        # llvm_dsp instance
        faust = LibFaust(faust_float, **kwargs)
        self.__ffi, self.__C = faust.ffi, faust.C
        factory, dsp = faust.compile_faust(dsp_code, dsp_fname)

        # initialise the DSP object
        self.__dsp = dsp_class(self.__C, self.__ffi, factory, dsp, fs)

        # set up the UI
        if ui_class:
            UI = ui_class(self.__ffi, dsp_fname, self.__dsp)
            self.__C.buildUserInterfaceCDSPInstance(self.__dsp.dsp, UI.ui)

        # get the meta-data of the DSP
        if meta_class:
            Meta = meta_class(self.__ffi, self.__dsp)
            self.__C.metadataCDSPFactory(factory, Meta.meta)

        # add shortcuts to the compute* functions
        self.compute  = self.__dsp.compute
        self.compute2 = self.__dsp.compute2

    # expose some internal attributes as properties
    dsp = property(fget=lambda x: x.__dsp,
                   doc="The internal PythonDSP object.")
