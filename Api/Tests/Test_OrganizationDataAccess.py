import pytest

from DataAccess import OrganizationDataAccess
from Services import FireStore

Database_Service: FireStore = FireStore.FireStoreService()
OrganizationData: OrganizationDataAccess = OrganizationDataAccess.OrganizationDataAccess(Database_Service)

def test_Get_Organization_By_Id():
    results = OrganizationData.Get_Organizations()
    assert OrganizationData.Get_Organization_By_Id(results[0].id) != None

def test_Get_Organizations():
    assert len(OrganizationData.Get_Organizations()) > 0
