from __future__ import division
import matplotlib.pyplot as plt
from os.path import expanduser
import statsmodels.api as sm
import pandas as pd
import numpy as np
import sys
from random import randint

mydir = expanduser("~/GitHub/CoDL")



######################### FUNCTIONS ###########################################

def randcolor():
    r = lambda: randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())





############################## DATA ###########################################

df = pd.read_csv(mydir+'/python_models/sim_data/ProcessFreeNull.txt')
#print list(df)

sims = list(set(df['sim']))




######################### FIG PARAMS ##########################################


sz = 10
lw = 1
a = 0.9
ws = 0.5
hs = 0.5
fs = 10
xlab = 'Age, mya'

clrs = []
for sim in sims:
    clr = randcolor()
    clrs.append(clr)


######################### GENERATE FIGS #######################################


fig = plt.figure()
fig.add_subplot(2, 2, 1)
metric = 'mean_braycurtis_nn'
for i, sim in enumerate(sims):
    
    df2 = df[df['sim'] == sim]
    
    x = df2['mya']
    y = df2[metric]
    
    plt.scatter(x, y, s = sz, c='0.8', linewidths=0.0, alpha=a, edgecolor=None)
    plt.plot(x, y, c='0.8', linewidth=lw, alpha=a)
    
y = df[metric].groupby(df['mya']).mean()
x = df['mya'].groupby(df['mya']).mean()

plt.scatter(x, y, s = sz, c='k', linewidths=0.0, alpha=a, edgecolor=None)
plt.plot(x, y, c='k', linewidth=lw, alpha=a)

plt.xlabel(xlab)
plt.ylabel('Similarity, Bray-Curtis')
plt.title('Mean community similarity\nof nearest neighbors', fontsize=fs)



fig.add_subplot(2, 2, 2)
metric = 'mean_geo_dist'
for i, sim in enumerate(sims):
    
    df2 = df[df['sim'] == sim]
    
    x = df2['mya']
    y = df2[metric]
    
    plt.scatter(x, y, s = sz, c='0.8', linewidths=0.0, alpha=a, edgecolor=None)
    plt.plot(x, y, c='0.8', linewidth=lw, alpha=a)
    
y = df[metric].groupby(df['mya']).mean()
x = df['mya'].groupby(df['mya']).mean()
plt.scatter(x, y, s = sz, c='k', linewidths=0.0, alpha=a, edgecolor=None)
plt.plot(x, y, c='k', linewidth=lw, alpha=a)

plt.xlabel(xlab)
plt.ylabel('Distance, km')
plt.title('Mean distance between sites', fontsize=fs)


    
    
fig.add_subplot(2, 2, 3)
metric = 'Bray_DD'
for i, sim in enumerate(sims):
    
    df2 = df[df['sim'] == sim]
    
    x = df2['mya']
    y = df2[metric]
    
    plt.scatter(x, y, s = sz, c='0.8', linewidths=0.0, alpha=a, edgecolor=None)
    plt.plot(x, y, c='0.8', linewidth=lw, alpha=a)
    
y = df[metric].groupby(df['mya']).mean()
x = df['mya'].groupby(df['mya']).mean()
plt.scatter(x, y, s = sz, c='k', linewidths=0.0, alpha=a, edgecolor=None)
plt.plot(x, y, c='k', linewidth=lw, alpha=a)
    
plt.xlabel(xlab)
plt.ylabel('Slope')
plt.title('Distance decay slope, Bray-Curtis', fontsize=fs)





#### Final Format and Save #####################################################
plt.subplots_adjust(wspace=ws, hspace=hs)
plt.savefig(mydir+'/python_models/figs/Sim_vs_Age.png',
    dpi=400, bbox_inches = "tight")
plt.close()