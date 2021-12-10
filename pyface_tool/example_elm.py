#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 11:53:29 2021

@author: guterlj
"""
from pyface_tool import *
import matplotlib.pyplot as plt


def f_elm(X):
    if X<0: 
        return 0.0
    else:
        return 1/(X+1e-10)**2*np.exp(1-1/(X+1e-10)**2)

def Gamma_elm(t,tau=2e-4,gamma0=1e24,gamma_elm=1e25,felm=1e2,nrepeat=1, tstart=1e2):
    return gamma0 + (gamma_elm-gamma0)*np.sum(np.array([f_elm((t-i/felm-tstart)/tau) for i in range(nrepeat)]))

time = np.linspace(1e2,1e2+1e-3,100000)
fig,ax = plt.subplots(1)
ax.plot(time,[Gamma_elm(t) for t in time])

##############################################################################
r = RunFACE(verbose=False)
r.setup()

r.vec_bulk += ['src']
r.plot_dens_list+=['src']
r.plot_flx_list+=['dsrfl']
r.plot_flx_xlim =[1e-5,1e2]
r.plot_flx_ylim =[1e12,1e25]
r.plot_dens_ylim =[1e15,1e30]

r.init()

r.reduction_factor_dt_spc =0.05
r.temp=800
r.Edes_l = 0.1
r.Edes_lsat=0.0
r.Eads_l=0.0
r.inflx=1e24

r.run(iter_max=40000, liveplot=True, niter_collect=500, time_max=1e2)
 ###### ELM###
r.time_inputs = {'inflx':Gamma_elm}
r.dt_face_max = 1e-6
r.dt_face = 1e-6
r.time_max = 1e2+3e-3 
r.ax_flx.set_xlim([1e2,1e2+3e-3])
r.ax_flx.set_ylim([1e12,1e25])
r.ax_flx.set_xscale('linear')

r.run(niter_collect=25)

r.save_state('data_elm.npy',overwrite=True)

   