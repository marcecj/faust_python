import cffi
from tempfile import NamedTemporaryFile
from string import Template
from subprocess import check_call

class empty(object):
    pass

def init_ffi(faust_dsp="dattorro_notch_cut_regalia.dsp",
             faust_float="float"):

    ffi = cffi.FFI()

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

    with NamedTemporaryFile(suffix=".c") as f:

        faust_args = ["-lang", "c", "-o", f.name, faust_dsp]

        if faust_float == "float":
            faust_args = ["-single"] + faust_args
        elif faust_float == "double":
            faust_args = ["-double"] + faust_args
        elif faust_float == "long double":
            faust_args = ["-quad"] + faust_args

        check_call(["faust"] + faust_args)

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
            """).substitute(FAUSTFLOAT=faust_float, FAUSTC=f.name),
            extra_compile_args=["-std=c99"],
        )

        return ffi, C
