import numpy as np
from FAUSTPy import *

bla = python_dsp.FAUST(C,ffi,48000,faust_ui,ui)
ui.openVerticalBox(ffi.NULL,"bla")

slider_val = ffi.new("FAUSTFLOAT*", 1.0)
assert slider_val[0] == 1.0
ui.addHorizontalSlider(ffi.NULL, "float", slider_val, 0.0, 0.0, 2.0, 0.1)
assert hasattr(bla.bla, "float")
assert bla.bla.float.zone == 0.0
bla.bla.float.zone = 0.5
assert bla.bla.float.zone == slider_val[0]

print(bla.fs)
print(bla.num_in)
print(bla.num_out)
print(dir(bla))

button_val = ffi.new("FAUSTFLOAT*", 1.0)
# should do nothing
ui.addButton(ffi.NULL, "float", button_val)

audio = np.zeros((2,48e3), dtype=np.float32)
audio[0][0] = 1
out = bla.compute(audio)

print(audio)
print(out)

print("everything passes!")
