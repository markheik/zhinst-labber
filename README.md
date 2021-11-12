# Zurich Instruments Labber Drivers

The Zurich Instruments Labber Drivers are a collection of instrument drivers for
the scientific measurement software [Labber](http://labber.org/). They provide
a high-level interface of Zurich Instruments devices such as

* the PQSC Programmable Quantum System Controller
* the HDAWG Arbitrary Waveform Generator
* the UHFQA and SHFQA Quantum Analyzers
* the MFLI and UHFLI Lock-In Amplifiers

The Labber drivers are based on the
[Zurich Instruments Toolkit](https://github.com/zhinst/zhinst-toolkit)
(*zhinst-toolkit*), an extension of our Python API *ziPython* for high-level
instrument control.


# Status

The Zurich Instruments Labber Drivers are well tested and considered stable
enough for general usage. The interfaces may have some incompatible changes
between releases. Please check the changelog if you are upgrading.


# Getting Started

## LabOne

As prerequisite, the LabOne software version 20.01 or later must be installed.
It can be downloaded for free at https://www.zhinst.com/labone. Follow the
installation instructions specific to your platform. Verify that you can connect
to your instrument(s) using the web interface of LabOne. If you are upgrading
from an older version, be sure to update the firmware of al your devices using
the web interface before continuing. In principle LabOne can be installed in a
remote machine, but we highly recommend to install on the local machine where
you intend to run the experiment.


## Labber Drivers

Download this repository as ZIP folder and unpack its content. It contains a set of
folders with the names *'Zurich_Instruments_XXXX'* that define the instrument
drivers. In order to make the drivers available in Labber, the folders
*'Zurich_Instruments_XXXX'* need to be copied to your *local* Labber Drivers
folder. It is located in *'C:\Users\USERNAME\Labber\Drivers'* or similar. Once
the driver folders are copied to your local Labber Drivers folder, they are
available to be selected in the *Labber Instrument Server*.

## Install dependencies (e.g. `zhinst-toolkit`)

The Zurich Instruments Labber Drivers are based on the
[Zurich Instruments Toolkit](https://github.com/zhinst/zhinst-toolkit) and a small set of third party packages.
A complete list can be found inside the [requirements.txt](requirements.txt)[]().
There are two ways to install these dependencies:

### Using Labber's Python distribution

Labber comes with its own Python distribution that is used by default. The required  packages needs to be installed with to this Python distribution,
which is done using Labber's own `pip` package manager. It is located
(on Windows) under C:\Program Files
*'(x86)\Labber\python-labber\Scripts\pip.exe'* or similar.

From within the unpacked project folder run:
``` bash
<path to Labber Scripts folder>\pip install -r requirements.txt
```

### Use your own Anaconda distribution

Alternatively, Labber can also configured to use your own Python distribution. Under *Instrument Server -> Preferences -> Advanced -> Python Distribution* you can
point Labber to a different Python distribution, for example your *Anaconda*
environment. If you chose for example you *base* Anaconda environment, install the required packages as followed.

From within the unpacked project folder run:
```
conda activate base
pip install -r requirements.txt
```

## Try It Out

To see if your installation was successful, try to connect to your device. Add
the instrument driver of your model to the *Instrument Server* with the serial
number (e.g. *'dev1234'*) in the *Address* field and start the instrument. If
the window turns green and no error emssage appears, you are ready to go!
