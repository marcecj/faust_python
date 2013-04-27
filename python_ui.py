import cffi
import wrapper

# TODO: test the MetaGlue and UIGlue types

ffi = wrapper.ffi

class param(object):

    def __init__(self, zone, init, min, max, step):
        self.min = min
        self.max = max
        self.step = step
        # _zone is a CData holding a float*
        self._zone = zone
        self._zone[0] = init
        self.__doc__ = "min={0}, max={1}, step={2}".format(min,max,step)

    def getter(self):
        return self._zone[0]

    def setter(self, x):
        if   x >= self.max:
            self._zone[0] = self.max
        elif x <= self.min:
            self._zone[0] = self.min
        else:
            self._zone[0] = self.min + round((x-self.min)/self.step)*self.step

    zone = property(fget=getter, fset=setter)


class PythonUI(object):

    def __init__(self, obj=None):
        if obj:
            self.__boxes = [obj]
        else:
            self.__boxes = [self]

    def declare(self, key, value):
        pass

    ##########################
    # stuff to do with boxes
    ##########################

    def openBox(self, label):
        if label:
            class namespace(object):
                pass

            # create a new sub-namespace and set it's parent to the current
            # namespace
            box = namespace()

            setattr(self.__boxes[-1], label, box)
            self.__boxes.append(box)

    def openVerticalBox(self, label):

        self.openBox(label)

    def openHorizontalBox(self, label):

        self.openBox(label)

    def openTabBox(self, label):

        self.openBox(label)

    def closeBox(self):

        if len(self.__boxes) > 1:
            self.__boxes.pop()
        else:
            print("Warning: Trying to close last box.")

    ##########################
    # stuff to do with inputs
    ##########################

    def add_input(self, label, zone, init, min, max, step):

        setattr(self.__boxes[-1], label, param(zone, init, min, max, step))

    def addHorizontalSlider(self, label, zone, init, min, max, step):

        self.add_input(label, zone, init, min, max, step)

    def addVerticalSlider(self, label, zone, init, min, max, step):

        self.add_input(label, zone, init, min, max, step)

    def addNumEntry(self, label, zone, init, min, max, step):

        self.add_input(label, zone, init, min, max, step)

    def addButton(self, label, zone):

        self.add_input(label, zone, 0, 0, 1, 1)

    def addToggleButton(self, label, zone):

        self.add_input(label, zone, 0, 0, 1, 1)

    def addCheckButton(self, label, zone):

        self.add_input(label, zone, 0, 0, 1, 1)

class empty(object):
    pass

# create a PythonUI object that adds namespaces and attributes to an empty object
# TODO: replace empty() with the actual FAUST DSP wrapper
bla = empty()
faust_ui = PythonUI(bla)

# define wrapper functions that know the global PythonUI object
# TODO: implement the dummy functions
def declare(key, value):
    faust_ui.declare(key, value)
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
def addNumDisplay(ignore, label, zone, p):
    pass
def addTextDisplay(ignore, label, zone, names, min, max):
    pass
def addHorizontalBargraph(ignore, label, zone, min, max):
    pass
def addVerticalBargraph(ignore, label, zone, min, max):
    pass

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

if __name__ == '__main__':

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
