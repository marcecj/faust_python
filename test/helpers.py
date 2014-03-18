from FAUSTPy.libfaust import LibFaust


class empty(object):
    pass


def init_ffi(faust_dsp="dattorro_notch_cut_regalia.dsp",
             faust_float="float"):

    if type(faust_dsp) is bytes and not faust_dsp.endswith(b".dsp"):
        dsp_code = faust_dsp
        dsp_fname = "123first_box."
    else:
        with open(faust_dsp, 'rb') as f:
            dsp_code = f.read()
        dsp_fname = faust_dsp

    faust = LibFaust(faust_float)
    factory, dsp = faust.compile_faust(dsp_code, dsp_fname)

    return faust.ffi, faust.C, factory, dsp
