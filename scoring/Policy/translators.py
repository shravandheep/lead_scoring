import os
import json
import traceback
from copy import deepcopy
import pandas as pd

import scoring.L1.plugins as plugins
from scoring.L1.plugins import Plugin 

_FILE_PATH = os.path.realpath(os.path.dirname(__file__))
age_rating = os.path.join(_FILE_PATH, "age_rating.csv")


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


    def run_translators(self, value, func):
        return func(value)
    
    def is_IEP(row):

        created_date = row['CreatedDate']
        birthdate = row['Birthdate__c']
        if pd.isnull(created_date) or pd.isnull(birthdate):
            return None
        sixty_fifth_birthday = birthdate + pd.DateOffset(years=65)
        three_months_before = sixty_fifth_birthday - pd.DateOffset(months=3)
        three_months_after = sixty_fifth_birthday + pd.DateOffset(months=3)

        if three_months_before <= created_date <= three_months_after:
            return 1
        else:
            return 0


    def is_MSOEP(row):

        created_date = row['CreatedDate']
        birthdate = row['Birthdate__c']
        if pd.isnull(created_date) or pd.isnull(birthdate):
            return None
        sixty_fifth_birthday = birthdate + pd.DateOffset(years=65)
        six_months_before = sixty_fifth_birthday - pd.DateOffset(months=6)
        six_months_after = sixty_fifth_birthday + pd.DateOffset(months=6)
        three_months_after = sixty_fifth_birthday + pd.DateOffset(months=3)
        three_months_before = sixty_fifth_birthday - pd.DateOffset(months=3)

        if six_months_before <= created_date <= six_months_after:
            return 1
        else:
            return 0


    def is_AEP(row):
        created_date = row['CreatedDate']
        if pd.isnull(created_date):
            return None
        if pd.Timestamp(created_date.year, 10, 1) <= created_date <= pd.Timestamp(created_date.year, 12, 7):
            return 1
        else:
            return 0

    def is_MAOEP(row):
        created_date = row['CreatedDate']
        if pd.isnull(created_date):
            return None
        if pd.Timestamp(created_date.year, 1, 1) <= created_date <= pd.Timestamp(created_date.year, 3, 1):
            return 1
        else:
            return 0


    def translate(self, data):
        
        new_data = deepcopy(data)
        
        for key, value in data.items():
            
            if key in self._translators.keys():

                try:
                    new_fields = self._translators[key]['alias']
                    functions = self._translators[key]['function']
                    
                    for (y, func) in zip(new_fields, functions):
                        
                        nv = new_data.get(y)
                        ov = new_data[key]
                        value = nv if nv is not None else ov
                        
                        try:
                            new_data[y] = self.run_translators(value, func)   
                        except:
                            new_data[y] = value

                except Exception as ex:
                    pass
            else:
                pass
            
        new_data = pd.DataFrame(new_data)
        
        new_data['Birthdate__c'] = pd.to_datetime(new_data['Birthdate__c'])
        new_data['CreatedDate'] = pd.to_datetime(new_data['CreatedDate'])
        
        new_data['is_IEP'] = new_data.apply(is_IEP, axis=1)
        new_data['is_AEP'] = new_data.apply(is_AEP, axis=1)
        new_data['is_MAOEP'] = new_data.apply(is_MAOEP, axis=1)
        new_data['is_MSOEP'] = new_data.apply(is_MSOEP, axis=1)
        
        age_rating = pd.read_csv(age_rating)
        new_data = new_data.merge(age_rating, how='left')
        new_data['Community %'] = new_data['Community %'].str.rstrip('%').astype(float)
        
        phone_neu = ['Input Phone1 Number', 'Appended Phones1 Number', 'Appended Phones2 Number', 'Appended Phones3 Number']
        phone_lead = ['MobilePhone']
        email_neu = ['Appended Emails 1 Email Address', 'Appended Emails 2 Email Address', 'Appended Emails 3 Email Address']
        email_lead = ['Email']
        
        new_data['Phones_Neustar'] = new_data.apply(lambda row: [row[column] for column in phone_neu], axis=1)
        new_data['Email_Neustar'] = new_data.apply(lambda row: [row[column] for column in email_neu], axis=1)
        
        new_data['Email_matching'] = new_data.apply(lambda row: self.find_index_in_list(row['Email'], row['Email_Neustar']), axis=1)
        new_data['Phone_matching'] = new_data.apply(lambda row: self.find_index_in_list(row['MobilePhone'], row['Phones_Neustar']), axis=1)
        
        new_data['Email_Match_Score'] = new_data['Email_matching'].apply(self.assign_random_score)
        new_data['Phone_Match_Score'] = new_data['Phone_matching'].apply(self.assign_random_score)
        
        new_data['StateCode_Match'] = int(new_data['StateCode'] == new_data['StateCode'])
        new_data['City_Match'] = int(new_data['City'] == new_data['Appended Addresses1 City'])
        new_data['FirstName_Match'] = int(new_data['FirstName'] == new_data['Individual Name First'])
        new_data['LastName_Match'] = int(new_data['LastName'] == new_data['Individual Name Last'])
        
        new_data.loc[new_data['p'].isin(['medicare', 'medicarefaq', 'brand eip','medicare advantage']), 'campaign_product'] = 'not_medigap'
        new_data.loc[new_data['p'].isin(['medigap']), 'campaign_product'] = 'medigap'
        
        new_data['b'] = 'medigap'
        
        new_data = new_data.to_dict(orient='records')
        
        return new_data
    
    