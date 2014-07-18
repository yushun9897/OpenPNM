"""
module __OpenPNMbase__: contains OpenPNM base classes
=====================================================

"""
import sys, os, string, random, time
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, parent_dir)
import OpenPNM
import scipy as sp
import scipy.constants
import logging as _logging


# set up logging to file - see previous section for more details
_logging.basicConfig(level=_logging.ERROR,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    )
                    
class Base(object):
    r"""
    .. class:: `OpenPNM.Utilities.OpenPNMbase` -- Base class for OpenPNM
    
    
    Base class with a few bells and whistles. Mainly output on screen, logging
    and pickling. This is the class from which all other classes should inherit.
    
    Parameters
    ----------    
    
    loglevel : int
        Level of the logger (10=Debug, 20=INFO, 30=Warning, 40=Error, 50=Critical)
    loggername : string
        Name of the logger. The default is the name of the class.

    Attributes
    ----------
    
    self._logger : _logging.logger
       This class defines a logger for the class and all classes inheriting from it.
       it supports all settings of the standard logger. It still needs some fine 
       tuning.
           
       ======== =====   =============================================================
       Level    Value   When it is used
       ======== =====   =============================================================
       DEBUG    10      Detailed information, at diagnostic stage
       INFO     20      Confirmation that things are working as expected.
       WARNING  30      An indication that something unexpected happened.
       ERROR    40      Due to a more serious problem, program might still execute.
       CRITICAL 50      A serious error, might compromise program execution
       ======== =====   =============================================================
       
    """
    _name = None
    def __init__(self,**kwargs):
        super(Base,self).__init__()
        if 'loggername' in kwargs.keys():
            self._logger = _logging.getLogger(kwargs['loggername'])
        else:
            self._logger = _logging.getLogger(self.__class__.__name__)
        if 'loglevel' in kwargs.keys():
            loglevel = kwargs['loglevel']
            self.set_loglevel(loglevel)
        else:
            loglevel = 30
            self.set_loglevel(loglevel)
        
    def __repr__(self):
        return '<%s.%s object at %s>' % (
        self.__class__.__module__,
        self.__class__.__name__,
        hex(id(self)))
              
    def set_loglevel(self,level=50):
        r"""
        Sets the effective log level for this class
        
        Parameters
        ----------
        level : int
            Level above which messages should be logged.
        """
        self._logger.setLevel(level)
        self._logger.debug("Changed log level")
            
    def find_object(self,obj_name='',obj_type=''):
        r'''
        Find objects associated with a given network model by name or type
        
        Parameters
        ----------
        obj_name : string
           Name of sought object
        
        Returns
        -------
        OpenPNM object or list of objects
        
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> geom = pn.add_geometry(name='geo1')
        >>> temp = pn.find_object(obj_name='geo1')
        >>> temp.name
        'geo1'
        >>> temp = pn.find_object(obj_type='Geometry')
        >>> temp[0].name
        'geo1'
        
        '''
        if self.__class__.__module__.split('.')[1] == 'Network':
            net = self
        else:
            net = self._net
        
        if obj_name != '':
            objs = []
            if self.name == obj_name:
                return self
            for geom in net._geometries:
                if geom.name == obj_name:
                    return geom
            for fluid in net._fluids:
                if fluid.name == obj_name:
                    return fluid
            for phys in net._physics:
                if phys.name == obj_name:
                    return phys
            return objs # Return empty list if none found
        elif obj_type != '':
            objs = []
            for geom in net._geometries:
                if geom.__class__.__module__.split('.')[1] == obj_type:
                    objs.append(geom)
            for phys in net._physics:
                if phys.__class__.__module__.split('.')[1] == obj_type:
                    objs.append(phys)
            for fluid in net._fluids:
                if fluid.__class__.__module__.split('.')[1] == obj_type:
                    objs.append(fluid)
            return objs
            
    def delete_object(self,obj=None,obj_name=''):
        r'''
        Remove specific objects from a network model
        
        Parameters
        ----------
        name : string
            The name of the object to delete
            
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> geom = pn.add_geometry(name='geo')
        >>> geom.name
        'geo'
        >>> pn.delete_object(obj_name='geo')
        >>> pn.find_object(obj_name='geo')
        []
        
        '''
        if self.__class__.__module__.split('.')[1] == 'Network':
            net = self
        else:
            net = self._net
        if obj_name != '':
            obj = self.find_object(obj_name=obj_name)
        #Get object type, so we know where to delete from
        obj_type = obj.__class__.__module__.split('.')[1]
        if obj_type == 'Geometry':  # Remove geometry from network
            net._geometries.remove(obj)
        elif obj_type == 'Fluids':
            for fluid in net._fluids:
                if fluid == obj:
                    for physics in fluid._physics:
                        physics._fluid = None
                        net._physics.remove(physics)
                    net._fluids.remove(obj)
                    del fluid
        elif obj_type == 'Physics':
            for physics in net._physics:
                if physics == obj:
                    for fluid in physics._fluid:
                        fluid._physics.remove(obj)
                    net._physcis.remove(obj)
                    del fluid
                    
    def _set_name(self,name):
#        obj_type = self.__module__.split('.')[1]
        if name == None:
            name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5))
            name = self.__module__.split('.')[-1].strip('__') + '_' + name
#        if obj_type == 'Geometry':
#            if self._name != None:
#                self._logger.error('Geometry objects cannot be renamed')
#                raise Exception('Geometry objects cannot be renamed')  
#        objs = self.find_object(obj_type=obj_type)
#        for item in objs:
#            if item.name == name:
#                self._logger.error('A '+obj_type+' object with that name already exists')
#                raise Exception('A '+obj_type+' object with that name already exists')
        self._name = name
    
    def _get_name(self):
        return self._name
        
    name = property(_get_name,_set_name)
            
    def save_object(self,filename):
        r'''
        '''
        temp = filename.split('.')[0]
        temp = temp+'.npz'
        sp.savez_compressed(temp,**self)
        
            
if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)


























