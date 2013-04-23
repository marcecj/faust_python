declare name        "Dattoro notch filter and resonator (Regalia)";
declare version     "0.1";
declare author      "Marc Joliet";
declare license     "MIT";
declare copyright   "(c)Marc Joliet 2013";

import("filter.lib");
import("math.lib");

// user inputs
fc = hslider("Center Freq. [unit:Hz]", 5e3, 30, 20e3, 1);
k  = hslider("Gain", 0.0, 0.0, 5.0,  1e-3);
q  = hslider("Q",    1,  1, 10, 1e-3);

wc    = 2*PI*fc/SR;

// the allpass is constructed from last to first coefficient; use the normalised
// ladder form for increased robustness
//ap(beta, gamma) = allpassnn(2, (gamma, beta));
ap(beta, gamma) = allpassn(2, (gamma, beta));

notch_resonator_regalia(k, fc) = H with {
    beta  = (1-tan(wc/(2*q)))/(1+tan(wc/(2*q)));
    gamma = neg(cos(wc));
    A     = ap(beta, gamma);
    H     = _ : *(0.5) <: *(1+k),(A:*(1-k)) :> _;
};

process = notch_resonator_regalia(k,fc);
