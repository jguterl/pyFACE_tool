#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 16:23:41 2021

@author: guterlj
"""
from pyface_tool import monitor, plot, io, utils
from pyface_tool.plot import PlotFACE
from pyface import face
import os
class RunFACE(monitor.MonitorFace,PlotFACE,io.IOFACE):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        super(monitor.MonitorFace,self).__init__(*args, **kwargs)
        super(PlotFACE,self).__init__(*args, **kwargs)
        
        self.reduce_dt_factor = 10
        self.increase_dt_factor = 10
        self.verbose_run = True
        self.time_start = 0
        self.time_max = 10.0
        self.dt_face_max = 1e15
        self.iter = 0 
        self.time_inputs={}
        self.dt_face_modif=None
        self.iter_max = 1000000
        self.niter_info = 100
        self.verbose = False if kwargs.get('verbose') is None else kwargs.get('verbose')
        self.initial_inventory = 0
        
    def restore(self,filename):
        dic = self.read_state(filename)
        self.setup(**dic)
        
    def setup(self,nspc=1,ngrd=100,ndt=1, enforce=True,  **kwargs):
        face.nspc = nspc
        face.ngrd = ngrd
        face.ndt = ndt
        face.allocate_face()
        self.upload_dic(kwargs, enforce)
        self.import_face_package()
        
    def exec_step(reduce_dt_factor=10.0, max_fail_iter=3, verbose=False):
        from pyface import face
        fail_counter = 0
        state=True
        if verbose: print("Performing FACE step")
        face.do_step(state)
        while not state:
            if fail_counter>max_fail_counter:
                raise ValueError('FACE fails to converge after timestep reduction: dt_face={}'.format(dt_face))
            fail_counter=+1
            print('Reducing time step dt_face:{} -> {}'.format(face.dt_face, face.dt_face/reduce_dt_factor))
            face.dt_face /= self.reduce_dt_factor
            face.do_step(state)
            sys.stdout.flush()
        return state
    
    def init(self):
        face.initialize_wrapper()
        self.iter = 0
        self.init_trace()
        self.initial_inventory = self.make_inventory()
        self.time = 0.0
        self.init_data()
        
   
    def print_info(self, force=False):
        if self.iter%self.niter_info == 0 or self.iter == 0 or force:
            print('iter = {:7d} | time = {:3.2e} | tempL={:3.2e} | dt={:3.1e} | inflx={:3.2e} | Gdes_l={:3.2e} |'.format(self.iter,self.time,self.temp[-1,0],self.dt_face,self.inflx[0],self.Gdes_l[-1,0]))
    def round_dt_face(self):
        if self.time+self.dt_face>self.time_max and self.time_max-self.time>0:
            self.dt_face = self.time_max-self.time
    def apply_time_inputs(self,dic):
        for k,v in dic.items():
            if not hasattr(self,k):
                raise KeyError('Variable "{}" not found in the current object attributes'.format(k))
            else:
                setattr(self,k,v(self.time))
    def apply_dtface_modif(self,f):
        if f is not None:
            return f(self.dt_face,self.time)
        else:
            return self.dt_face
              
    @utils.kwgetter  
    def run(self, **kwargs):
        print(100*'-')
        self.print('Starting run')
        while self.time<self.time_max and self.iter<self.iter_max:
            self.apply_time_inputs(self.time_inputs)
            if self.exec_step():
                self.print_info()
                
                self.update_trace()
                face.time += face.dt_face
                self.iter += 1
                self.data_collector()
                self.plot_live()
                self.dt_face = min(face.compute_dt(),self.dt_face*self.increase_dt_factor)
                self.dt_face = min(self.dt_face,self.dt_face_max)
                self.dt_face = self.apply_dtface_modif(self.dt_face_modif)
                self.round_dt_face()
                
            else:
                print('Failure')
                return
        print('\n')
        print(100*'-')
        self.print('run completed')
        self.print_info(force=True)
        self.particle_conservation()
        print(100*'-')
        print('\n')