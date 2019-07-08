from __future__ import division
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from os.path import expanduser
from math import radians, cos, sin, asin, sqrt, pi
import sys
import geopy
from geopy.distance import VincentyDistance
from random import shuffle, uniform

mydir = expanduser("~/GitHub/asm")

lonlats = [[0,0], [0,90], [0,-90], [-180, 40], [180,-40]]

for ll in lonlats:
    
    m = Basemap(projection='ortho',lon_0=ll[0],lat_0=ll[1],resolution='l')
    S = 10000

    lats = []
    lons = []
    lat, lon = [0,0]
    d = 20037
    for ii in range(S):
        b = np.random.uniform(360)
        di = np.random.uniform(d)
            
        origin = geopy.Point(lat, lon)
        destination = VincentyDistance(kilometers=di).destination(origin, b)
        lat, lon = destination.latitude, destination.longitude
        
        lons.append(lon)
        lats.append(lat)
   

    lons, lats = m(lons, lats)
    m.scatter(lons, lats, marker='o',color='m',s=1)

    m.drawcoastlines()
    m.fillcontinents(color='None')
    m.drawmapboundary(fill_color='None')
    plt.show()