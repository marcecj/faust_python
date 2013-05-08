#/usr/bin/env python

"""
A set of classes used to dynamically wrap FAUST DSP programs in Python.

This package defines three types:
- PythonUI is an implementation of the UIGlue C struct.
- FAUSTDsp wraps the DSP struct.
- FAUST integrates the other two, sets up the CFFI environment (defines the
  data types and API) and compiles the FAUST program.  This is the class you
  most likely want to use.
"""

from . wrapper import FAUST
from . python_ui import PythonUI, param
from . python_dsp import FAUSTDsp

__author__           = "Marc Joliet"
__copyright__        = "Copyright 2013, Marc Joliet"
__credits__          = ["Marc Joliet"]
__license__          = "MIT"
__version__          = "0.1"
__maintainer__       = "Marc Joliet"
__email__            = "marcec@gmx.de"
__status__           = "Prototype"

__all__ = ["FAUST", "PythonUI", "FAUSTDsp", "param", "wrapper"]
