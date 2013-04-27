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

# TODO: make the ui C object a member of PythonUI
class PythonUI(object):

    def __init__(self, obj=None):
        if obj:
            self.__boxes = [obj]
        else:
            self.__boxes = [self]

    def __set_boxes(self, b):
        self.__boxes = [b]

    boxes = property(fget=lambda x: x.__boxes[0], fset=__set_boxes)

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
        setattr(self.__boxes[-1], sane_label, param(zone, init, min, max, step))

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
