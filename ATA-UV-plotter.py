#!/usr/bin/env python3

import numpy as np
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, Angle
import astropy.units as u
from astropy.time import Time
from astropy.constants import c
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import itertools
import sys

def baseline(bl):
    a = bl[0]
    b = bl[1]
    return EarthLocation(ant_pos[b].x - ant_pos[a].x,
                         ant_pos[b].y - ant_pos[a].y,
                         ant_pos[b].z - ant_pos[a].z)
                        
def baselines(usrp1, usrp2):
    return list(itertools.product(usrp1, usrp2))

def baseline2uvw(bl_rot, s, λ):
# Calculate u, v, w coordinates from the source position and
# rotated baseline
    bl = bl_rot.cartesian
    u =  np.sin(s.ra)  * bl.x + np.cos(s.ra) * bl.y
    v = -np.sin(s.dec) * np.cos(s.ra) * bl.x + \
         np.sin(s.dec) * np.sin(s.ra) * bl.y + \
         np.cos(s.dec) * bl.z
    w =  np.cos(s.dec) * np.cos(s.ra) * bl.x + \
        -np.cos(s.dec) * np.sin(s.ra) * bl.y + \
         np.sin(s.dec) * bl.z
    return u/λ, v/λ, w/λ
    
def read_ant_pos():
    global ant_pos
    if len(ant_pos) > 0:
        return
    coords_file = open('antenna_coordinates_ecef.txt', 'r')
    for line in coords_file:
        if line[0:7] == 'Antenna': # Skip header
            continue
        (ant, x, y, z) = line.split(',')
        x = float(x) * u.m
        y = float(y) * u.m
        z = float(z) * u.m
        ant_pos[ant.lower()] = EarthLocation(x, y, z)
    return

def source(name):
    sources = {'CasA'   : (350.85  , 58.815),
               '3C286'  : (202.7844708  , 30.5090842),
               'VirA'   : (187.70593076  , 12.39112329),
               'CygA'   : (299.86815191  , 40.73391574),
               '3C84'   : (49.95066567  , 41.51169838),
               '3C48'   : (24.4220816  , 33.1597442),
               'TauA'   : (83.633083  , 22.0145),
               '4C39.25': (141.76247  , 39.03755),
               '3C345'  : (250.7449658  , 39.810233),
               '3C147'  : (85.65057458  , 49.85200937),
               '3C138'  : (80.29119136  , 16.63945882),
               '3C454.3': (343.4906339  , 16.1482595) }
    source = sources[name] * u.deg
    return SkyCoord(source[0], source[1])

#########################################################
#
# Main Loop
#
#########################################################

# Keep as a global array for convenience
ant_pos = {}

if len(sys.argv) != 3 or sys.argv[1] == '-h':
    print('Usage: ATA-UV-plotter.py <name> <freq>')
    print('where freq is an integer in MHz')
    print('Output file: ATA-UV-<source>-<freq>MHz.png')
    sys.exit()

read_ant_pos()

f = int(sys.argv[2]) *  u.MHz
fig, axs = plt.subplots(1,1, figsize = (12,10))
fig.suptitle('ATA UV plot ' + sys.argv[1] + ' ' + str(f))

source = source(sys.argv[1])
λ = (c / f).to(u.m)

usrp1 = ['1a', '2c', '2a', '4g', '4j']
usrp2 = ['1f', '1h', '1k', '2b', '2h', '3c', '5c']

colors = itertools.cycle(cm.rainbow(np.linspace(0, 1, len(baselines(usrp1, usrp2)))))

# Start with CygA well below the horizon
obs24h = Time('2021-06-10 00:00:00', format = 'iso') + np.linspace(0, 24, 96, endpoint = False) * u.hour
azel = source.transform_to(AltAz(obstime = obs24h, location = ant_pos['1a']))

# Remove all timepoints where the elevation is < 20 deg
obstime = []
for i in range(len(obs24h)):
    if azel[i].alt.deg > 20:
        obstime.append(obs24h[i])
obstime = Time(obstime)

for bl in baselines(usrp1, usrp2):
#for bl in [('4g', '2b')]:
    bl_lab = bl[0] + '-' + bl[1]
    bl_rot = baseline(bl).get_gcrs(obstime)
    (u, v, w) = baseline2uvw(bl_rot, source, λ)
    c = next(colors)
    axs.plot(u, v, marker = '+', label = bl_lab, c = c)
    axs.plot(-u, -v, marker = '+', c = c)

plt.legend(ncol = 1, loc = 'center left',
    bbox_to_anchor = (1,0,1,1))
axs.set_aspect(1)
axs.grid()
axs.set_xlabel('u [λ]')
axs.set_ylabel('v [λ]')
plt.tight_layout(rect = [0, 0.003, 1, 0.95])
fig.savefig('ATA-UV-'+sys.argv[1]+'-'+str(int(f.value))+'MHz.png')
