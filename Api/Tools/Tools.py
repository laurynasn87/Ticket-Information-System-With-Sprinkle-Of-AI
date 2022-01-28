from copy import copy
from typing import List
from dateutil.parser import parse
import numpy

class Tools:
    @staticmethod
    def Get_Page(Records:list,Page:int,Page_size:int):
        data = []
        index = (Page-1) * Page_size
        if len(Records) > index:
            if Page_size < len(Records):
                data = Records[index:index+Page_size]
            else:
                data = Records[index:index+len(Records)]

        return {'results': data,
                'page': Page,
                'page_size': Page_size,
                'total_results':len(Records)}

    @staticmethod
    def Handel_Additional_Filters(Records:list,additional_Filters:str):
        Filters:list = additional_Filters.split(";")
        Records_Filtered =[]
        Conditions = {}
        Records = numpy.array(Records)
        if len(Filters)>0:
            for filter in Filters:
                if ':' not in filter:
                    continue
                field_Name=filter.split(":")[0]
                field_Value=filter.split(":")[1]
                field_Values = field_Value.split(",")

                if len(field_Values) == 0:
                    field_Values.append(field_Value)

                for field in field_Values:
                    if field_Name != '' and field != '':
                        if field_Name in Conditions:
                            Conditions[field_Name].append(field)
                        else:
                            Conditions[field_Name] = [field]
            for record in Records:
                for condition in Conditions:
                    fieldValue = str(Tools.Get_Attribute(record,condition))
                    if fieldValue in Conditions[condition]:
                        Records_Filtered.append(record)
                        break

                             

        return Records_Filtered

    @staticmethod
    def Get_Attribute(object,property_name):
        result = ''
        if ('.' in property_name):
            property_root = property_name.split('.')[0]
            property_name = property_name.split('.')[1]
            if hasattr(object,property_root):
               result = Tools.Get_Attribute(getattr(object,property_root),property_name)
        else:
            if hasattr(object,property_name) or (isinstance(object,dict) and property_name in object):
                if isinstance(object,dict):
                    result = object[property_name]
                else:
                    result = getattr(object,property_name)

        return result

    @staticmethod
    def Merge_FireAuth_Users_With_Database_Users(Fire_Auth_Users, Database_Users):
        merged_users = []
        for user in Fire_Auth_Users:
            new_usr =copy(user)
            database_usr = [db_usr for db_usr in Database_Users if db_usr.get('uid', 'NO KEY') == user.get('localId', 'NO KEY')]
            if len(database_usr) > 0:
                database_usr=database_usr[0]
            if database_usr != []:
                new_usr = {**new_usr, **database_usr}
            merged_users.append(new_usr)

        return merged_users


    @staticmethod
    def Filter_Columns(data:list, columns):
        results = []
        for row in data:
            N_row = {}
            for key, value in row.items():
                if key in columns:
                    N_row[key]=value
            if N_row != {}:
                results.append(N_row)

        return results

    @staticmethod
    def Sort_List(data:list, field_Name:str, ascending:bool):
        data = sorted(data, reverse=not ascending, key=lambda item: Tools.Resolve_Sort_Field(item, field_Name))
        return data
    
    @staticmethod
    def Resolve_Sort_Field(item,field_Name):
        if '.' in field_Name:
            root_var = field_Name.split('.')[0]
            item = getattr(item, root_var)
            field_Name = field_Name.split('.')[1]

        if (type(item) is dict):
           result =  item[field_Name]
        else:
            result = getattr(item, field_Name,"")
        if "at" in field_Name:
            Tools.is_date(result,result)

        if (type(result) is str):
            result= result.lower()
        return result


    @staticmethod
    def is_date(string, fuzzy=False):
        try:
            Parsed = parse(string, fuzzy=fuzzy)
            return True, Parsed

        except ValueError:
            return False, string