import cffi
import os
from subprocess import check_call
from tempfile import NamedTemporaryFile
from string import Template
from . import python_ui, python_dsp

FAUST_PATH = ""

class FAUST(object):
    """Wraps a FAUST DSP using the CFFI.  The DSP file is compiled to C, which
    is then compiled and linked to the running Python interpreter by the CFFI.
    It exposes the compute() function of the DSP along with some other
    attributes (see below).
    """

    def __init__(self, faust_dsp, fs, faust_float="float",
                dsp_class=python_dsp.FAUSTDsp,
                ui_class=python_ui.PythonUI,
                faust_flags=[],
                **kwargs):
        """
        Initialise a FAUST object.

        Parameters:
        -----------

        faust_dsp : string
            The path to the FAUST DSP file to be wrapped.
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

        The default compiler flags are "-std=c99 -march=native -O3".  The
        reasons for this are:

        - compilation happens at run time, so -march=native should be safe,
        - FAUST programs usually profit from -O3, especially since it activates
        auto-vectorisation, and
        - since additional flags are appended to this default, you *can*
        override it in situations where it is unsuitable.
        """

        self.FAUST_PATH = FAUST_PATH
        self.FAUST_FLAGS = ["-lang", "c"] + faust_flags

        # compile the FAUST DSP to C and compile it with the CFFI
        with NamedTemporaryFile(suffix=".c") as f:
            self.__compile_faust(faust_dsp, f.name, faust_float)
            self.__ffi, self.__C = self.__gen_ffi(f.name, faust_float, **kwargs)

        # initialise the DSP object
        self.__dsp = dsp_class(self.__C, self.__ffi, faust_float, fs, ui_class)

        # add a shortcut to the compute function
        self.compute  = self.__dsp.compute

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
            int min(int x, int y) { return x < y ? x : y;};
            int max(int x, int y) { return x > y ? x : y;};

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
