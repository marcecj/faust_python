# TODO: store meta-data about the UI type in the param class to enable users of
# PythonUI to know the type of the UI elements

# a string consisting of characters that are valid identifiers in both
# Python 2 and Python 3
import string
valid_ident = string.ascii_letters + string.digits + "_"

def str_to_identifier(s):
    """Convert a "bytes" to a valid (in Python 2 and 3) identifier."""

    # convert to unicode string
    s = s.decode()

    def filter_chars(s):
        for c in s:
            # periods are used for abbreviations and look ugly when converted to
            # underscore, so filter them out completely
            if   c == ".":
                yield ""
            elif c in valid_ident or c == "_":
                yield c
            else:
                yield "_"

    if s[0] in string.digits:
        s = "_"+s

    return ''.join(filter_chars(s))

class param(object):
    """A UI parameter object.

    This objects represents a FAUST UI input.  It makes sure to enforce the
    constraints specified by the minimum, maximum and step size.

    This object implements the descriptor protocol: reading it works just like
    normal objects, but assignment is redirects to its "zone" attribute.
    Furthermore, it cannot be deleted.
    """

    def __init__(self, label, zone, init, min, max, step):
        """Initialise a param object.

        Parameters:
        -----------

        zone : cffi.CData
            Points to the FAUSTFLOAT object inside the DSP C object.
        init : float
            The initialisation value.
        min : float
            The minimum allowed value.
        max : float
            The maximum allowed value.
        step : float
            The step size of the parameter.
        """

        # NOTE: _zone is a CData holding a float*
        self.label    = label
        self.min      = min
        self.max      = max
        self.step     = step
        self._zone    = zone
        self._zone[0] = init
        self.default  = init
        self.__doc__  = "min={0}, max={1}, step={2}".format(min,max,step)

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

    zone = property(fget=getter, fset=setter,
                    doc="Pointer to the value of the parameter.")

class namespace(object):
    def __init__(self, label):
        self.label = label

class PythonUI(object):
    """
    Maps the UI elements of a FAUST DSP to attributes of another object,
    specifically a FAUST wrapper object.

    In FAUST, UI's are specified by the DSP object, which calls methods of a UI
    object to create them.  The PythonUI class implements such a UI object.  It
    creates C callbacks to its methods and stores then in a UI struct, which can
    then be passed to the buildUserInterface() function of a FAUST DSP object.

    The DSP object basically calls the methods of the PythonUI class from C via
    the callbacks in the UI struct and thus creates a hierarchical namespace of
    attributes which map back to the DSP's UI elements.

    See also:
    ---------

    FAUSTPy.param - wraps the UI input parameters.
    """

    def __init__(self, ffi, obj=None):
        """
        Initialise a PythonUI object.

        Parameters:
        -----------

        ffi : cffi.FFI
            The CFFI instance that holds all the data type declarations.
        obj : object (optional)
            The Python object to which the UI elements are to be added.  If None
            (the default) the PythonUI instance manipulates itself.
        """

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
        ui.uiInterface           = ffi.NULL # we don't use this anyway

        self.__ui = ui

    ui = property(fget=lambda x: x.__ui,
                  doc="The UI struct that calls back to its parent object.")

    def declare(self, zone, key, value):
        pass

    ##########################
    # stuff to do with boxes
    ##########################

    def openBox(self, label):
        # If the label is an empty string, don't do anything, just stay at the
        # current position in the namespace hierarchy.
        # TODO: figure out how to store the original intended hierarchy
        if label:
            # create a new sub-namespace and make it a child of the current
            # namespace
            #
            # NOTE: labels are char*, which map to strings in Python2 and bytes
            # in Python3, so they need to be decoded to work in both
            box        = namespace(label)
            sane_label = str_to_identifier(label)
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

        # labels are char*, which map to strings in Python2 and bytes in
        # Python3, so they need to be decoded to work in both
        sane_label = str_to_identifier(label)
        setattr(self.__boxes[-1].__class__, sane_label, param(label, zone, init, min, max, step))

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
