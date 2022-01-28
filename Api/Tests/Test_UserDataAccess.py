import pytest

from DataAccess import UserDataAccess
from Services import FireStore

Database_Service: FireStore = FireStore.FireStoreService()
UserData: UserDataAccess = UserDataAccess.UserDataAccess(Database_Service)

def  test_Get_User_By_Id():
    results = UserData.Get_Users()
    assert UserData.Get_User_By_Id(results[0].id) != None

def  test_Get_Users():
    assert len(UserData.Get_Users()) > 0
