class FACEParams(dict):
   def __init__(self,name, *arg,**kw):
      super(FACEParams, self).__init__(*arg, **kw)
      self.name = name
   def __repr__(self):
       return '{}:{}'.format('FACEParams',self.name)
   def collect_attrs(self,obj):
       for a in get_varlist(obj):
           self[a] = getattr(obj,a)
   def show(self):
       for k,v in self.items():
           print('{}:{}'.format(k,v))
           
           
      
      
      
def get_name_obj(obj):
    return repr(pyface.input).split('instance at')[0].strip('<')
          
def get_varlist(obj):
    return getattr(obj,'varlist')()
    
def set_defaults_params(nspc):
    pass
    