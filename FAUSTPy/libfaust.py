from string import Template
from subprocess import check_output

import cffi


# TODO: think of a way to cache existing libfaust wrappers, because creating a
# new, identical instance will invalidate the old one.  Doing this will give a
# warning, like so:
#
#  /usr/lib64/python3.3/site-packages/cffi/vengine_cpy.py:166: UserWarning:
#      reimporting '_cffi__x8d5b106dx146bdea1' might overwrite older
#      definitions
#    % (self.verifier.get_module_name()))
#
# One solution might be to pre-compile one instance for each possible
# FAUSTFLOAT, then reference those instances in wrapper.py.
class LibFaust(object):

    def __init__(self, faust_float, **kwargs):

        # define the ffi object
        ffi = cffi.FFI()

        llvm_syslibs = check_output('llvm-config --system-libs'.split()) \
            .decode().split()

        # c_flags = ["-std=c99", "-march=native", "-O3"]
        c_flags = ["-std=c99", "-march=native", "-O0", "-g"]
        kwargs["extra_compile_args"] = c_flags + \
            kwargs.get("extra_compile_args", [])

        kwargs["extra_link_args"] = ["-Wl,-rpath,/usr/lib/faust"] + \
            llvm_syslibs + \
            kwargs.get("extra_link_args", [])

        kwargs["library_dirs"] = ["/usr/lib/faust"] + \
            kwargs.get("library_dirs", [])

        kwargs["libraries"] = ["faust"] + kwargs.get("libraries", [])

        # declare various types and functions
        #
        # These declarations need to be here -- independently of the code in
        # the ffi.verify() call below -- so that the CFFI knows the contents of
        # the data structures and the available functions.
        ffi.cdef(
"typedef {0} FAUSTFLOAT;".format(faust_float) + """

/*******************************************************************************
 * CUI : Faust User Interface for C or LLVM generated code.
 ******************************************************************************/

/* -- layout groups */

typedef void (* openTabBoxFun) (void* interface, const char* label);
typedef void (* openHorizontalBoxFun) (void* interface, const char* label);
typedef void (* openVerticalBoxFun) (void* interface, const char* label);
typedef void (*closeBoxFun) (void* interface);

/* -- active widgets */

typedef void (* addButtonFun) (void* interface, const char* label, FAUSTFLOAT* zone);
typedef void (* addCheckButtonFun) (void* interface, const char* label, FAUSTFLOAT* zone);
typedef void (* addVerticalSliderFun) (void* interface, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
typedef void (* addHorizontalSliderFun) (void* interface, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);
typedef void (* addNumEntryFun) (void* interface, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT init, FAUSTFLOAT min, FAUSTFLOAT max, FAUSTFLOAT step);

/* -- passive display widgets */

typedef void (* addHorizontalBargraphFun) (void* interface, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);
typedef void (* addVerticalBargraphFun) (void* interface, const char* label, FAUSTFLOAT* zone, FAUSTFLOAT min, FAUSTFLOAT max);

typedef void (* declareFun) (void* interface, FAUSTFLOAT* zone, const char* key, const char* value);

typedef struct {
    void* uiInterface;
    openTabBoxFun openTabBox;
    openHorizontalBoxFun openHorizontalBox;
    openVerticalBoxFun openVerticalBox;
    closeBoxFun closeBox;
    addButtonFun addButton;
    addCheckButtonFun addCheckButton;
    addVerticalSliderFun addVerticalSlider;
    addHorizontalSliderFun addHorizontalSlider;
    addNumEntryFun addNumEntry;
    addHorizontalBargraphFun addHorizontalBargraph;
    addVerticalBargraphFun addVerticalBargraph;
    declareFun declare;
} UIGlue;

typedef void (* metaDeclareFun) (void* interface, const char* key, const char* value);
typedef struct {
    void* mInterface;
    metaDeclareFun declare;
} MetaGlue;

typedef ... llvm_dsp;
typedef ... llvm_dsp_factory;
typedef ... llvm_dsp_imp;


llvm_dsp_factory* createCDSPFactoryFromString(const char* name_app,
                        const char* dsp_content,
                        int argc, const char* argv[],
                        const char* target,
                        char* error_msg,
                        int opt_level);

void deleteCDSPFactory(llvm_dsp_factory* factory);

llvm_dsp* createCDSPInstance(llvm_dsp_factory* factory);
void deleteCDSPInstance(llvm_dsp* dsp);

void metadataCDSPFactory(llvm_dsp_factory* factory, MetaGlue* meta);

int getNumInputsCDSPInstance(llvm_dsp* dsp);
int getNumOutputsCDSPInstance(llvm_dsp* dsp);
void initCDSPInstance(llvm_dsp* dsp, int samplingFreq);
void buildUserInterfaceCDSPInstance(llvm_dsp* dsp, UIGlue* interface);
void computeCDSPInstance(llvm_dsp* dsp, int count, FAUSTFLOAT** input, FAUSTFLOAT** output);
        """
        )

        # compile the code
        C = ffi.verify(
            Template("""
#define FAUSTFLOAT ${FAUSTFLOAT}
#include <faust/gui/CUI.h>
#include <faust/llvm-c-dsp.h>
            """).substitute(FAUSTFLOAT=faust_float),
            **kwargs
        )

        self.__faust_float = faust_float
        self.__ffi = ffi
        self.__C = C

    def compile_faust(self, dsp_code, dsp_fname, opt_level=3, *kargs):

        args = list(kargs)
        if self.__faust_float == "float":
            args.append("-single")
        elif self.__faust_float == "double":
            args.append("-double")
        elif self.__faust_float == "long double":
            args.append("-quad")

        err = self.__ffi.new("char[256]", b"")

        faust_args = []
        for arg in args:

            if type(arg) == str:
                arg = arg.encode("utf-8")

            faust_args.append(self.__ffi.new("char[]", arg))

        if type(dsp_fname) == str:
            dsp_fname = dsp_fname.encode("utf-8")

        factory = self.__C.createCDSPFactoryFromString(
            dsp_fname,
            dsp_code,
            len(faust_args), faust_args,
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
    C = property(fget=lambda x: x.__C)
