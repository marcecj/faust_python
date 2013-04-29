# TODO: test the MetaGlue and UIGlue types
# TODO: store meta-data about the UI type in the param class to enable users of
# PythonUI to know the type of the UI elements

class param(object):

    def __init__(self, zone, init, min, max, step):
        self.min = min
        self.max = max
        self.step = step
        # _zone is a CData holding a float*
        self._zone = zone
        self._zone[0] = init
        self.__doc__ = "min={0}, max={1}, step={2}".format(min,max,step)

    def __get__(self, obj, type=None):

        return self

    def __set__(self, obj, value):

        self.zone = value

    def __delete__(self, obj):

        print("Please do not delete this.")

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

    def __init__(self, ffi, obj=None):
        if obj:
            self.__boxes = [obj]
        else:
            self.__boxes = [self]

        # define wrapper functions that know the global PythonUI object
        # TODO: implement the dummy functions
        def declare(mInterface, zone, key, value):
            self.declare(zone, key, value)
        def openVerticalBox(mInterface, label):
            self.openVerticalBox(ffi.string(label))
        def openHorizontalBox(mInterface, label):
            self.openHorizontalBox(ffi.string(label))
        def openTabBox(mInterface, label):
            self.openTabBox(ffi.string(label))
        def closeBox(mInterface):
            self.closeBox()
        def addHorizontalSlider(ignore, c_label, zone, init, min, max, step):
            label = ffi.string(c_label)
            self.addHorizontalSlider(label, zone, init, min, max, step)
        def addVerticalSlider(ignore, c_label, zone, init, min, max, step):
            label = ffi.string(c_label)
            self.addVerticalSlider(label, zone, init, min, max, step)
        def addNumEntry(ignore, c_label, zone, init, min, max, step):
            label = ffi.string(c_label)
            self.addNumEntry(label, zone, init, min, max, step)
        def addButton(ignore, c_label, zone):
            label = ffi.string(c_label)
            self.addButton(label, zone)
        def addToggleButton(ignore, c_label, zone):
            label = ffi.string(c_label)
            self.addToggleButton(c_label, zone)
        def addCheckButton(ignore, c_label, zone):
            label = ffi.string(c_label)
            self.addCheckButton(label, zone)
        def addNumDisplay(ignore, c_label, zone, p):
            label = ffi.string(c_label)
            self.addNumDisplay(label, zone, p)
        def addTextDisplay(ignore, c_label, zone, names, min, max):
            label = ffi.string(c_label)
            self.addTextDisplay(label, zone, names, min, max)
        def addHorizontalBargraph(ignore, c_label, zone, min, max):
            label = ffi.string(c_label)
            self.addHorizontalBargraph(label, zone, min, max)
        def addVerticalBargraph(ignore, c_label, zone, min, max):
            label = ffi.string(c_label)
            self.addVerticalBargraph(label, zone, min, max)

        # define C callbacks that call the above Python functions
        self.__declare_c           = ffi.callback("void(void*, FAUSTFLOAT*, char*, char*)", declare)
        self.__openVerticalBox_c   = ffi.callback("void(void*, char*)", openVerticalBox)
        self.__openHorizontalBox_c = ffi.callback("void(void*, char*)", openHorizontalBox)
        self.__openTabBox_c        = ffi.callback("void(void*, char*)", openTabBox)
        self.__closeBox_c          = ffi.callback("void(void*)", closeBox)
        self.__addHorizontalSlider_c = ffi.callback(
            "void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT)",
            addHorizontalSlider
        )
        self.__addVerticalSlider_c = ffi.callback(
            "void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT)",
            addVerticalSlider
        )
        self.__addNumEntry_c = ffi.callback(
            "void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT, FAUSTFLOAT)",
            addNumEntry
        )
        self.__addButton_c       = ffi.callback("void(void*, char*, FAUSTFLOAT*)", addButton)
        self.__addToggleButton_c = ffi.callback("void(void*, char*, FAUSTFLOAT*)", addToggleButton)
        self.__addCheckButton_c  = ffi.callback("void(void*, char*, FAUSTFLOAT*)", addCheckButton)
        self.__addNumDisplay_c   = ffi.callback("void(void*, char*, FAUSTFLOAT*, int)", addNumDisplay)
        self.__addTextDisplay_c  = ffi.callback("void(void*, char*, FAUSTFLOAT*, char*[], FAUSTFLOAT, FAUSTFLOAT)", addTextDisplay)
        self.__addHorizontalBargraph_c = ffi.callback("void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT)", addHorizontalBargraph)
        self.__addVerticalBargraph_c = ffi.callback("void(void*, char*, FAUSTFLOAT*, FAUSTFLOAT, FAUSTFLOAT)", addVerticalBargraph)

        # create a UI object and store the above callbacks as it's function pointers
        ui = ffi.new("UIGlue*")
        ui.declare               = self.__declare_c
        ui.openVerticalBox       = self.__openVerticalBox_c
        ui.openHorizontalBox     = self.__openHorizontalBox_c
        ui.openTabBox            = self.__openTabBox_c
        ui.closeBox              = self.__closeBox_c
        ui.addHorizontalSlider   = self.__addHorizontalSlider_c
        ui.addVerticalSlider     = self.__addVerticalSlider_c
        ui.addNumEntry           = self.__addNumEntry_c
        ui.addButton             = self.__addButton_c
        ui.addToggleButton       = self.__addToggleButton_c
        ui.addCheckButton        = self.__addCheckButton_c
        ui.addNumDisplay         = self.__addNumDisplay_c
        ui.addTextDisplay        = self.__addTextDisplay_c
        ui.addHorizontalBargraph = self.__addHorizontalBargraph_c
        ui.addVerticalBargraph   = self.__addVerticalBargraph_c
        # we don't use this anyway
        ui.uiInterface           = ffi.NULL

        self.__ui = ui

    ui = property(fget=lambda x: x.__ui)

    def declare(self, zone, key, value):
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

            sane_label = label.replace(" ", "_").replace(".", "_")
            setattr(self.__boxes[-1], sane_label, box)
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

        sane_label = label.replace(" ","_").replace(".","_")
        setattr(self.__boxes[-1].__class__, sane_label, param(zone, init, min, max, step))

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

    def addNumDisplay(self, label, zone, p):
        pass

    def addTextDisplay(self, label, zone, names, min, max):
        pass

    def addHorizontalBargraph(self, label, zone, min, max):
        pass

    def addVerticalBargraph(self, label, zone, min, max):
        pass
