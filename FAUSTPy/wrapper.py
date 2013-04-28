import cffi
from string import Template
from . import python_ui, python_dsp

class FAUST(object):

    def __init__(self, fs, faust_float, faust_dsp):

        self.__ffi, self.__C = self.__gen_ffi(faust_float, faust_dsp)

        self.__dsp = python_dsp.FAUSTDsp(self.__C,self.__ffi,fs,python_ui.PythonUI)

    def compute(self, audio):

        return self.__dsp.compute(audio)

    dsp = property(fget=lambda x: x.__dsp)
    ffi = property(fget=lambda x: x.__ffi)
    C   = property(fget=lambda x: x.__C)

    def __gen_ffi(self, FAUSTFLOAT, FAUSTDSP):

        # define the ffi object
        ffi = cffi.FFI()

        # declare various types and functions
        cdefs = "typedef {0} FAUSTFLOAT;".format(FAUSTFLOAT) + """

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

            #include "${FAUSTDSP}.h"
            """).substitute(FAUSTFLOAT=FAUSTFLOAT, FAUSTDSP=FAUSTDSP),
            libraries=[],
            include_dirs=["."],
            extra_compile_args=["-std=c99"],
        )

        return ffi, C
