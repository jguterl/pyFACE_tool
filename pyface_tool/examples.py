#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 11:53:29 2021

@author: guterlj
"""
# import sys
# from io import StringIO

# old_stdout = sys.stdout
# old_stderr = sys.stderr
# my_stdout = sys.stdout = StringIO()
# my_stderr = sys.stderr = StringIO()
from pyface_tool import *
from pyface import face
from pyface_tool.monitor import *

state=True
face.verbose_compute=True
face.verbose_update_dt = False


face.dt_face = 1e-15
#face.do_step(state)

class ObjFACE():
    def __init__(self):
         pass
    def upload_face_package(self):
        for v in face.varlist():
            setattr(self.__class__,v,property(self.getter(v), self.setter(v), self.deleter(),face.getvardoc(v)))
            
    @staticmethod
    def getter(varname):
        def getfaceobj(self):
            return face.getpyobject(varname)
        return getfaceobj
    
    @staticmethod
    def setter(varname):
        def setfaceobj(self,vv):
            return face.setpyobject(varname,vv)
        return setfaceobj
    
    @staticmethod
    def deleter():
        def setfaceobj(self):
            pass
        return setfaceobj

def kwgetter(func):
      def wrapper(self,*args, **kwargs):
          for k,v in kwargs.items():
              if hasattr(self,k):
                  setattr(self,k,v)
          func(self,*args, **kwargs)
      return wrapper   

class PlotFACE():
    def init_plots(self):
        fig,axes = plt.subplots(2,1)
        self.ax_dens = axes[0]
        self.ax_flx = axes[1]
        self.ax_flx.set_xlabel('time[s]')
        self.ax_flx.set_ylabel('flux [m^-2.s^-1]')
        self.ax_flx.set_xscale('log')
        self.ax_flx.set_yscale('log')
        

    def plot_flx(self):
        if not hasattr(self,'ax_flx'):
            self.init_plots()
        for k in range(self.data_nspc):
            spc = face.namespc[k].decode('utf-8')
            self.pgl = self.ax_flx.plot(self.data['time'][0:self.iter_data],self.data['Gdes_l'][0:self.iter_data,k],label='Gdes_l {}'.format(spc))
            self.pgr = self.ax_flx.plot(self.data['time'][0:self.iter_data],self.data['Gdes_r'][0:self.iter_data,k],label='Gdes_r {}'.format(spc))
            self.pinflx = self.ax_flx.plot(self.data['time'][0:self.iter_data],self.data['inflx'][0:self.iter_data,k],label='influx {}'.format(spc))
                
class DataFace():
    def __init__(self, storage=10000):
        self.data = {}
        self.niter_collect = 100
        self.dt_collect = -1
        self.iter_collect = 0
        self.time_collect = 0
        self.iter_data = 0
        self.vec_bulk =  ['dens']
        for k in self.vec_bulk:
            self.data[k] = np.zeros((storage,face.ngrd+1,face.nspc))
        self.vec_srf =  ['Gdes_l','Gdes_r','dsrfl','dsrfr','inflx','int_dens','int_dsrf']
        for k in self.vec_srf:
            self.data[k] = np.zeros((storage,face.nspc))
        self.scalars = ['time','iter','dt_face']
        for k in self.scalars:
            self.data[k] = np.zeros((storage))
            
    def data_collector(self):
        
        if self.dt_collect>=0 and self.niter_collect>=0:
            raise ValueError('self.dt_collect>=0 and self.niter_collect>=0')
        if self.dt_collect>=0:
            self.time_collect += face.dt_face
            
            if self.time_collect>=self.dt_collect or self.time_collect == 0.0:
               self.collect_data()
               self.time_collect = 0.0
               
        if self.niter_collect>=0:
            self.iter_collect += 1
            if self.iter_collect>=self.niter_collect or self.iter_collect == 0:
               self.collect_data()
               self.iter_collect = 0
        
    
    def collect_data(self):
        self.data_nspc = face.nspc
        for k in self.scalars:
            self.data[k][self.iter_data] = getattr(self,k)
        for k in self.vec_srf:
            if k == 'int_dens':
                vec = integrales_dens() 
            elif k == 'int_dsrf':
                vec = integrales_dsrf() 
            else:
                
                vec = getattr(self,k)
            if len(vec.shape) > 1:
                vec = vec[-1,:]
            
            self.data[k][self.iter_data,:] = vec
        for k in self.vec_bulk:
            self.data[k][self.iter_data,:] = getattr(self,k)[-1,:,:]
        self.iter_data = self.iter_data + 1 
        
class RunFACE(MonitorFace,DataFace,ObjFACE,PlotFACE):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.reduce_dt_factor = 10
        self.increase_dt_factor = 10
        self.verbose_run = True
        self.time_start = 0
        self.time_max = 10.0
        self.iter = 0 
        self.itermax = 1000000
        self.niter_info = 100
        self.setup(**kwargs)
    def setup(self,nspc=1,ngrd=100,order=1):
        face.nspc = nspc
        face.ngrd = ngrd
        face.allocate()
        self.upload_face_package()
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
        return state
    def init(self):
        
        face.initialize_wrapper()
        self.iter = 0
        self.init_trace()
        self.initial_inventory = self.make_inventory()
        self.time = 0.0
        
   
    def print_info(self):
        if self.iter%self.niter_info == 0 or self.iter == 0:
            print('iter = {} | time = {} | tempL={}'.format(self.iter,self.time,self.temp[-1,0]))
        
    @kwgetter  
    def run(self,**kwargs):
        while face.time<self.time_max and self.iter<self.itermax:
            if self.exec_step():
                self.print_info()
                self.data_collector()
                self.update_trace()
                face.time += face.dt_face
                face.dt_face = min(face.compute_dt(),face.dt_face*self.increase_dt_factor)
                self.iter += 1
            else:
                print('Failure')
                return
    

        
#%%
r = RunFACE()
r.init()
face.reduction_factor_dt_spc =0.03
face.temp=800
r.run(itermax=100)
  
r.run(itermax=20000)
r.particle_conservation()      
#r.setup()
    #self.iter = self.
    
    



# def compute_onthefly_inventory:
        
#         ! sum up the outgassing flux left and right over time to estimate the average outgassing flux over the simulation
#         ! end verify if <Gdes_l>\approx Gdes_l(end)
#         real:: int_src,int_dens,int_dsrf,int_des
#         integer k,j
#          if (print_onthefly_inventory) then
#         do k=1,nspc
#             int_src=integrale_src(k)*dt_face
#             int_dens=integrale_dens(k)

#             int_dsrf=0d0
            
#             int_dsrf=dsrfl[ndt,k]+int_dsrf
#             endif

            
#             int_dsrf=dsrfr(ndt,k)+int_dsrf
#             endif

#             int_des=Gdes_l(ndt,k)*dt_face+Gdes_r(ndt,k)*dt_face

#             onthefly_net_int_dens(k)=int_dens-onthefly_int_dens(k)
#             onthefly_net_int_dsrf(k)=int_dsrf-onthefly_int_dsrf(k)
#             onthefly['dens'][k]=int_dens
#             onthefly['src'][k]=int_src
#             onthefly['dsrf'][k]=int_dsrf
#             onthefly['des'][k]=int_des
#         enddo
#         endif
def collect_scalar_species(listdata, dic):
    for var in listdata:
        dic[var][iteration,:] = face.gypyobject(var)[-1,:]
    
# subroutine compute_trace_flux
#     ! sum up the outgassing flux left and right over time to estimate the average outgassing flux over the simulation
#     ! end verify if <Gdes_l>\approx Gdes_l(end)
#     real:: int_src
#     integer k,j

#     do k=1,nspc
#             int_src=integrale_src(k)
            





# sys.stdout = old_stdout
# sys.stderr = old_stderr
# my_stdout.close()
# my_stderr.close()
    
   