#!/usr/bin/env python3

# Performs post-processing of FX cross correlated data
# Caclulates the baseline residuals by determining the fringe phase, unwrapping it,
# and subtracting the projected baseline for the source benig observed.
# The unwrapped phase only provides a relative measurement, and the starting phase
# is random, so subtract the average offset for each scan.

# (C) Paul Boven, GPL v3

# https://github.com/PE1NUT/ATA-FX

from astropy.coordinates import SkyCoord, EarthLocation, GCRS
from astropy import units as u
from astropy.time import Time
from astropy.constants import c
import numpy as np

# Read in recorded fringe
# TODO: In future observations, might as well store the fringe as complex data
def read_xc_data(fn):
    data = np.fromfile(fn, dtype='float32')
    # Reshape into interleaved I/Q spectra of 256 bins
    data = np.reshape(data, (-1, 2, 256))
    # Convert into complex array
    return data[:,0,:] + 1j * data[:,1,:]

# Integration: return fringe averaged over 1 second
# TODO: this is a hack, should be replaced by proper rational resampling
# TODO: Numpy abuse, figure out how to deal with varying stepsize, or above.
# Magic numbers: 256 is the number of spectral bins, 1000 is the integration in the FX correlator
# and 10e6 is the sampling rate of the observation.
def int_xc(data):
    f = []
    t = 0
    n = 0
    count = 0
    xc = 0
    for a in data:
        xc += a # complex addition, so coherent integration
        t += 256 * 1000 / 10e6
        n += 1
        if t > 1.0 :
            f.append(a / n)
            n = 0
            xc = 0
            t -= 1
    if t > 0.5: # If there's more than half a second left over, tack that on.
        f.append(a/n)
    return np.array(f)
            
# Find max amplitude in each xc, return its phase (in radians)
def phase_xc(data):
    maxbin = np.argmax(np.absolute(data), axis = 1)
    return np.angle(data[np.arange(data.shape[0]), maxbin])

# Observation parameters
f = 1350e6 * u.Hz
labda = (c/f).to(u.m)

# Telescope locations, to determine the baseline, and sky position of the source
# Note: These are just from Google Maps, to be replaced with the actual coordinates.
ant1h = EarthLocation.from_geodetic(lat = 40.816410 * u.deg, lon = -121.471831 * u.deg, height = 986 * u.m)
#ant4g = EarthLocation.from_geodetic(lat = (40.818315 ) * u.deg, lon = (-121.470432 ) * u.deg, height = 986 * u.m)
# Revised location for a better baseline fit
ant4g = EarthLocation.from_geodetic(lat = (40.818315 + 0.0000057) * u.deg, lon = (-121.470432 - 0.0000025) * u.deg, height = 986 * u.m)
baseline = EarthLocation(ant1h.x - ant4g.x, ant1h.y - ant4g.y, ant1h.z - ant4g.z)

print(baseline)
asdlfasdlfjk
# List of observed sources, so we hit the lookup only once
CasA = SkyCoord.from_name('Cas A')
VirA = SkyCoord.from_name('Vir A')

# List of fringe recordings: filename, source, start time
# TODO: get the length and start time of each file, or better: use metadata
obs = (('CasA-fringe-256bins-IQ-float', CasA, Time('2020-10-04 23:55:13') - 3431 * u.s),
       ('VirA-fringe-256bins-IQ-float', VirA, Time('2020-10-04 22:54:27') - 1776 * u.s),
       ('CasA-fringe-256bins-IQ-float-2020-10-10-07_10', CasA, Time('2020-10-10 07:35:47') - 1411 * u.s),
       ('CasA-fringe-256bins-IQ-float2020-10-10 08:58:58.096593', CasA, Time('2020-10-10 11:25:49') - 8794 * u.s),
       ('CasA-fringe-256bins-IQ-float2020-10-10 12:01:50.510766', CasA, Time('2020-10-10 12:01:50') + 18 * u.s),
       ('CasA-fringe-256bins-IQ-float2020-10-10 12:35:57.197301', CasA, Time('2020-10-10 15:01:18') - 8702 * u.s))

# Process each scan, printing out the difference between the baseline delay,
# and the averaged unwrapped phase (in metres), after subtracting the average offset.
# Ideally, this should be flat for every observation.
for (fn, source, start) in obs:
    xc = int_xc(read_xc_data(fn))
    phase = np.unwrap(phase_xc(xc))
    delay_measured = labda * phase / 2 / np.pi
    # Calculate the projected baseline for every measured phase second
    # Add half a second to calculate the midpoint of each integration
    obstime = start + range(len(delay_measured)) * u.s + 0.5 *u.s
    baseline_projected = baseline.get_gcrs(obstime).cartesian.xyz.T.dot(source.cartesian.xyz)
    offset = np.average(delay_measured - baseline_projected)
    print(*(delay_measured - baseline_projected - offset).value, sep = '\n')
    print() # Two newlines to indicate a new index to gnuplot
    print()
