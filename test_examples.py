import os
import glob
import argparse
import FAUSTPy

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path',
                    dest="examples_path",
                    default="/usr/share/faust-*/examples",
                    help="The path to the FAUST examples."
                   )
args = parser.parse_args()

fs = 48e3

for f in glob.glob(os.sep.join([args.examples_path, "*.dsp"])):
    print(f)
    dsp = FAUSTPy.FAUST(f, int(fs), "double")
