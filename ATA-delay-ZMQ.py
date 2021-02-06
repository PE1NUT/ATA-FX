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

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:50001")

# Note: These coordinates are not official, but from clicking on Google Maps.
ant1a = EarthLocation.from_geodetic(lat = 40.816695 * u.deg, \
                                    lon = -121.471042 * u.deg, \
                                    height = 986 * u.m)

ant1c = EarthLocation.from_geodetic(lat = 40.815967 * u.deg, \
                                    lon = -121.470725 * u.deg, \
                                    height = 986 * u.m)

ant1h = EarthLocation.from_geodetic(lat = 40.816410 * u.deg, \
                                    lon = -121.471831 * u.deg, \
                                    height = 986 * u.m)

ant4g = EarthLocation.from_geodetic(lat = 40.8183207 * u.deg, \
                                    lon = -121.4704345 * u.deg, \
                                    height = 986 * u.m)

# Unfortunately, EarthLocation doesn't override the - operator.
# These are corrections for fringe stopping on each baseline, which can't
# readily be attributed to any antenna.
baseline = {}
baseline[('1a', '4g')] = EarthLocation(ant1a.x - ant4g.x -0.31*u.m, ant1a.y - ant4g.y + 0.12 *u.m, ant1a.z - ant4g.z + 0.38 * u.m)
baseline[('1c', '4g')] = EarthLocation(ant1c.x - ant4g.x -1.038*u.m, ant1c.y - ant4g.y - 0.697 *u.m, ant1c.z - ant4g.z + 1.63 * u.m)
baseline[('1h', '4g')] = EarthLocation(ant1h.x - ant4g.x -0.10*u.m, ant1h.y - ant4g.y + 0.009 *u.m, ant1h.z - ant4g.z + 0.42 * u.m)
baseline[('2b', '4g')] = EarthLocation(39.922913 * u.m, 60.929134 * u.m, 83.856601 * u.m)

# Note: this number is still being refined, and depends on the baseline.
# NOte: it can jump by 100ns due to PPS/10MHz phase drift
fixed_delay = {}
fixed_delay[('1a', '4g')] = -750.8 *u.ns
fixed_delay[('1c', '4g')] = -750.8 *u.ns - 147.2  * u.ns
fixed_delay[('1h', '4g')] = -750.8 *u.ns + 26.6 * u.ns
fixed_delay[('2b', '4g')] = 33.46 * 20 * u.ns

source = SkyCoord(ra = float(sys.argv[1]) * u.deg, dec = float(sys.argv[2]) * u.deg)
anta = sys.argv[3]
antb = sys.argv[4]

while True:
    obstime = Time.now()
    baseline_projected = \
        baseline[(antb, anta)].get_gcrs(obstime).cartesian.xyz.T.dot(source.cartesian.xyz)
    delay = baseline_projected / c + fixed_delay[(antb, anta)]
    msg = pmt.cons(pmt.intern("delay"), pmt.from_double(delay.value))
    sb = pmt.serialize_str(msg)
    socket.send(sb)
    time.sleep(0.5)
