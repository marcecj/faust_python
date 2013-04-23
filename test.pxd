cdef extern from "extra_types.h":

    # helper function definitions
    cdef int min(int x, int y)
    cdef int max(int x, int y)

    ctypedef float FAUSTFLOAT

    # the MetaGlue struct that will be wrapped
    ctypedef struct MetaGlue:
        void *mInterface
        void (*declare)(void* interface, const char* key, const char* value)

    # the UIGlue struct that will be wrapped
    ctypedef struct UIGlue:
        # widget layouts
        void (*openVerticalBox)(void*, const char* label)
        void (*openHorizontalBox)(void*, const char* label)
        void (*openTabBox)(void*, const char* label)
        void (*declare)(void*, FAUSTFLOAT*, ...)
        # passive widgets
        void (*addNumDisplay)(void*, const char* label, FAUSTFLOAT* zone, int p)
        void (*addTextDisplay)(void*, const char* label, FAUSTFLOAT* zone, const char* names[], FAUSTFLOAT min, FAUSTFLOAT max)
        void (*addHorizontalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max)
        void (*addVerticalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max)
        # active widgets
        void (*addHorizontalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step)
        void (*addVerticalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step)
        void (*addButton)(void*, const char* label, FAUSTFLOAT* zone)
        void (*addToggleButton)(void*, const char* label, FAUSTFLOAT* zone)
        void (*addCheckButton)(void*, const char* label, FAUSTFLOAT* zone)
        void (*addNumEntry)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step)
        void (*closeBox)(void*)
        void* uiInterface

cdef extern from "dattorro_notch_cut_regalia.h":

    ctypedef struct mydsp:
        pass

    ctypedef struct mydsp:
        pass
    mydsp *newmydsp()
    void deletemydsp(mydsp*)
    void metadatamydsp(MetaGlue* m)
    int getSampleRatemydsp(mydsp* dsp)
    int getNumOutputsmydsp(mydsp* dsp)
    int getInputRatemydsp(mydsp* dsp, int channel)
    void classInitmydsp(int samplingFreq)
    void instanceInitmydsp(mydsp* dsp, int samplingFreq)
    void initmydsp(mydsp* dsp, int samplingFreq)
    void buildUserInterfacemydsp(mydsp* dsp, UIGlue* interface)
    void computemydsp(mydsp* dsp, int count, FAUSTFLOAT** inputs, FAUSTFLOAT** outputs)
