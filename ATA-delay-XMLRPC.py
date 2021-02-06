#!/usr/bin/env python3

# Delay estimator for ATA baselines
# Sends out delay values over XMLRCP, intended to be used with the
# ATA-FX GNU Radio correlator.

# See: https://github.com/PE1NUT/ATA-FX

# This software is (c) Paul Boven, licensed under GPLv3.

# TODO: Should take as parameters the antenna names or positions, and fixed delays to
# a reference antenne, and the source position.

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.constants import c
import time
from xmlrpc.client import ServerProxy

xmlrpc_client = ServerProxy('http://localhost:8080')

# Note: These coordinates are not official, but from clicking on Google Maps.
ant1a = EarthLocation.from_geodetic(lat = 40.816695 * u.deg, \
                                    lon = -121.471042 * u.deg, \
                                    height = 986 * u.m)

ant4g = EarthLocation.from_geodetic(lat = 40.8183207 * u.deg, \
                                    lon = -121.4704345 * u.deg, \
                                    height = 986 * u.m)

# Unfortunately, EarthLocation doesn't override the - operator.
baseline = EarthLocation(ant1a.x - ant4g.x, ant1a.y - ant4g.y, ant1a.z - ant4g.z)

# Note: this number is still being refined, and depends on the baseline.
fixed_delay = -(195 * u.m / c).to(u.s)

source = SkyCoord(ra = sys.argv[1] * u.deg, dec = sys.argv[2] * u.deg)

while True:
    obstime = Time.now()
    baseline_projected = 
        baseline.get_gcrs(obstime).cartesian.xyz.T.dot(source.cartesian.xyz)
    delay = baseline_projected / c + fixed_delay
    print(delay)
    xmlrpc_client.set_delay(float(delay.value))
    time.sleep(0.5)
