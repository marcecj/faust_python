import argparse
import numpy as np
from FAUSTPy import *

# set up command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--faustfloat',
                    dest="faustfloat",
                    default="float",
                    help="The value of FAUSTFLOAT.")
parser.add_argument('-p', '--path',
                    dest="faust_path",
                    default="",
                    help="The path of FAUSTFLOAT.")
parser.add_argument('-c', '--cflags',
                    dest="cflags",
                    default=[],
                    type=str.split,
                    help="Extra compiler flags")
args = parser.parse_args()

wrapper.FAUST_PATH = args.faust_path

#################################
# test PythonUI
#################################

class empty(object):
    pass

dattorro = FAUST("dattorro_notch_cut_regalia.dsp", 48000, args.faustfloat,
                 extra_compile_args=args.cflags)
ffi = dattorro.ffi
C   = dattorro.C

bla = empty()
ui = PythonUI(ffi, bla).ui
ui.openVerticalBox(ffi.NULL,"bla")

slider_val = ffi.new("FAUSTFLOAT*", 1.0)
assert float(slider_val[0]) == 1.0
ui.addHorizontalSlider(ffi.NULL, "float", slider_val, 0.0, 0.0, 2.0, 0.1)
assert hasattr(bla.bla, "float")
assert float(bla.bla.float.zone) == 0.0
bla.bla.float.zone = 0.5
assert float(bla.bla.float.zone) == float(slider_val[0])

button_val = ffi.new("FAUSTFLOAT*", 1.0)
# should do nothing
ui.addButton(ffi.NULL, "float", button_val)

#################################
# test FAUSTDsp
#################################

dsp = FAUSTDsp(C,ffi,args.faustfloat,48000,PythonUI)

print(dsp.fs)
print(dsp.num_in)
print(dsp.num_out)
print(dir(dsp))

audio = np.zeros((dattorro.dsp.num_in,48e3), dtype=dattorro.dsp.dtype)
audio[:,0] = 1
out = dsp.compute(audio)

print(audio)
print(out)

#################################
# test FAUST
#################################

out2 = dattorro.compute(audio)

print(audio)
print(out2)

#################################
# THE END
#################################

print("everything passes!")
