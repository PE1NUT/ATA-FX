#!/usr/bin/env python3

# Delay estimator for ATA baselines
# Sends out delay values over XMLRCP, intended to be used with the
# ATA-FX GNU Radio correlator.

# See: https://github.com/PE1NUT/ATA-FX

# This software is (c) Paul Boven, licensed under GPLv3.

# TODO: Swap sign of delay etc when baseline is the other way around

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.constants import c
import time
import pmt
import zmq
import sys

# Read all the source coordinates
ant_pos = {};
coords_file = open('antenna_coordinates_ecef.txt', 'r')
for line in coords_file:
    if line[0:7] == 'Antenna':
        continue
    (ant, x, y, z) = line.split(',')
    ant = ant.lower()
    ant_pos[ant] = (float(x), float(y),float(z))

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:50001")

# Note: this number is still being refined, and depends on the baseline.
# Note: it can jump by 100ns due to PPS/10MHz phase drift
fixed_delay = {}
fixed_delay[('1a', '4g')] = -750.8 *u.ns
fixed_delay[('1c', '4g')] = -750.8 *u.ns - 147.2  * u.ns
fixed_delay[('1h', '4g')] = -750.8 *u.ns + 26.6 * u.ns
fixed_delay[('2b', '4g')] = 33.46 * 20 * u.ns

source = SkyCoord(ra = float(sys.argv[1]) * u.deg, dec = float(sys.argv[2]) * u.deg)
ant_a = sys.argv[3].lower()
ant_b = sys.argv[4].lower()

baseline = EarthLocation((ant_pos[ant_b][0] - ant_pos[ant_a][0]) * u.m,
                         (ant_pos[ant_b][1] - ant_pos[ant_b][1]) * u.m,
                         (ant_pos[ant_b][2] - ant_pos[ant_b][2]) * u.m)

while True:
    obstime = Time.now()
    baseline_projected = \
        baseline.get_gcrs(obstime).cartesian.xyz.T.dot(source.cartesian.xyz)
    delay = baseline_projected / c + fixed_delay[(ant_b, ant_a)]
    msg = pmt.cons(pmt.intern("delay"), pmt.from_double(delay.value))
    sb = pmt.serialize_str(msg)
    socket.send(sb)
    time.sleep(0.5)
