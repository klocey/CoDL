from __future__ import division
import numpy as np
from os.path import expanduser
from math import radians, cos, sin, asin, sqrt
import sys
from scipy import spatial, stats
import geopy
from geopy.distance import VincentyDistance
import requests

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt, pi
from random import shuffle, uniform


mydir = expanduser("~/GitHub/CoDL")

OUT = open(mydir + '/python_models/sim_data/ProcessFreeNull.txt','w+')

headers = 'sim,mya,min_geo_dist,max_geo_dist,mean_geo_dist,'
headers += 'min_sorensen,mean_sorensen,max_sorensen,'
headers += 'min_braycurtis,mean_braycurtis,max_braycurtis,'
headers += 'min_canberra,mean_canberra,max_canberra,'
        
headers += 'min_geo_dist_nn,max_geo_dist_nn,mean_geo_dist_nn,'
headers += 'min_sorensen_nn,mean_sorensen_nn,max_sorensen_nn,'
headers += 'min_braycurtis_nn,mean_braycurtis_nn,max_braycurtis_nn,'
headers += 'min_canberra_nn,mean_canberra_nn,max_canberra_nn,'
        
        
headers += 'min_geo_dist_fn,max_geo_dist_fn,mean_geo_dist_fn,'
headers += 'min_sorensen_fn,mean_sorensen_fn,max_sorensen_fn,'
headers += 'min_braycurtis_fn,mean_braycurtis_fn,max_braycurtis_fn,'
headers += 'min_canberra_fn,mean_canberra_fn,max_canberra_fn,'

headers += 'Bray_DD,Sor_DD,Canb_DD'

print>>OUT, headers



def get_abs(species, Sg, lon, lat, map_lons, map_lats, s_o_lons, s_o_lats):

    dist_from_o = []
    for si, val in enumerate(s_o_lons):
        d = haversine(val, s_o_lats[si], lon, lat)
        dist_from_o.append(d)
    dist_from_o = np.sqrt(np.array(dist_from_o))
    geo_match = (100/(100+dist_from_o))
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
    


######################### RUN SIMULATIONS ###############################
for sim in range(100):
    pts = []
    ct_m = 0
    r = 250
    Sg = 10000
    species = np.random.logseries(0.999, Sg)
    
    s_o_lats = []
    s_o_lons = []
    lat, lon = [0,180]
    maxd = 20037
    for ii in range(Sg):
        b = np.random.uniform(360)
        di = np.random.uniform(maxd)
            
        origin = geopy.Point(lat, lon)
        destination = VincentyDistance(kilometers=di).destination(origin, b)
        lat, lon = destination.latitude, destination.longitude
        
        s_o_lons.append(lon)
        s_o_lats.append(lat)
        
    loc1 = [0.0, 0.0]
    pts = get_pts(r, loc1, maxd)
    pts_str = []
    for pt in pts:
        pts_str.extend(pt)
    pts_str = ','.join(map(str, pts_str))
    
    lons = []
    lats = []
    for ii, val in enumerate(pts):
        lons.append(val[0])
        lats.append(val[1])
    
    s_by_s = []
    for pt in pts:
        lon, lat = pt
        sad = get_abs(species, Sg, lon, lat, lons, lats, s_o_lons, s_o_lats)
        s_by_s.append(sad)
            
    s_by_s = np.asarray(s_by_s)
        
    ts = [1, 10, 50, 100, 150, 200, 250, 300]
    for t in ts:
        
        print 'sim:',sim,', mya:',t
        
        req_str = 'http://portal.gplates.org/service/reconstruct_points/?points='
        req_str = req_str + pts_str + '&time=' +str(t)+ '&model=default.json'
        response = requests.get(req_str)
        c_dict = eval(response.text)
        pts = c_dict["coordinates"]
        
        Ds = []    
        Sor = []
        Canb = []
        Bray = []
        
        Ds_nn = []    
        Sor_nn = []
        Canb_nn = []
        Bray_nn = []
        
        Ds_fn = []    
        Sor_fn = []
        Canb_fn = []
        Bray_fn = []
        
        Bray_DD = []
        Sor_DD = []
        Canb_DD = []
        
        for i, pt in enumerate(pts):
            
            lon1, lat1 = pts[i]
            sad1 = s_by_s[i]
            
            d_nn = 10**6
            d_fn = 0
            
            sor_nn = 0
            canb_nn = 0
            bray_nn = 0
            sor_fn = 0
            canb_fn = 0
            bray_fn = 0
            
            for ii, pt in enumerate(pts):
                if ii <= i:
                    continue
    
                lon2, lat2 = pts[ii]
                sad2 = s_by_s[ii]
                
                d = haversine(lon1, lat1, lon2, lat2)
                    
                pair = np.asarray([sad1, sad2])
                pair = np.delete(pair, np.where(~pair.any(axis=0))[0], axis=1)
                    
                bray = 1 - spatial.distance.pdist(pair, metric='braycurtis')[0]
                Bray.append(bray)
                    
                sor = 1 - spatial.distance.pdist(pair, metric='dice')[0]
                Sor.append(sor)
                    
                canb = 1 - spatial.distance.pdist(pair, metric='canberra')[0]/len(sad1)
                Canb.append(canb)
                    
                Ds.append(d)
                
                if d < d_nn:
                    d_nn = float(d)
                    sor_nn = sor
                    bray_nn = bray
                    canb_nn = canb
                    
                elif d > d_fn:
                    d_fn = float(d)
                    sor_fn = sor
                    bray_fn = bray
                    canb_fn = canb
            
            if d_nn != 10**6 and d_fn != 0:
                Ds_nn.append(d_nn)
                Sor_nn.append(sor_nn)
                Canb_nn.append(canb_nn)
                Bray_nn.append(bray_nn)
        
                Ds_fn.append(d_fn)
                Sor_fn.append(sor_fn)
                Canb_fn.append(canb_fn)
                Bray_fn.append(bray_fn)
                
        
        '''
        m = Basemap(projection='ortho', lon_0=0, lat_0=0, resolution='l')
        S = 10000

        lats = []
        lons = []
        for pt in pts:
            lats.append(pt[1])
            lons.append(pt[0])

        lons, lats = m(lons, lats)
        m.scatter(lons, lats, marker='o',color='m',s=10)

        #m.drawcoastlines()
        m.fillcontinents(color='None')
        m.drawmapboundary(fill_color='None')
        plt.show()
        '''
    
    
        outlist = []
        
        min_geo_dist = min(Ds)
        max_geo_dist = max(Ds)
        mean_geo_dist = np.mean(Ds)
        min_sorensen = min(Sor)
        mean_sorensen = np.mean(Sor)
        max_sorensen = max(Sor)
        min_braycurtis = min(Bray)
        mean_braycurtis = np.mean(Bray)
        max_braycurtis = max(Bray)
        min_canberra = min(Canb)
        mean_canberra = np.mean(Canb)
        max_canberra = max(Canb)
        
        outlist.extend([sim,t,min_geo_dist,max_geo_dist,mean_geo_dist])
        outlist.extend([min_sorensen,mean_sorensen,max_sorensen])
        outlist.extend([min_braycurtis,mean_braycurtis,max_braycurtis])
        outlist.extend([min_canberra,mean_canberra,max_canberra])
        
        min_geo_dist_nn = min(Ds_nn)
        max_geo_dist_nn = min(Ds_nn)
        mean_geo_dist_nn = min(Ds_nn)
        min_sorensen_nn = min(Sor_nn)
        mean_sorensen_nn = min(Sor_nn)
        max_sorensen_nn = min(Sor_nn)
        min_braycurtis_nn = min(Bray_nn)
        mean_braycurtis_nn = min(Bray_nn)
        max_braycurtis_nn = min(Bray_nn)
        min_canberra_nn = min(Canb_nn)
        mean_canberra_nn = min(Canb_nn)
        max_canberra_nn = min(Canb_nn)
        
        outlist.extend([min_geo_dist_nn,max_geo_dist_nn,mean_geo_dist_nn])
        outlist.extend([min_sorensen_nn,mean_sorensen_nn,max_sorensen_nn])
        outlist.extend([min_braycurtis_nn,mean_braycurtis_nn,max_braycurtis_nn])
        outlist.extend([min_canberra_nn,mean_canberra_nn,max_canberra_nn])

        min_geo_dist_fn = min(Ds_fn)
        max_geo_dist_fn = min(Ds_fn)
        mean_geo_dist_fn = min(Ds_fn)
        min_sorensen_fn = min(Sor_fn)
        mean_sorensen_fn = min(Sor_fn)
        max_sorensen_fn = min(Sor_fn)
        min_braycurtis_fn = min(Bray_fn)
        mean_braycurtis_fn = min(Bray_fn)
        max_braycurtis_fn = min(Bray_fn)
        min_canberra_fn = min(Canb_fn)
        mean_canberra_fn = min(Canb_fn)
        max_canberra_fn = min(Canb_fn)
        
        outlist.extend([min_geo_dist_fn,max_geo_dist_fn,mean_geo_dist_fn])
        outlist.extend([min_sorensen_fn,mean_sorensen_fn,max_sorensen_fn])
        outlist.extend([min_braycurtis_fn,mean_braycurtis_fn,max_braycurtis_fn])
        outlist.extend([min_canberra_fn,mean_canberra_fn,max_canberra_fn])
        
        
        Bray = np.array(Bray)/max(Bray)
        Sor = np.array(Sor)/max(Sor)
        Canb = np.array(Canb)/max(Canb)
        Ds = np.array(Ds)/max(Ds)
        
        Bray_slope, Bray_int, r, p, std_err = stats.linregress(Bray, Ds)
        Sor_slope, Bray_int, r, p, std_err = stats.linregress(Sor, Ds)
        Canb_slope, Bray_int, r, p, std_err = stats.linregress(Canb, Ds)
        
        outlist.extend([Bray_slope,Sor_slope,Canb_slope])
        
        outlist = str(outlist).strip('[]')
        outlist = outlist.replace(" ", "")
    
        OUT = open(mydir + '/python_models/sim_data/ProcessFreeNull.txt','a+')
        print>>OUT, outlist
        OUT.close()
        
    