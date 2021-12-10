#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 10:07:29 2021

@author: guterlj
"""
import sys
import json
import numpy as np
import os
def kwgetter(func):
      def wrapper(self,*args, **kwargs):
          for k,v in kwargs.items():
              if hasattr(self,k):
                  setattr(self,k,v)
          func(self,*args, **kwargs)
      return wrapper   
  
    
def checkfile(filename, overwrite=False):
    if os.path.exists(filename) and not overwrite:
        return query_yes_no('Do you want to replace {}?'.format(filename))
    else:
        return True 
        
def query_yes_no(question, default="yes"):
        """Ask a yes/no question via input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n") 
                
                
def write_jsonfile(filename,dic):
        with open(filename,'w') as f:
            json.dump(dic,f)
            
def write_npyfile(filename,dic):
        np.save(filename,dic)
   
def read_jsonfile(filename):
        with open(filename,'w') as f:
            return json.read(f)

def read_npyfile(filename):
         return np.load(filename,allow_pickle=True).tolist()