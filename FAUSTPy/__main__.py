from FAUSTPy import *

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

print("everything passes!")
