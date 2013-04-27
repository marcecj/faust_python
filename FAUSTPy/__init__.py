from . wrapper import ffi, C
from . import python_ui

class empty(object):
    pass

# create a PythonUI object that adds namespaces and attributes to an empty object
# TODO: replace empty() with the actual FAUST DSP wrapper
bla = empty()
faust_ui = python_ui.PythonUI(bla)

# define wrapper functions that know the global PythonUI object
# TODO: implement the dummy functions
def declare(mInterface, zone, key, value):
    faust_ui.declare(zone, key, value)
def openVerticalBox(mInterface, label):
    faust_ui.openVerticalBox(ffi.string(label))
def openHorizontalBox(mInterface, label):
    faust_ui.openHorizontalBox(ffi.string(label))
def openTabBox(mInterface, label):
    faust_ui.openTabBox(ffi.string(label))
def closeBox(mInterface):
    faust_ui.closeBox()
def addHorizontalSlider(ignore, c_label, zone, init, min, max, step):
    label = ffi.string(c_label)
    faust_ui.addHorizontalSlider(label, zone, init, min, max, step)
def addVerticalSlider(ignore, c_label, zone, init, min, max, step):
    label = ffi.string(c_label)
    faust_ui.addVerticalSlider(label, zone, init, min, max, step)
def addNumEntry(ignore, c_label, zone, init, min, max, step):
    label = ffi.string(c_label)
    faust_ui.addNumEntry(label, zone, init, min, max, step)
def addButton(ignore, c_label, zone):
    label = ffi.string(c_label)
    faust_ui.addButton(label, zone)
def addToggleButton(ignore, c_label, zone):
    label = ffi.string(c_label)
    faust_ui.addToggleButton(c_label, zone)
def addCheckButton(ignore, c_label, zone):
    label = ffi.string(c_label)
    faust_ui.addCheckButton(label, zone)
def addNumDisplay(ignore, c_label, zone, p):
    label = ffi.string(c_label)
    faust_ui.addNumDisplay(label, zone, p)
def addTextDisplay(ignore, c_label, zone, names, min, max):
    label = ffi.string(c_label)
    faust_ui.addTextDisplay(label, zone, names, min, max)
def addHorizontalBargraph(ignore, c_label, zone, min, max):
    label = ffi.string(c_label)
    faust_ui.addHorizontalBargraph(label, zone, min, max)
def addVerticalBargraph(ignore, c_label, zone, min, max):
    label = ffi.string(c_label)
    faust_ui.addVerticalBargraph(label, zone, min, max)

# define C callbacks that call the above Python functions
declare_c           = ffi.callback("void(void*, FAUSTFLOAT*, char*, char*)", declare)
openVerticalBox_c   = ffi.callback("void(void*, char*)", openVerticalBox)
openHorizontalBox_c = ffi.callback("void(void*, char*)", openHorizontalBox)
openTabBox_c        = ffi.callback("void(void*, char*)", openTabBox)
closeBox_c          = ffi.callback("void(void*)", closeBox)
addHorizontalSlider_c = ffi.callback(
    "void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT)",
    addHorizontalSlider
)
addVerticalSlider_c = ffi.callback(
    "void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT)",
    addVerticalSlider
)
addNumEntry_c = ffi.callback(
    "void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT)",
    addNumEntry
)
addButton_c       = ffi.callback("void(void*, char*, FAUSTFLOAT*)", addButton)
addToggleButton_c = ffi.callback("void(void*, char*, FAUSTFLOAT*)", addToggleButton)
addCheckButton_c  = ffi.callback("void(void*, char*, FAUSTFLOAT*)", addCheckButton)
addNumDisplay_c   = ffi.callback("void(void*, char*, FAUSTFLOAT*, int)", addNumDisplay)
addTextDisplay_c  = ffi.callback("void(void*, char*, FAUSTFLOAT*, char*[], FAUSTFLOAT, FAUSTFLOAT)", addTextDisplay)
addHorizontalBargraph_c = ffi.callback("void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT)", addHorizontalBargraph)
addVerticalBargraph_c = ffi.callback("void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT)", addVerticalBargraph)

# create a UI object and store the above callbacks as it's function pointers
ui = ffi.new("UIGlue*")
ui.declare               = declare_c
ui.openVerticalBox       = openVerticalBox_c
ui.openHorizontalBox     = openHorizontalBox_c
ui.openTabBox            = openTabBox_c
ui.closeBox              = closeBox_c
ui.addHorizontalSlider   = addHorizontalSlider_c
ui.addVerticalSlider     = addVerticalSlider_c
ui.addNumEntry           = addNumEntry_c
ui.addButton             = addButton_c
ui.addToggleButton       = addToggleButton_c
ui.addCheckButton        = addCheckButton_c
ui.addNumDisplay         = addNumDisplay_c
ui.addTextDisplay        = addTextDisplay_c
ui.addHorizontalBargraph = addHorizontalBargraph_c
ui.addVerticalBargraph   = addVerticalBargraph_c
# we don't use this anyway
ui.uiInterface           = ffi.NULL
