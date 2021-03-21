# ATA-FX
> A simple software correlator to test interferometry at the Alan Telescope Array

## Table of Contents

* [Introduction](#Introduction)
* [Results](#Results)
* [Baseline Fits](#baseline)
* [Usage](#Usage)
* [TODO](#Todo)

## Introduction

This project is a simple cross correlation engine based on GNU Radio.
It performs corrections for geometric delay, fringe rotation, and fractional delay. Even though we are still
refining the baseline coordinates, this approach centers and stops the fringe, and permits integration times on the order
of several minutes. The output product is a cross-spectrum with a configurable integration time and number of lags. 
The result can both be written to file, and viewed in realtime.
The realtime display shows the fringe peak (in the lag domain) and the phase over the frequency bins.

![ATA-FX Flowchart](ATA-FX-screenshot.png)

## Results

Initial observations on strong sources showed clear fringes even with integration times of 0.1 seconds.
As expected, fringe phase rotated rapidly. The correlator makes its output products available over a
ZMQ socket, allowing the fringe and its rotation to be viewed in real time.

Using a first estimate of the baseline vector, the fringe position could be centered, and its phase rotation slowed down
significantly. This allowed the observation of weaker sources as well by increasing the integration time. This could then be used to find a much
more accurate baseline (see next section), which seems stable at the cm level over 24 hours.

# Baseline Fits

By repeatedly observing a set of sources over many hours, a fit for all the parameters of the 1a-4g baseline has been constructed:
```
baseline 4g-1a = (-105.64717766, -73.78305528, -136.26892389) m, fixed delay = -750.8 ns, phase = -1.65 rad,
```

Determining a baseline involves several steps:

* Determine an initial estimate by finding the antenna coordinates in e.g. Google Maps
* Observe a bright, compact source to measure the phase slope over frequency. Determine a first estimate
of the fixed delay by looking at the maximum bin, and phase slope. Correcting for these centers the fringe.
* Observe a large set of compact sources, with different right ascension and declination, over several hours.
* Using the brightest, compact source, try to find the best fit for X and Y offsets. These are generally within 0.5 m
of the initial estimate.
* While fitting for X and Y, the fixed phase offset can be automatically sovled for as the average difference of
the unwrapped phase values. This requires dense enough measurements in time that the phase can be unwrapped.
* After fixing X and Y, use the observations of the other sources to find Z.
* Rerun some overvations with the improved baseline vector, to verify that phases are stable, and check for any
remaining residual effects

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

This software is not yet fully ready to use, but can be used as a starting point for more exploration.

* Steer two dishes to track the same source
* Configure the switch matrix
* Set observing frequency to 1350 MHz
* Compile the flowchart to python, copy the python file to the ATA
* Once the array is on source, run the compiled flowchart, which will record the data
* In a second shell, start the 'ATA-delay-ZMQ.py' which calculates the predicted delays
* The fringe can be viewed in real time using the included flowgraph 'ATA-ZMQ-display.grc'
* Add the recording to the source of 'baseline-phase.py' and run it, writing the results to 'file 'baseline-residuals'
* Edit the plot file and then run 'gnuplot baseline-phase-residuals.gpi' to create a graph
* Note: due to their size, observation data hasn't been included.

## TODO

Lots of TODOs, this software is very experimental

* Use both polarizations, and also compute autocorrelations
* Determine baseline vectors for the dishes that we can use
* Record simple sources over multiple baselines
* Try imaging the data
