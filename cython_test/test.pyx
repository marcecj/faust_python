from test cimport *

cdef class param:

    def __cinit__(self, *args, **kargs):
        pass

    def __init__(self, zone, init, min, max, step):
        self.min = min
        self.max = max
        self.step = step
        self._zone = init
        self.__doc__ = "min={0}, max={1}, step={2}".format(min,max,step)

    def getter(self):
        return self._zone

    def setter(self, x):
        if   x >= self.max:
            self._zone = self.max
        elif x <= self.min:
            self._zone = self.min
        else:
            self._zone = self.min + round((x-self.min)/self.step)*self.step

    zone = property(fget=getter, fset=setter)


cdef class FAUSTBase(object):

    cdef list __boxes

    def __cinit__(self, *args, **kargs):
        pass

    def __init__(self):
        self.__boxes = [self]

    def declare(self, key, value):
        pass

    def openVerticalBox(self, label):
        if label:
            class namespace(object):
                pass

            # create a new sub-namespace and set it's parent to the current
            # namespace
            box = namespace()

            setattr(self.__boxes[-1], label, box)
            self.__boxes.append(box)

    def closeBox(self):

        self.__boxes.pop()

    def add_input(self, label, zone, init, min, max, step):

        setattr(self.__boxes[-1], label, param(zone, init, min, max, step))

class FAUST(FAUSTBase):

    def __init__(self):
        FAUSTBase.__init__(self)

cdef void* interface

cdef MetaGlue bla
bla.mInterface = interface

cdef UIGlue ui

faust = FAUST()
print faust
cdef void openVerticalBox(void* ignored, const char* label):
    faust.openVerticalBox(label)
# cdef void add_input(void* ignored, const char* label):
#     faust.openVerticalBox(label)

ui.openVerticalBox = &openVerticalBox
ui.openVerticalBox(NULL, "bla")
ui.openVerticalBox(NULL, "bla")
print dir(faust.bla)
