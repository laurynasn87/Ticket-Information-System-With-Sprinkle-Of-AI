import ast
from datetime import datetime
import json
from typing import Set
from Models.SystemSettings import Systemsettings
from Services.FireStore import FireStoreService


class ConfigService:
    Database = {}
    Database_Names={
    "Tickets":"Tickets",
    "Fields": "Fields",
    "FieldMap": "Fieldmap",
    "Users":"SystemUser",
    "Organizations":"Organization",
    "Groups":"Groups",
    "Metrics": "TicketMetrics",
    "Comments":"Comments",
    "Settings":"Settings",
    "Accounts":"users"
    }
    Settings = []
    Config_Update_Time =""

    
    def __init__(self, FireStoreService:FireStoreService):
        self.Database = FireStoreService
        self.Settings = self.Get_All_Settings()
    
    def Get_All_Settings(self):
        self.All_Settings=[]
        ResultsJson = self.Database.GetData(self.Database_Names["Settings"])
        for singular_Result in ResultsJson:
            self.All_Settings.append(Systemsettings.from_dict(singular_Result.to_dict()))

        self.Config_Update_Time = datetime.now()
        return self.All_Settings

    def Get_Setting_By_Name(self,Name, return_Value = False):
        if len(self.All_Settings) < 1 or self.is_Config_Too_Old():
            self.Get_All_Settings()

        Setting = next((setting for setting in self.All_Settings if setting.Name == Name),None)
        
        if return_Value and Setting is not None:
            if isinstance(Setting.Value,str) and self.is_json(Setting.Value):
               return json.loads(Setting.Value)
            elif isinstance(Setting.Value,str) and (Setting.Value[0] == '[' and Setting.Value[len(Setting.Value)-1] == ']'):   
                return ast.literal_eval(Setting.Value)
            return self.Check_If_Bool(Setting.Value)
        
        return Setting
    def Check_If_Bool(self, value:str):
        if (value == 'true'):
            return True
        if (value == 'false'):
            return False
        return value

    def is_Config_Too_Old(self):
        if self.Config_Update_Time == "":
            return True
        now = datetime.now()
        minutes_diff = (now - self.Config_Update_Time).total_seconds() / 60.0

        if minutes_diff >=5: 
            return True
        else:
            return False


    def Set_Setting_By_Name(self,Name,Value):
        Result = True
        New_Setting = {"Name":Name, "Value":Value}
        try:
            self.Database.Add_Document(New_Setting,self.Get_Database_Name("Settings"),Name)
        except:
            Result= False

        self.Get_All_Settings()

        return Result
    
    def Get_Database_Name(self,name: str):
        return self.Database_Names.get(name,'')

    def is_json(self,string):
        if ('{' in string and '}' in string) or ('[' in string and ']' in string)  :  
            try:
                json.loads(string)
            except ValueError:
                return False
            return True
        else:
            return False