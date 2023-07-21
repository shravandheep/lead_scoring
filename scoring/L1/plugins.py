import os
import re
import json
from abc import ABC, abstractmethod
from datetime import datetime

class Plugin(ABC):
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def apply(self):
        pass
    
    @abstractmethod
    def get_status(self):
        pass
    
    @abstractmethod
    def get_error(self):
        pass
    

class Split(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
        self._char = kwargs['char'] 
        self._day = kwargs["day"]
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        split_data = str(x).split(self._char) 
        return int(split_data[self._day])
     


class Isweekday(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        dt = datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
        return int(dt.weekday() < 5)
    
    
    
    
class Timediff(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        x = datetime.strptime(x, '%Y-%m-%d')
        current_time = datetime.today()
        
        return (current_time.year - x.year)
    
    
class Weekofmonth(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        x = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        x = x.date().day
        x = x/7 +1
        x = int(x)
        return x
    
    
class Timeofday(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        x = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        self._hour = x.hour
        if 6 <= self._hour < 12:
            self._res = 'Morning'
        elif 12 <= self._hour < 18:
            self._res = 'Afternoon'
        else:
            self._res = 'Evening/Night'
            
        return self._res
    
    
    
class Quarter(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        x = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        return 1+x.month/4
    
    
    
class Createdmonth(Plugin):
    def __init__(self,kwargs):
        self._status = True
        self._error =None
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error

    def apply(self,x):
        x = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        return x.month
            
            
class Substitute(Plugin):
    def __init__(self,kwargs):
#         try:
            self._to = kwargs['to']
            self._from = kwargs['from']
            
            if isinstance(self._from, str): 
                
                _FILE_PATH = os.path.realpath(os.path.dirname(__file__))
                config_path = os.path.join(_FILE_PATH, 'configs')
                subst_path = os.path.join(config_path, self._from)
                
                if os.path.isfile(subst_path):
                    self._data = json.load(open(subst_path))
                else:
                    raise Exception("Config file not found")
                
                assert isinstance(self._from, str),"'from' must be a list of strings: %s "%self._from
                
            else:
                assert isinstance(self._from, list),"'from' must be a list of strings: %s "%self._from
                
            
#             assert type(self._from)==list,"'from' must be a list of strings: %s "%self._from
            assert len(self._from)>0,"Empty 'from' list : %s "%self._from
            assert self._to is not None,"Missing 'to' : %s "%self._to
            assert all([isinstance(k, str) for k in self._from]),"'from' must be a list of strings: %s "%self._from
            self._status = True
            self._error = None
#         except Exception as ex:
#             self._status = False
#             self._error = ex
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error
    
    def apply(self,x):
        if isinstance(self._from, str):
            for self._key, self._value in self._data.items():
                if x in self._value["from"]:
                    self._to = self._value["to"]
                    break
            return self._to 
        else: 
            return self._to if str(x) in self._from else x
    

class Regex(Plugin):   
    def __init__(self,kwargs):
        try:
            self._to = kwargs['to']
            self._from = kwargs['from']
            self._reg_list = list(map(re.compile,self._from))
            assert type(self._from)==list,"'from' must be a list of strings: %s "%self._from
            assert len(self._from)>0,"Empty 'from' list : %s "%self._from
            assert self._to is not None,"Missing 'to' : %s "%self._to
            assert all([type(k)==str for k in self._from]),"'from' must be a list of strings: %s "%self._from
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error
    
    def apply(self,x):
        return self._to if any(regex.match(str(x)) for regex in self._reg_list) else x
    
class Fill_Na(Plugin):
    def __init__(self,kwargs):
        try:
            self._value = kwargs['value']
            self._status = True
            self._error = None
        except Exception as ex:
            self._status = False
            self._error = ex
    
    def get_status(self):
        return self._status
    
    def get_error(self):
        return self._error
        
    def apply(self,x):
        
        #TODO: Rewrite this logic better later
        val = True
        
        if x == "" or x is None:
            val = None
            
        return self._value if val is None else x

    