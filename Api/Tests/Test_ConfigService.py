import pytest
from Services import ConfigService

from Services import FireStore

Database_Service: FireStore = FireStore.FireStoreService()
cfgs: ConfigService = ConfigService.ConfigService(Database_Service)

def  test_Get_All_Settings():
    assert len(cfgs.Get_All_Settings()) > 0

@pytest.mark.parametrize('settingName',['ChartsConfig','Default_Ticket_Columns','RecordsPerPage',"UpdateFromZendesk"])
def  test_Get_Setting_By_Name(settingName):
    assert cfgs.Get_Setting_By_Name(settingName) is not None

def  test_Get_All_Settings_Value():
    settingname = "Default_Ticket_Columns"
    assert not isinstance(cfgs.Get_Setting_By_Name(settingname,True),str)

def  test_Check_If_Bool():
    assert cfgs.Check_If_Bool("true") and not cfgs.Check_If_Bool("false")

@pytest.mark.parametrize('name',['Tickets','Fields','FieldMap',"Users","Organizations","Groups"])
def  test_Get_Database_Name(name):
    assert cfgs.Get_Database_Name(name) is not ""
