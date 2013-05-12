import cffi
import os
from subprocess import check_call
from tempfile import NamedTemporaryFile
from string import Template
from . import python_ui, python_dsp

FAUST_PATH = ""
FAUSTFLOATS = frozenset(("float", "double", "long double"))

class FAUST(object):
    """Wraps a FAUST DSP using the CFFI.  The DSP file is compiled to C, which
    is then compiled and linked to the running Python interpreter by the CFFI.
    It exposes the compute() function of the DSP along with some other
    attributes (see below).
    """

    def __init__(self, faust_dsp, fs,
                 faust_float = "float",
                 dsp_class   = python_dsp.FAUSTDsp,
                 ui_class    = python_ui.PythonUI,
                 faust_flags = [],
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
        ui_class : PythonUI-like (optional)
            The constructor of a UIGlue wrapper.  Just in case you want to write
            your own.
        faust_flags : list of strings (optional)
            A list of additional flags to pass to the FAUST compiler, which are
            appended to "-lang c" (since FAUSTPy requires the FAUST C backend).

        You may also pass additional keyword arguments, which will get passed
        directly to cffi.FFI.verify().  This lets you override the compiler
        flags, for example.

        Notes:
        ------

        You can override the C compiler (at least on Unix-like systems) by
        overriding the ``CC`` environment variable, which you can verify by
        viewing the output of the test suite when called via setup.py, for
        example using clang::

            CC=clang python setup.py test

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

        self.FAUST_PATH = FAUST_PATH
        self.FAUST_FLAGS = ["-lang", "c"] + faust_flags

        # compile the FAUST DSP to C and compile it with the CFFI
        with NamedTemporaryFile(suffix=".dsp") as dsp_file:

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
                dsp_file.write(faust_dsp)

                # make sure the data is immediately written to disc
                dsp_file.flush()

                faust_dsp = dsp_file.name

            with NamedTemporaryFile(suffix=".c") as c_file:
                self.__compile_faust(faust_dsp, c_file.name, faust_float)
                self.__ffi, self.__C = self.__gen_ffi(c_file.name, faust_float, **kwargs)

        # initialise the DSP object
        self.__dsp = dsp_class(self.__C, self.__ffi, faust_float, fs, ui_class)

        # add shortcuts to the compute* functions
        self.compute  = self.__dsp.compute
        self.compute2 = self.__dsp.compute2

    # expose some internal attributes as properties
    # TODO: see if you can remove the ffi and C properties
    dsp = property(fget=lambda x: x.__dsp,
                   doc="The internal FAUSTDsp object.")
    ffi = property(fget=lambda x: x.__ffi,
                   doc="The internal FFI object.")
    C   = property(fget=lambda x: x.__C,
                   doc="The internal FFILibrary object.")

    def __compile_faust(self, faust_dsp, faust_c, faust_float):

        if   faust_float == "float":
            self.FAUST_FLAGS.append("-single")
        elif faust_float == "double":
            self.FAUST_FLAGS.append("-double")
        elif faust_float == "long double":
            self.FAUST_FLAGS.append("-quad")

        if self.FAUST_PATH:
            faust_cmd = os.sep.join([self.FAUST_PATH, "faust"])
        else:
            faust_cmd = "faust"

        faust_args = self.FAUST_FLAGS + ["-o", faust_c, faust_dsp]

        check_call([faust_cmd] + faust_args)

    def __gen_ffi(self, FAUSTC, faust_float, **kwargs):

        # define the ffi object
        ffi = cffi.FFI()

        c_flags = ["-std=c99", "-march=native", "-O3"]
        kwargs["extra_compile_args"] = c_flags + kwargs.get("extra_compile_args", [])

        # declare various types and functions
        #
        # These declarations need to be here -- independently of the code in the
        # ffi.verify() call below -- so that the CFFI knows the contents of the
        # data structures and the available functions.
        cdefs = "typedef {0} FAUSTFLOAT;".format(faust_float) + """

        typedef struct {
            void *mInterface;
            void (*declare)(void* interface, const char* key, const char* value);
        } MetaGlue;

        typedef struct {
            // widget layouts
            void (*openVerticalBox)(void*, const char* label);
            void (*openHorizontalBox)(void*, const char* label);
            void (*openTabBox)(void*, const char* label);
            void (*declare)(void*, FAUSTFLOAT*, char*, char*);
            // passive widgets
            void (*addNumDisplay)(void*, const char* label, FAUSTFLOAT* zone, int p);
            void (*addTextDisplay)(void*, const char* label, FAUSTFLOAT* zone, const char* names[], FAUSTFLOAT min, FAUSTFLOAT max);
            void (*addHorizontalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
            void (*addVerticalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
            // active widgets
            void (*addHorizontalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
            void (*addVerticalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
            void (*addButton)(void*, const char* label, FAUSTFLOAT* zone);
            void (*addToggleButton)(void*, const char* label, FAUSTFLOAT* zone);
            void (*addCheckButton)(void*, const char* label, FAUSTFLOAT* zone);
            void (*addNumEntry)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
            void (*closeBox)(void*);
            void* uiInterface;
        } UIGlue;

        typedef struct {...;} mydsp;

        mydsp *newmydsp();
        void deletemydsp(mydsp*);
        void metadatamydsp(MetaGlue* m);
        int getSampleRatemydsp(mydsp* dsp);
        int getNumInputsmydsp(mydsp* dsp);
        int getNumOutputsmydsp(mydsp* dsp);
        int getInputRatemydsp(mydsp* dsp, int channel);
        int getOutputRatemydsp(mydsp* dsp, int channel);
        void classInitmydsp(int samplingFreq);
        void instanceInitmydsp(mydsp* dsp, int samplingFreq);
        void initmydsp(mydsp* dsp, int samplingFreq);
        void buildUserInterfacemydsp(mydsp* dsp, UIGlue* interface);
        void computemydsp(mydsp* dsp, int count, FAUSTFLOAT** inputs, FAUSTFLOAT** outputs);
        """
        ffi.cdef(cdefs)

        # compile the code
        C = ffi.verify(
            Template("""
            #define FAUSTFLOAT ${FAUSTFLOAT}

            // helper function definitions
            FAUSTFLOAT min(FAUSTFLOAT x, FAUSTFLOAT y) { return x < y ? x : y;};
            FAUSTFLOAT max(FAUSTFLOAT x, FAUSTFLOAT y) { return x > y ? x : y;};

            // the MetaGlue struct that will be wrapped
            typedef struct {
                void *mInterface;
                void (*declare)(void* interface, const char* key, const char* value);
            } MetaGlue;

            // the UIGlue struct that will be wrapped
            typedef struct {
                // widget layouts
                void (*openVerticalBox)(void*, const char* label);
                void (*openHorizontalBox)(void*, const char* label);
                void (*openTabBox)(void*, const char* label);
                void (*declare)(void*, FAUSTFLOAT*, char*, char*);
                // passive widgets
                void (*addNumDisplay)(void*, const char* label, FAUSTFLOAT* zone, int p);
                void (*addTextDisplay)(void*, const char* label, FAUSTFLOAT* zone, const char* names[], FAUSTFLOAT min, FAUSTFLOAT max);
                void (*addHorizontalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
                void (*addVerticalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
                // active widgets
                void (*addHorizontalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
                void (*addVerticalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
                void (*addButton)(void*, const char* label, FAUSTFLOAT* zone);
                void (*addToggleButton)(void*, const char* label, FAUSTFLOAT* zone);
                void (*addCheckButton)(void*, const char* label, FAUSTFLOAT* zone);
                void (*addNumEntry)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
                void (*closeBox)(void*);
                void* uiInterface;
            } UIGlue;

            #include "${FAUSTC}"
            """).substitute(FAUSTFLOAT=faust_float, FAUSTC=FAUSTC),
            **kwargs
        )

        return ffi, C
