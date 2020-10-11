# ATA-FX
> A simple software correlator to test interferometry at the Alan Telescope Array

## Table of Contents

* [Introduction](#Introduction)
* [Results](#Results)
* [Usage](#Usage)
* [TODO](#Todo)

## Introduction

A simple project to test using interferometry on the ATA using GNU Radio and Python3.

## Results

So far, we've been mostly using ATA antennas 1H and 4G. We get very nice fringes on CasA and VirA on those.
Using the software in this repository, it's possible to calculate the delay change by unwrapping the fringe
phase, and multiplying it with the wavelength of the observation. This is then compared against the
predicted baseline length, calculated from the inner product of the (rotated) baseline, and the source location
on the sky. Ideally, the fringe phase should match the predicted baseline, resulting in a flat residual over
each observation. As the fringe phase only provides a relative measurement, the constant offset in each
observation is removed.

As the plot below shows, for most of the observations, the residuals are below the cm level. The observation
on VirA encountered a phase slip, and the first observation on CasA on 2020-10-10 had error reports from the USRP.

These residual plots have been used to improve the baseline vector, which for this pair of dishes is
```
baseline = (-172.922, -56.792, -160.605) m
```

![Baseline residuals](FX_baseline_phase_residuals.png)

## Usage

This software is not intended to be ready to use, but as a starting point for more exploration.

* Steer dishes 1H and 4G to a source
* Configure the switch matrix to use dishes 1H and 4G
* Set observing frequency to 1350 MHz
* Compile the flowchart to python, copy the python file to the ATA
* Once the array is on source, run the compiled flowchart, which will record the data
* Fringe can be viewed in real time using the included flowgraph 'ATA-ZMQ-display.grc'
* Add the recording to the source of 'baseline-phase.py' and run it, writing the results to 'file 'baseline-residuals'
* Edit the plot file and then run 'gnuplot baseline-phase-residuals.gpi' to create a graph
* Note: due to their size, previous observations haven't been included.

## TODO

Lots of TODOs, this software is very experimental

* Record fringes as complex spectra, instead of interleaving real/imaginary
* Higher sampling rate
* Use both polarizations, and also compute autocorrelations
* Remove fixed delay before correlation
