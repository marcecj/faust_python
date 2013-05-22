# FAUSTPy
Marc Joliet <marcec@gmx.de>

A FAUST wrapper for Python.

## Introduction

FAUSTPy is a Python wrapper for the [FAUST](http://faust.grame.fr/) DSP
language. It is implemented using the [CFFI](https://cffi.readthedocs.org/) and
hence creates the wrapper dynamically at run-time.

## Installation

FAUSTPy has the following requirements:

- [FAUST](http://faust.grame.fr/), specifically the FAUST2 branch, because
  FAUSTPy requires the C backend.
- [CFFI](https://cffi.readthedocs.org/), tested with version 0.6.
- A C compiler; the default CFLAGS assume a GCC compatible one.
- [NumPy](http://numpy.scipy.org/), tested with version 1.6.

FAUSTPy works with Python 2.7 and 3.2+.

You can install FAUSTPy via the provided setup.py script by running

    sudo python setup.py install

or

    python setup.py install --user

Although you may want to verify that everything works beforehand by running the
test suite first:

    python setup.py test

## Useage

Using FAUSTPy is fairly simple, the main class is FAUSTPy.FAUST, which takes
care of the dirty work.  A typical example:

    dsp = FAUSTPy.FAUST("faust_file.dsp", fs)

This will create a wrapper that initialises the FAUST DSP with the sampling rate
`fs` and with `FAUSTFLOAT` set to the default value of `float` (the default
precision that is set by the FAUST compiler).  Note that this

1. compiles the FAUST DSP to C,
2. compiles and links the C code, and
3. initialises the C objects,

all of which happens in the background, thanks to the CFFI.  Furthermore, this
wrapper class

1. initialises the UI as a `ui` attribute of the DSP, and
2. stores the meta-data declared by the DSP as a `metadata` attribute.

To better match the [NumPy](http://numpy.scipy.org/) default of `double`, you
can overload the `faust_float` argument:

    dsp = FAUSTPy.FAUST("faust_file.dsp", fs, "double")

To process an array, simply call:

    # dsp.dsp is a PythonDSP object wrapped by the FAUST object
    audio = numpy.zeros((dsp.dsp.num_in, count))
    audio[:,0] = 1
    out = dsp.compute(audio)

Here the array `audio` is initialised to the number of inputs of the DSP and
`count` samples; each channel consists of a Kronecker delta, so `out` contains
the impulse response of the DSP.  In general `audio` is allowed to have more
channels (rows) than the DSP, in which case the first `dsp.dsp.num_in` channels
are processed, but not less.

You can also pass in-line FAUST code as the first argument, which will be
written to a temporary file and compiled by FAUST as usual.  In Python 3:

    dsp = FAUSTPy.FAUST(b"process = _:*(0.5);", fs)

Finally, below is a simple IPython example (using Python 2) that shows what a
FAUST object might look like.  It is based on the DSP
`dattorro_notch_cut_regalia.dsp` included in this repository.

    In [1]: import FAUSTPy

    In [2]: import numpy as np

    In [3]: fs = 48000

    In [4]: dattorro = FAUSTPy.FAUST("dattorro_notch_cut_regalia.dsp", fs, "double")

    In [5]: dattorro.
    dattorro.compute      dattorro.dsp          dattorro.FAUST_PATH
    dattorro.compute2     dattorro.FAUST_FLAGS

    In [5]: dattorro.dsp.
    dattorro.dsp.compute     dattorro.dsp.faustfloat  dattorro.dsp.num_out
    dattorro.dsp.compute2    dattorro.dsp.fs          dattorro.dsp.ui
    dattorro.dsp.dsp         dattorro.dsp.metadata
    dattorro.dsp.dtype       dattorro.dsp.num_in

    In [5]: dattorro.dsp.metadata
    Out[5]:
    {'author': 'Marc Joliet',
     'copyright': '(c)Marc Joliet 2013',
     'filter.lib/author': 'Julius O. Smith (jos at ccrma.stanford.edu)',
     'filter.lib/copyright': 'Julius O. Smith III',
     'filter.lib/license': 'STK-4.3',
     'filter.lib/name': 'Faust Filter Library',
     'filter.lib/reference': 'https://ccrma.stanford.edu/~jos/filters/',
     'filter.lib/version': '1.29',
     'license': 'MIT',
     'math.lib/author': 'GRAME',
     'math.lib/copyright': 'GRAME',
     'math.lib/license': 'LGPL with exception',
     'math.lib/name': 'Math Library',
     'math.lib/version': '1.0',
     'music.lib/author': 'GRAME',
     'music.lib/copyright': 'GRAME',
     'music.lib/license': 'LGPL with exception',
     'music.lib/name': 'Music Library',
     'music.lib/version': '1.0',
     'name': 'Dattoro notch filter and resonator (Regalia)',
     'version': '0.1'}

    In [6]: dattorro.dsp.fs
    Out[6]: 48000

    In [7]: dattorro.dsp.num_in
    Out[7]: 2

    In [8]: dattorro.dsp.num_out
    Out[8]: 2

    In [9]: dattorro.dsp.ui.
    dattorro.dsp.ui.label          dattorro.dsp.ui.metadata       dattorro.dsp.ui.p_Gain
    dattorro.dsp.ui.layout         dattorro.dsp.ui.p_Center_Freq  dattorro.dsp.ui.p_Q

    In [9]: dattorro.dsp.ui.label
    Out[9]: 'dattorro_notch_cut_regalia'

    In [10]: dattorro.dsp.ui.layout
    Out[10]: 'vertical'

    In [11]: dattorro.dsp.ui.p_Center_Freq
    Out[11]: <FAUSTPy.python_ui.Param at 0x31617d0>

    In [12]: dattorro.dsp.ui.p_Center_Freq.
    dattorro.dsp.ui.p_Center_Freq.default   dattorro.dsp.ui.p_Center_Freq.min
    dattorro.dsp.ui.p_Center_Freq.label     dattorro.dsp.ui.p_Center_Freq.step
    dattorro.dsp.ui.p_Center_Freq.max       dattorro.dsp.ui.p_Center_Freq.type
    dattorro.dsp.ui.p_Center_Freq.metadata  dattorro.dsp.ui.p_Center_Freq.zone

    In [12]: dattorro.dsp.ui.p_Center_Freq.label
    Out[12]: 'Center Freq.'

    In [13]: dattorro.dsp.ui.p_Center_Freq.metadata
    Out[13]: {'unit': 'Hz'}

    In [14]: dattorro.dsp.ui.p_Center_Freq.type
    Out[14]: 'HorizontalSlider'

    In [15]: audio = np.zeros((dattorro.dsp.num_in,fs), dtype=dattorro.dsp.dtype)

    In [16]: audio[:,0] = 1

    In [17]: audio
    Out[17]:
    array([[ 1.,  0.,  0., ...,  0.,  0.,  0.],
           [ 1.,  0.,  0., ...,  0.,  0.,  0.]])

    In [18]: dattorro.compute(audio)
    Out[18]:
    array([[ 0.74657288, -0.30020767,  0.0227801 , ...,  0.        ,
             0.        ,  0.        ],
           [ 0.74657288, -0.30020767,  0.0227801 , ...,  0.        ,
             0.        ,  0.        ]])

For more details, see the built-in documentation (aka `pydoc FAUSTPy`) and - if
you are so inclined - the source code.

## Demo script

The `__main__.py` of the FAUST package contains a small demo application which
plots some magnitude frequency responses of the example FAUST DSP.  You can
execute it by executing

    PYTHONPATH=. python FAUSTPy

in the source directory.  This will display four plots:

- the magnitude frequency response of the FAUST DSP at default settings,
- the magnitude frequency response with varying Q,
- the magnitude frequency response with varying gain, and
- the magnitude frequency response with varying center frequency.

## TODO

- finish the UIGlue wrapper
- finish the test suite
  - finish the unit tests
  - add functional tests so that you can test how everything works together
    (perhaps use "UITester.dsp" and maybe one other DSP from the examples)
