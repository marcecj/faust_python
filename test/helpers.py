import cffi
from tempfile import NamedTemporaryFile
from string import Template
from subprocess import check_call

def init_ffi():
    ffi = cffi.FFI()

    faust_dsp = "dattorro_notch_cut_regalia.dsp"

    # just use single precision for tests
    faust_float = "float"

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

        faust_args = ["-lang", "c", "-single", "-o", f.name, faust_dsp]

        check_call(["faust"] + faust_args)

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
            """).substitute(FAUSTFLOAT=faust_float, FAUSTC=f.name),
            extra_compile_args=["-std=c99"],
        )

        return ffi, C, faust_float
