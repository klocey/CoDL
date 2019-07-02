from __future__ import division
import gdal
import matplotlib
from mpl_toolkits.basemap import Basemap, addcyclic
import matplotlib.pyplot as plt
import numpy as np
from os.path import expanduser
from math import radians, cos, sin, asin, sqrt
import sys
import random
from random import choice, shuffle
from scipy import spatial, stats
import geopy
from geopy.distance import VincentyDistance
import requests


mydir = expanduser("~/GitHub/CoDL")


def get_abs(species, Sg, lon, lat, map_lons, map_lats, s_o_lons, s_o_lats):

    dist_from_o = []
    for si, val in enumerate(s_o_lons):
        d = haversine(val, s_o_lats[si], lon, lat)
        dist_from_o.append(d)
    dist_from_o = np.sqrt(np.array(dist_from_o))
    geo_match = (10/(10+dist_from_o))
    p_or_a0 = np.random.binomial(1, geo_match, Sg) 

    
    lon = min(map_lons, key=lambda x:abs(x-lon))
    lat = min(map_lats, key=lambda x:abs(x-lat))

    sad = p_or_a0 * geo_match**2
    
    return sad



def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km



def get_pts(r, loc1, d):
    
    pts = []
    
    lat, lon = loc1
    for ii in range(r):
        b = np.random.uniform(360)
        di = np.random.uniform(d)
        
        origin = geopy.Point(lat, lon)
        destination = VincentyDistance(kilometers=di).destination(origin, b)
        lat2, lon2 = destination.latitude, destination.longitude
        
        pts.append([lon2, lat2])

    return pts
    


######################### SIMULATION PARAMETERS ###############################

for t in range(100):
        
    Ds = []
    maxDs = []
    numSamp = []
    Sors = [] 
    EnvD = []
    As = []
    xs = []
    Ss = []
    clrs = []
    AccS = []
    Names = []
    Slopes = []
    
    #clr = 'lime' #randcolor()
    pts = []
    
    ######################### RUN SIMULATIONS #################################
    
    ct_m = 0
    r = 10
    Sg = 1000
    species = np.random.logseries(0.999, Sg)
    s_o_lats = np.linspace(-90, 90, Sg)
    shuffle(s_o_lats)
    s_o_lons = np.linspace(-180, 180, Sg)
    shuffle(s_o_lons)
    
    max_dist = 10**4
    loc1 = [0.0, 0.0]
    pts = get_pts(r, loc1, max_dist)
    
    
    pts_str = []
    for pt in pts:
        pts_str.extend(pt)
    pts_str = ','.join(map(str, pts_str)) 
    
    req_str = 'http://portal.gplates.org/service/reconstruct_points/?points='
    req_str = req_str + pts_str + '&time=' +str(t)+ '&model=default.json'
    response = requests.get(req_str)
    c_dict = eval(response.text)
    pts = c_dict["coordinates"]
    
    sys.exit()
        
    
    fig = plt.figure(figsize=(10,10))
    ax1 = plt.subplot2grid((4, 4), (0, 0), colspan=4, rowspan=2)
        
    #plt.style.use('dark_background')
    plt.style.use('classic')
        

    ######################## MODEL COMMUNITIES #######################
    lons = []
    lats = []
    for ii, val in enumerate(pts):
        lon1 = val[0]
        lat1 = val[1]
                
        lons.append(lon1)
        lats.append(lat1)
    
          
    Ds2 = []    
    Sor2 = []
    EnvD2 = []
    Ds2 = []   
    s_by_s = []
        
    for pt in pts:
        lon, lat = pt
        sad = get_abs(species, Sg, lon, lat, lons, lats, 
                      s_o_lons, s_o_lats)
        if max(sad) != 0:
            s_by_s.append(sad)
        else: s_by_s.append([0]*Sg)
            
        
    s_by_s = np.asarray(s_by_s)
    Gsad = s_by_s.sum(axis=0).tolist()
        
    try: 
        names = [iii for iii, v in enumerate(Gsad) if v > 0]
    except: 
        continue
    Names.extend(names)
    ns = len(list(set(Names)))
    AccS.append(ns)
        
        
    S = len(Gsad) - Gsad.count(0)
    Ss.append(S)


    ct = 0
    while ct < 2000:
            
        ind1 = choice(range(len(pts)))
        lon1, lat1 = pts[ind1]
        
        sad1 = s_by_s[ind1]
            
        if max(sad) == 0: continue

        ind2 = choice(range(len(pts)))
        lon2, lat2 = pts[ind2]
        if lat1 == lat2 and lon1 == lon2: continue
            
        
        sad2 = s_by_s[ind2]
                
        if max(sad) == 0: 
            continue
        else:        
            d = haversine(lon1, lat1, lon2, lat2)
                
            pair = np.asarray([sad1, sad2])
            pair = np.delete(pair, np.where(~pair.any(axis=0))[0], axis=1)
            dis = 1 - spatial.distance.pdist(pair, metric='braycurtis')[0]
            if np.isnan(dis) == True or dis < 0 or dis > 1: continue
            Sor2.append(dis)
                
            Ds2.append(d)
            ct += 1

        

