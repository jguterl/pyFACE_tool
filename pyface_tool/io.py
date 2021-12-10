#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 11:12:49 2021

@author: guterlj
"""
import os
from pyface_tool import utils, monitor
import numpy as np
from pyface import face
class DataFACE():
    def __init__(self, *args,  **kwargs):
        
            
        self.data = {}
        self.niter_collect = 100
        self.dt_collect = -1
        self.iter_collect = 0
        self.time_collect = 0
        self.iter_data = 0
        self.data_collected = False
        self.vec_bulk =  ['dens']
        self.storage = 10000
        
        
    def init_data(self):
        for k in self.vec_bulk:
            self.data[k] = np.zeros((self.storage,face.ngrd+1,face.nspc))
        self.vec_srf =  ['Gdes_l','Gdes_r','dsrfl','dsrfr','inflx','int_dens','int_dsrf']
        for k in self.vec_srf:
            self.data[k] = np.zeros((self.storage,face.nspc))
        self.scalars = ['time','iter','dt_face']
        for k in self.scalars:
            self.data[k] = np.zeros((self.storage))        
    def data_collector(self):
        self.data_collected = False
        if self.dt_collect>=0 and self.niter_collect>=0:
            raise ValueError('self.dt_collect>=0 and self.niter_collect>=0')
        if self.dt_collect>=0:
            self.time_collect += face.dt_face
            if self.time_collect>=self.dt_collect or self.iter == 1 or self.iter >= self.iter_max or self.time >= self.time_max:
               self.collect_data()
               self.time_collect = 0.0
               self.data_collected = True
              
        if self.niter_collect>=0:
            self.iter_collect += 1
            if self.iter_collect>=self.niter_collect or self.iter == 1  or self.iter >= self.iter_max or self.time >= self.time_max:
               self.collect_data()
               self.iter_collect = 0
               self.data_collected = True
            
    
    def collect_data(self):
        if self.verbose: print('Collecting data ...', self.iter_collect,self.niter_collect )
        for k in self.scalars:
            self.data[k][self.iter_data] = getattr(self,k)
        for k in self.vec_srf:
            if k == 'int_dens':
                vec = monitor.integrales_dens() 
            elif k == 'int_dsrf':
                vec = monitor.integrales_dsrf() 
            else:
                
                vec = getattr(self,k)
            if len(vec.shape) > 1:
                vec = vec[-1,:]
            
            self.data[k][self.iter_data,:] = vec
        for k in self.vec_bulk:
            self.data[k][self.iter_data,:,:] = getattr(self,k)[-1,:,:]
        self.iter_data = self.iter_data + 1 
        if self.data.get('x') is None:
            self.data['x'] = getattr(face,'x') 
        
    def save_data(self,filename=''):
        if filename == '':
            filename = 'default,npy'
        else:
            pass
        
class ObjFACE():
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
     
    def upload_dic_face(self,dic, enforce=True):
        for k,v in dic.items():
            if hasattr(face,k):
                setattr(face,k,v)
            else:
                msg = 'Cannot find entry {} in the package face'.format(k)
                if enforce:
                    raise KeyError(msg)
                else:
                    raise Warning(msg)
                
    def import_face_package(self):
        for v in face.varlist():
            setattr(self.__class__,v,property(self.getter(v), self.setter(v), self.deleter(),face.getvardoc(v)))
            
    @staticmethod
    def getter(varname):
        def getfaceobj(self):
            return getattr(face,varname)
        return getfaceobj
    
    @staticmethod
    def setter(varname):
        def setfaceobj(self,vv):
            return setattr(face,varname,vv)
        return setfaceobj
    
    @staticmethod
    def deleter():
        def setfaceobj(self):
            pass
        return setfaceobj
    
    
class IOFACE(ObjFACE,DataFACE):
    def __init__(self,*args,**kwargs):
         print('init IOFACE')
         super().__init__(*args,**kwargs)
         self.directory = '.'
    def print(self,string):
        print(' [FACE] {}'.format(string))
    @staticmethod
    def dump_face_dic():
        dic={}
        for var in face.varlist():
            dic[var] = getattr(face,var)
        return dic
    
    def dump_state(self):
        dic={}
        for var in dir(self):
            dic[var] = getattr(self,var)
        return dic
    

    def upload_dic(self,dic, enforce=True):
        for k,v in dic.items():
            if hasattr(self,k):
                setattr(self,k,v)
            else:
                msg = 'Cannot find entry ["{}"] in this object'.format(k)
                if enforce:
                    raise KeyError(msg)
                else:
                    raise Warning(msg)

        
    
    
    def save_state(self, filename, dataset='all', overwrite=False):
        if dataset == 'all':
            self.write_state(filename,self.__dict__,  overwrite)
        elif dataset == 'face':
            self.write_state(filename,self.dump_face_dic(),  overwrite)
        elif dataset == 'data':
            self.save_data(filename, ext, overwrite)
        else:
            raise KeyError('dataset must be: [all] | face | data ')
        
    def read_state(self,filename):
        if not os.path.exists(filename):
            raise FileNotFoundError('Cannot read {}'.format(filename))
        else:
            ext = os.path.splitext(filename)[1]
            if self.verbose: print('Extension: {} for {}'.format(ext,filename))
            if ext =='.json':
                return utils.read_jsonfile(filename)
            elif ext == '.npy':
                return utils.read_npyfile(filename)
            else:
                ValueError('Cannot read file with extension {}.'.format(ext))
            
    
    def write_state(self,filename, dic, overwrite=True):

        ext = os.path.splitext(filename)[1]
        if os.path.dirname(filename) == ' ':
            filename = os.path.join(self.directory,filename)
            
        if utils.checkfile(filename, overwrite):
            self.print('Writing data into {} ...'.format(filename))
            if ext =='.json':
                utils.write_jsonfile(filename,dic)
            elif ext == '.npy':
                utils.write_npyfile(filename,dic)
            else:
                raise ValueError('unknown format')
        else:
            self.print('Skipping writing data into {} ...'.format(filename))
            
            
        


        


    
    

