#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 09:29:09 2021

@author: guterlj
"""
from pyface import face
import numpy as np
class MonitorFace():
    def __init__(self,*args,**kwargs):
        self.trace = {}
    def init_trace(self):
        self.trace = {}
    
        for k in range(face.nspc):
            self.trace[k] = self.init_trace_dic()
    
    def update_trace(self):
        for k in range(face.nspc):
            self.update_trace_dic(self.trace[k],k)
    @staticmethod        
    def make_inventory():
        
        inventory = {}
        for k in range(face.nspc):
            inventory[k] = {}
            inventory[k]['int_dens'] = integrale_dens(k)
            inventory[k]['int_dsrf'] = integrale_dsrf(k)
            inventory[k]['content'] = integrale_dsrf(k) + integrale_dens(k)
            
        return inventory
    
    @staticmethod
    def init_trace_dic():
        trace={}
        trace['inflx'] = 0
        trace['qflx'] = 0
        trace['Q_l'] = 0
        trace['Q_r'] = 0
        trace['Gdes_l'] = 0
        trace['Gdes_r'] = 0 
        return trace
    
    @staticmethod
    def update_trace_dic(trace,k):
            trace['inflx'] += integrale_src(k)*face.dt_face
            trace['qflx'] += face.qflx_in*face.dt_face
            trace['Q_l'] -= face.qflx_in*face.dt_face
            trace['Q_r'] += face.qflx[-1,-1]*face.dt_face
            trace['Gdes_l'] += face.Gdes_l[-1,k]*face.dt_face
            trace['Gdes_r'] += face.Gdes_r[-1,k]*face.dt_face 
            trace['Ges'] =  trace['Gdes_r'] + trace['Gdes_l'] 
            trace['net_inflx'] = trace['inflx'] - trace['Ges'] 
            
    def particle_conservation(self):
        inventory = self.make_inventory()
        lt = ['Gdes_l','Gdes_r','inflx','net_inflx']
        li = ['int_dsrf','int_dens','content']
        ll = lt + li 
        strs = len(ll)*'| {:10s} |'
        strf = len(ll)*'| {:3.1e} |'
        print('')
        print(100*'*')
        print(strs.format(*ll))
        net_content = {}
        net_balance = {}
        for k in range(face.nspc):
            vt = [self.trace[k][l] for l in lt]
            vi = [inventory[k][l] for l in li]
            v = vt + vi
            print(strf.format(*v))
        print(100*'*')
        ll = ['net_content','net_balance','error[%]']
        strs = len(ll)*'| {:10s} |'
        strf = len(ll)*'| {:3.1e} |'
        for k in range(face.nspc):
            if hasattr(self,'initial_inventory'):
                net_content[k] = inventory[k]['content']-self.initial_inventory[k]['content']
            net_balance[k] = net_content[k] - self.trace[k]['net_inflx'] 
            v=  [net_content[k], net_balance[k],(net_content[k]-net_balance[k])/net_balance[k]*100 ]
            print(strf.format(*v))
        print(100*'*')
def integrales_src():
     return np.array([np.sum(face.src[-1,:,k]*face.dx) for k in range(face.nspc)])       
def integrales_srs():
       return np.array([np.sum(face.srs[-1,:,k]*face.dx) for k in range(face.nspc)])
def integrales_srb():
       return np.array([np.sum([np.sum(face.srb[-1,:,k,l]*face.dx) for l in range(face.nspc)]) for k in range(face.nspc)])    
def integrales_dens():
     return np.array([np.trapz(face.dens[-1,:,k],face.x) for k in range(face.nspc)]) 
                  
def integrale_src(k):
    return np.trapz(face.src[-1,:,k],face.x)       
    
def integrale_dens(k):
    return np.trapz(face.dens[-1,:,k],face.x)     

def integrale_dsrf(k):
    int_dsrf=0.0
    if face.left_surface_model_int[k] == face.surf_model_S:
            int_dsrf += face.dsrfl[-1,k]

    if face.right_surface_model_int[k] == face.surf_model_S:
        int_dsrf += face.dsrfr[-1,k]
    return int_dsrf
def integrales_dsrf():
    int_dsrf=np.zeros((face.nspc))
    for k in range(face.nspc):
        if face.left_surface_model_int[k] == face.surf_model_S:
                int_dsrf[k] += face.dsrfl[-1,k]
    
        if face.right_surface_model_int[k] == face.surf_model_S:
            int_dsrf[k] += face.dsrfr[-1,k]
    return int_dsrf   
def integrales_src_profile():
    return np.array([np.sum(face.src_profile[:,k]*face.dx) for k in range(face.nspc)])  
