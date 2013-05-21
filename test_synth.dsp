declare name        "Simple test synth; produces garbage";
declare version     "0.0";
declare author      "Marc Joliet";
declare license     "MIT";
declare copyright   "(c)Marc Joliet 2013";

// produces the stream 1,0,1,0,...
process = _~+(1):%(2);
