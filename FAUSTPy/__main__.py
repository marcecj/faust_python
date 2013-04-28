import numpy as np
from FAUSTPy import *

#################################
# test PythonUI
#################################

class empty(object):
    pass

dattorro = FAUST("dattorro_notch_cut_regalia", 48000, "float")
ffi = dattorro.ffi
C   = dattorro.C

bla = empty()
ui = PythonUI(ffi, bla).ui
ui.openVerticalBox(ffi.NULL,"bla")

slider_val = ffi.new("FAUSTFLOAT*", 1.0)
assert slider_val[0] == 1.0
ui.addHorizontalSlider(ffi.NULL, "float", slider_val, 0.0, 0.0, 2.0, 0.1)
assert hasattr(bla.bla, "float")
assert bla.bla.float.zone == 0.0
bla.bla.float.zone = 0.5
assert bla.bla.float.zone == slider_val[0]

button_val = ffi.new("FAUSTFLOAT*", 1.0)
# should do nothing
ui.addButton(ffi.NULL, "float", button_val)

#################################
# test FAUSTDsp
#################################

dsp = FAUSTDsp(C,ffi,48000,PythonUI)

print(dsp.fs)
print(dsp.num_in)
print(dsp.num_out)
print(dir(dsp))

audio = np.zeros((2,48e3), dtype=np.float32)
audio[0][0] = 1
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
