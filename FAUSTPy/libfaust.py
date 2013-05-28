from string import Template
import cffi

class LibFaust(object):

    def __init__(self, faust_float, **kwargs):

        # define the ffi object
        ffi = cffi.FFI()

        # c_flags = ["-std=c99", "-march=native", "-O3"]
        c_flags = ["-std=c99", "-march=native", "-O0", "-g"]
        kwargs["extra_compile_args"] = c_flags + \
                kwargs.get("extra_compile_args", [])

        kwargs["extra_link_args"] = ["-Wl,-rpath,/usr/lib/faust"] + \
                kwargs.get("extra_link_args", [])

        kwargs["library_dirs"]    = ["/usr/lib/faust"] + \
                kwargs.get("library_dirs", [])

        kwargs["libraries"]       = ["faust"] + kwargs.get("libraries", [])

        # declare various types and functions
        #
        # These declarations need to be here -- independently of the code in the
        # ffi.verify() call below -- so that the CFFI knows the contents of the
        # data structures and the available functions.
        ffi.cdef(
"typedef {0} FAUSTFLOAT;".format(faust_float) + """

typedef struct {
    void *mInterface;
    void (*declare)(void* interface, const char* key, const char* value);
} MetaGlue;

typedef struct {
    void* uiInterface;
    // widget layouts
    void (*openTabBox)(void*, const char* label);
    void (*openHorizontalBox)(void*, const char* label);
    void (*openVerticalBox)(void*, const char* label);
    void (*closeBox)(void*);
    // active widgets
    void (*addButton)(void*, const char* label, FAUSTFLOAT* zone);
    void (*addCheckButton)(void*, const char* label, FAUSTFLOAT* zone);
    void (*addVerticalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
    void (*addHorizontalSlider)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
    void (*addNumEntry)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
    // passive widgets
    void (*addHorizontalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
    void (*addVerticalBargraph)(void*, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
    void (*declare)(void*, FAUSTFLOAT*, char*, char*);
} UIGlue;

typedef ... llvm_dsp;
typedef ... llvm_dsp_factory;
typedef ... llvm_dsp_imp;

llvm_dsp_factory* createCDSPFactory(int argc, const char *argv[],
                        const char* library_path,
                        const char* draw_path,
                        const char* name,
                        const char* input,
                        const char* target,
                        char* error_msg,
                        int opt_level);

void deleteCDSPFactory(llvm_dsp_factory* factory);

llvm_dsp* createCDSPInstance(llvm_dsp_factory* factory);
void deleteCDSPInstance(llvm_dsp* dsp);

void metadataCDSPFactory(llvm_dsp_factory* factory, MetaGlue* meta);

int getNumInputsCDSPInstance(llvm_dsp* dsp);
int getNumOutputsCDSPInstance(llvm_dsp* dsp);
void instanceInitCDSPInstance(llvm_dsp* dsp, int samplingFreq);
void initCDSPInstance(llvm_dsp* dsp, int samplingFreq);
void buildUserInterfaceCDSPInstance(llvm_dsp* dsp, UIGlue* interface);
void computeCDSPInstance(llvm_dsp* dsp, int count, FAUSTFLOAT** input, FAUSTFLOAT** output);
        """
        )

        # compile the code
        C = ffi.verify(
            Template("""
#define FAUSTFLOAT ${FAUSTFLOAT}

typedef struct {} llvm_dsp_factory;
typedef struct {} llvm_dsp;
typedef struct {} llvm_dsp_imp;

#include <faust/gui/CUI.h>
#include <faust/llvm-c-dsp.h>
            """).substitute(FAUSTFLOAT=faust_float),
            **kwargs
        )

        self.__faust_float = faust_float
        self.__ffi = ffi
        self.__C   = C

    def compile_faust(self, dsp_code, dsp_fname, opt_level=3,
                      *kargs):

        args = list(kargs)
        if   self.__faust_float == "float":
            args.append("-single")
        elif self.__faust_float == "double":
            args.append("-double")
        elif self.__faust_float == "long double":
            args.append("-quad")

        err = self.__ffi.new("char[256]", b"")

        faust_args = []
        for arg in kargs:

            if type(arg) == str:
                arg = arg.encode("utf-8")

            faust_args.append(self.__ffi.new("char[]", arg))

        if type(dsp_fname) == str:
            dsp_fname = dsp_fname.encode("utf-8")

        factory = self.__C.createCDSPFactory(
            len(faust_args), faust_args,
            b"",
            self.__ffi.new("char[]", b""),
            dsp_fname,
            dsp_code,
            b"",
            err,
            opt_level
        )

        if factory == self.__ffi.NULL:
            raise Exception("factory == NULL")

        dsp = self.__C.createCDSPInstance(factory)

        if dsp == self.__ffi.NULL:
            self.__C.deleteCDSPFactory(factory)
            raise Exception("dsp == NULL")

        return factory, dsp

    ffi = property(fget=lambda x: x.__ffi)
    C   = property(fget=lambda x: x.__C)
