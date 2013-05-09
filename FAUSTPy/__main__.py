import argparse
import numpy as np
import matplotlib.pyplot as plt
from FAUSTPy import *

#######################################################
# set up command line arguments
#######################################################

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--faustfloat',
                    dest="faustfloat",
                    default="float",
                    help="The value of FAUSTFLOAT.")
parser.add_argument('-p', '--path',
                    dest="faust_path",
                    default="",
                    help="The path of FAUSTFLOAT.")
parser.add_argument('-c', '--cflags',
                    dest="cflags",
                    default=[],
                    type=str.split,
                    help="Extra compiler flags")
parser.add_argument('-s', '--fs',
                    dest="fs",
                    default=48000,
                    type=int,
                    help="The sampling frequency")
args = parser.parse_args()

#######################################################
# initialise the FAUST object and get the default parameters
#######################################################

wrapper.FAUST_PATH = args.faust_path

dattorro = FAUST("dattorro_notch_cut_regalia.dsp", args.fs, args.faustfloat,
                 extra_compile_args=args.cflags)

def_Q = dattorro.dsp.dattorro_notch_cut_regalia.Q
def_Gain = dattorro.dsp.dattorro_notch_cut_regalia.Gain
def_Freq = dattorro.dsp.dattorro_notch_cut_regalia.Center_Freq

#######################################################
# plot the frequency response with the default settings
#######################################################

audio = np.zeros((dattorro.dsp.num_in, args.fs), dtype=dattorro.dsp.dtype)
audio[:,0] = 1

out = dattorro.compute(audio)

print(audio)
print(out)

spec = np.fft.fft(out)[:,:args.fs/2]

fig = plt.figure()
p   = fig.add_subplot(
    1,1,1,
    title="Frequency response with the default settings\n"
          "(Q={}, F={:.2f} Hz, G={:.0f} dB FS)".format(
              def_Q.zone, def_Freq.zone, 20*np.log10(def_Gain.zone+1e-8)
          ),
    xlabel="Frequency in Hz (log)",
    ylabel="Magnitude in dB FS",
    xscale="log"
)
p.plot(20*np.log10(np.absolute(spec.T)+1e-8))
p.legend(("Left channel", "Right channel"), loc="best")

#######################################################
# plot the frequency response with varying Q
#######################################################

Q  = np.linspace(def_Q.min, def_Q.max, 10)

dattorro.dsp.dattorro_notch_cut_regalia.Center_Freq = 1e2
dattorro.dsp.dattorro_notch_cut_regalia.Gain = 10**(-0.5) # -10 dB

cur_G = dattorro.dsp.dattorro_notch_cut_regalia.Gain.zone
cur_F = dattorro.dsp.dattorro_notch_cut_regalia.Center_Freq.zone

fig = plt.figure()
p = fig.add_subplot(
    1,1,1,
    title="Frequency response "
          "(G={:.0f} dB FS, F={} Hz)".format(20*np.log10(cur_G+1e-8), cur_F),
    xlabel="Frequency in Hz (log)",
    ylabel="Magnitude in dB FS",
    xscale="log"
)

for q in Q:
    dattorro.dsp.dattorro_notch_cut_regalia.Q = q
    out = dattorro.compute(audio)
    spec = np.fft.fft(out)[0,:args.fs/2]

    p.plot(20*np.log10(np.absolute(spec.T)+1e-8),
           label="Q={}".format(q))

p.legend(loc="best")

#######################################################
# plot the frequency response with varying gain
#######################################################

# start at -60 dB because the minimum is at an extremely low -160 dB
G  = np.logspace(-3, np.log10(def_Gain.max), 10)

dattorro.dsp.dattorro_notch_cut_regalia.Q = 2

cur_Q = dattorro.dsp.dattorro_notch_cut_regalia.Q.zone
cur_F = dattorro.dsp.dattorro_notch_cut_regalia.Center_Freq.zone

fig = plt.figure()
p = fig.add_subplot(
    1,1,1,
    title="Frequency response (Q={}, F={} Hz)".format(cur_Q, cur_F),
    xlabel="Frequency in Hz (log)",
    ylabel="Magnitude in dB FS",
    xscale="log"
)

for g in G:
    dattorro.dsp.dattorro_notch_cut_regalia.Gain = g
    out = dattorro.compute(audio)
    spec = np.fft.fft(out)[0,:args.fs/2]

    p.plot(20*np.log10(np.absolute(spec.T)+1e-8),
           label="G={:.3g} dB FS".format(20*np.log10(g+1e-8)))

p.legend(loc="best")

###########################################################
# plot the frequency response with varying center frequency
###########################################################

F  = np.logspace(np.log10(def_Freq.min), np.log10(def_Freq.max), 10)

dattorro.dsp.dattorro_notch_cut_regalia.Q    = def_Q.default
dattorro.dsp.dattorro_notch_cut_regalia.Gain = 10**(-0.5) # -10 dB

cur_Q = dattorro.dsp.dattorro_notch_cut_regalia.Q.zone
cur_G = dattorro.dsp.dattorro_notch_cut_regalia.Gain.zone

fig = plt.figure()
p = fig.add_subplot(
    1,1,1,
    title="Frequency response "
          "(Q={}, G={:.0f} dB FS)".format(cur_Q, 20*np.log10(cur_G+1e-8)),
    xlabel="Frequency in Hz (log)",
    ylabel="Magnitude in dB FS",
    xscale="log"
)

for f in F:
    dattorro.dsp.dattorro_notch_cut_regalia.Center_Freq = f
    out = dattorro.compute(audio)
    spec = np.fft.fft(out)[0,:args.fs/2]

    p.plot(20*np.log10(np.absolute(spec.T)+1e-8),
           label="F={:.2f} Hz".format(f))

p.legend(loc="best")

################
# show the plots
################

plt.show()

print("everything passes!")
