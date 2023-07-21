import os
import json
import traceback
from copy import deepcopy

import scoring.L1.plugins as plugins
from scoring.L1.plugins import Plugin 


class Translator(object):
    __instance = None

    @classmethod
    def get_instance(cls):
        return cls.__instance

    def __init__(self, config_file):
        
        if self.__instance is not None:
            raise Exception("data transformations service is a singleton, use `get_instance` method instead")
            
        assert os.path.exists(config_file), "Config file not found: %s" % config_file
        
        self.confg = json.load(open(config_file, "r"))
        self._translators = {}
        
        for key in self.confg:
            
            self._translators[key] = dict() 
            self._translators[key]['function'] = list()
            self._translators[key]['alias'] = list()
            
            for op in self.confg[key]:
                
                
                assert isinstance(op['apply'], str), "'plugin' must be a string: %s : %s" % (key, op)
                assert issubclass(getattr(plugins, op['apply'].title()), Plugin), "%s is not a valid plugin: %s : %s" % (op['plugin'], key, op)
                
                plugn_cls = getattr(plugins, op['apply'].title())(op['kwargs'])
                assert plugn_cls.get_status(), "Plugin Error: %s : %s : %s" % (key, op, plugn_cls.get_error())
                
                func = plugn_cls.apply
                                
                if "alias" in op:
                    self._translators[key]['apply_on'] = key
                    self._translators[key]['alias'].append(op["alias"])
                    self._translators[key]['function'].append(func)
                    
                else:
                    self._translators[key]['apply_on'] = key
                    self._translators[key]['alias'].append(key)
                    self._translators[key]['function'].append(func)
                    
        ## HACK : This is a singleton class but we're removing this constraint for a specific usecase
        ## This should be handled differently in the future
        # Translator.__instance = self


    def run_translators(self, value, func):
        return func(value)


    def translate(self, data):
        
        new_data = deepcopy(data)
        
        for key, value in data.items():
            
            if key in self._translators.keys():

                try:
                    new_fields = self._translators[key]['alias']
                    functions = self._translators[key]['function']
                    
                    for (y, func) in zip(new_fields, functions):
                            
                        
                        
                        if new_data.get(y) is not None:
                            value = new_data[y]
                        else:
                            value = new_data[key]
                        
                        try:
                            new_data[y] = self.run_translators(value, func)   
                        except:
                            new_data[y] = value

                except Exception as ex:
                    pass
            else:
                pass
            
        return new_data
    
    