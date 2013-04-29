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
- [CFFI](https://cffi.readthedocs.org/)

Theoretically, FAUSTPy should work with Python 3, but I have not tested it.

You can install FAUSTPy via the provided setup.py script by running

    sudo python setup.py install

or

    python setup.py install --user

## Useage

Usage is fairly simple, the main class is FAUSTPy.FAUST, which takes care of the
dirty work.  A typical example:

    dsp = FAUSTPy.FAUST("faust_file.dsp", fs)

This will create a wrapper that initialises the FAUST DSP with the sampling rate
`fs` and with `FAUSTFLOAT` set to the default value of `float` (the default
precision that is set by the FAUST compiler).  Note that this

1. compiles the FAUST DSP to C,
2. compiles and links the C code, and
3. initialises the C objects,

all of which happens in the background, thanks to the CFFI.

To better match the [NumPy](http://numpy.scipy.org/) default of `double`, you
can instead simply do:

    dsp = FAUSTPy.FAUST("faust_file.dsp", fs, "double")

To process an array, simply call:

    # dsp.dsp is a FAUSTDsp object wrapped by the FAUST object
    audio = numpy.zeros((dsp.dsp.num_in, count))
    audio[:,0] = 1
    out = dsp.compute(audio)

Here the array `audio` is initialised to the number of inputs of the DSP and
`count` samples; each channel consists of a Kronecker delta, so `out` contains
the impulse response of the DSP.  In general `audio` is allowed to have more
channels (rows) than the DSP, in which case the first `dsp.dsp.num_in` channels
are processed, but not less.

For more details, see the built-in documentation (aka `pydoc FAUSTPy`).

## TODO

- finish the MetaGlue and UIGlue wrappers
- write a test suite
- write a demo program
