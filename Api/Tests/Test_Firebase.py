import pytest

from Services import FireStore
from Models import ConditionModel
Database_Service: FireStore = FireStore.FireStoreService()

def  test_Multiple_Instances_Creation():
    Database_Service2: FireStore = FireStore.FireStoreService()
    assert True

def  test_GetData():
   
    assert len([1 for row in Database_Service.GetData("test")]) > 0

def  test_GetDataByDocumentId():
    assert Database_Service.GetDataByDocumentId("test","1").exists

def  test_GetDataWithConditions():
    condit = ConditionModel.ConditionModel("test","==","2")
    assert len([1 for row in Database_Service.GetDataWithConditions("test",[condit])]) == 1

def  test_Add_Document():
    Database_Service.Add_Document({"test":"5"},"test","Dco6")
    condit = ConditionModel.ConditionModel("test","==","5")
    assert len([1 for row in Database_Service.GetDataWithConditions("test",[condit])]) == 1
    Database_Service.Delete_Document("test","Dco6")

def  test_Delete_Document():
    Database_Service.Add_Document({"test":"6"},"test","TestDoc6")
    condit = ConditionModel.ConditionModel("test","==","6")
    Database_Service.Delete_Document("test","TestDoc6")
    assert len([1 for row in Database_Service.GetDataWithConditions("test",[condit])]) == 0

def  test_Get_Users():
    assert len(Database_Service.Get_Users()) > 0

def  test_Batch_Add_Document():
    data = [{"test":"7"},{"test":"8"}]
    Database_Service.Batch_Add_Document(data,"test","test")

    assert Database_Service.GetDataByDocumentId("test","8").exists and Database_Service.GetDataByDocumentId("test","7").exists
    Database_Service.Delete_Document("test","7")
    Database_Service.Delete_Document("test","8")
    
