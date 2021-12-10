#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 16:22:52 2021

@author: guterlj
"""
import time
from matplotlib.pylab import plt
from pyface_tool import utils
from pyface import face
plt.ion()
class PlotFACE():
    def __init__(self,*args, **kwargs):
        self.liveplot = False
        self.ax_dens = None
        self.ax_flx = None
        self.plot_flx_list = ['Gdes_l','Gdes_r','inflx']
        self.plot_dens_list = ['dens']
        self.plt_obj_flx = {}
        self.plt_obj_dens = {}
        self.plot_dens_ylim = [1e9,1e25]
        self.plot_flx_ylim = [1e15,1e22]
        self.plot_flx_xlim = []

            
            
    def init_plots(self):
        fig,axes = plt.subplots(2,1)
        self.ax_dens = axes[0]
        self.ax_flx = axes[1]
        self.ax_flx.set_xlabel('time[s]')
        self.ax_flx.set_ylabel('flux [m^-2.s^-1]')
        self.ax_flx.set_xscale('log')
        self.ax_flx.set_yscale('log')
        self.ax_dens.set_xscale('log')
        self.ax_dens.set_yscale('log')
        self.ax_dens.set_xlabel('depth [m]')
        self.ax_dens.set_ylabel('density [m^-3]')
        
    @utils.kwgetter
    def plot_dens(self, species=None):
        
        if self.ax_dens is None:
            self.init_plots()
        for k in range(face.nspc):
            if self.verbose: print('plotting dens for', k)
            spc = face.namespc[k].decode('utf-8')
            if species is None or spc in species:
                if self.plt_obj_dens.get(k) is None:
                    print(k,self.iter_data,self.data['x'],self.data['dens'][self.iter_data-1,:,k])
                    self.plt_obj_dens[k] = dict((var,self.ax_dens.plot(self.data['x'],self.data[var][self.iter_data-1,:,k],label='{} {}'.format(var, spc))) for var in self.plot_dens_list)
                    self.ax_dens.legend()
                    
                    #self.ax_dens.set_xlim([0,self.time_max])
        
                else:
                    for var in self.plot_dens_list:
                        self.plt_obj_dens[k][var][0].set_xdata(self.data['x'])
                        self.plt_obj_dens[k][var][0].set_ydata(self.data[var][self.iter_data-1,:,k])
                   
        self.ax_dens.set_title('iteration:{}/{} ; time:{:3.3e}; dt={:3.3e}'.format(self.iter,self.iter_max,self.time,self.dt_face))
        self.ax_dens.set_ylim(self.plot_dens_ylim)              
    def plot_flx(self, species=None):
        
        if self.ax_flx is None:
            self.init_plots()
        for k in range(face.nspc):
            if self.verbose: print('plotting flx for', k)
            spc = face.namespc[k].decode('utf-8')
            if species is None or spc in species:
                if self.plt_obj_flx.get(k) is None:
                    self.plt_obj_flx[k] = dict((var,self.ax_flx.plot(self.data['time'][0:self.iter_data],self.data[var][0:self.iter_data,k],label='{} {}'.format(var, spc))) for var in self.plot_flx_list)
                    self.ax_flx.legend()
                    if self.plot_flx_xlim == []:
                        self.plot_flx_xlim = [0,self.time_max]
                    self.ax_flx.set_xlim(self.plot_flx_xlim)
                    self.ax_flx.set_ylim(self.plot_flx_ylim)   
                else:
                    for var in self.plot_flx_list:
                        self.plt_obj_flx[k][var][0].set_xdata(self.data['time'][0:self.iter_data])
                        self.plt_obj_flx[k][var][0].set_ydata(self.data[var][0:self.iter_data,k])

                    

    def plot_live(self, species=None):

        if self.liveplot and self.data_collected:
                self.plot_flx(species)
                self.plot_dens(species)
                self.ax_flx.figure.canvas.draw()
                self.ax_flx.figure.canvas.flush_events()
                time.sleep(0.1)
        
            