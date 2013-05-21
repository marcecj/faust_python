class PythonMeta(object):
    """
    Stores DSP meta-data in a metadata attribute of another object, specifically
    a FAUST wrapper object.

    In FAUST, a DSP may specify meta-data of itself and libraries it uses, which
    it does through the declare() method of a Meta object.  The PythonMeta class
    implements such a Meta object.  It creates a C callback to its declare()
    method and stores it in a Meta struct, which can be passed to the
    metadatamydsp() function of a FAUST DSP object.
    """

    def __init__(self, ffi, obj=None):
        """
        Initialise a PythonMeta object.

        Parameters:
        -----------

        ffi : cffi.FFI
            The CFFI instance that holds all the data type declarations.
        obj : object (optional)
            The Python object in which the meta-data is to be stored.  If None
            (the default) the PythonMeta instance manipulates itself.
        """

        if obj:
            self.__obj = obj
        else:
            self.__obj = self

        self.__obj.metadata = {}

        def declare(mInterface, key, value):
            self.declare(ffi.string(key), ffi.string(value))

        self.__declare_c = ffi.callback("void(void*, char*, char*)", declare)

        meta = ffi.new("MetaGlue*")
        meta.declare = self.__declare_c
        meta.mInterface = ffi.NULL # we don't use this anyway

        self.__meta = meta

    meta = property(fget=lambda x: x.__meta,
                    doc="The Meta struct that calls back to its parent object.")

    def declare(self, key, value):

        self.__obj.metadata[key] = value

