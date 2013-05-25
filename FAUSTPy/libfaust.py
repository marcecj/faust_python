import cffi

ffi = cffi.FFI()

ffi.cdef("""
int compile_faust(
         int argc,
         const char* argv[],
         const char* library_path,
         const char* draw_path,
         const char* name,
         const char* input,
         char* error_msg);
""")

C = ffi.verify(
    extra_link_args=["-Wl,-rpath,/usr/lib/faust"],
    library_dirs=["/usr/lib/faust"],
    libraries=["faust"]
)

def compile_faust(dsp_code, dsp_fname, faust_c="", *kargs):

    err = ffi.new("char[256]", b"")

    faust_args = [ffi.new("char[]", b"faust")]

    for arg in kargs:

        if type(arg) == str:
            arg = arg.encode("utf-8")

        faust_args.append(ffi.new("char[]", arg))

    if faust_c:

        if type(faust_c) == str:
            faust_c = faust_c.encode("utf-8")

        faust_args.extend([
            ffi.new("char[]", b"-o"),
            ffi.new("char[]", faust_c),
        ])

    if type(dsp_fname) == str:
        dsp_fname = dsp_fname.encode("utf-8")

    ret = C.compile_faust(
        len(faust_args), faust_args,
        ffi.NULL,
        ffi.new("char[]", b""),
        dsp_fname,
        dsp_code,
        err
    )

    err_str = ffi.string(err)
    if ret != 0 or err_str:
        raise Exception("FAUST error: " + err_str)
