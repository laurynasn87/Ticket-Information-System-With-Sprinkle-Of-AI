import pytest

from DataAccess import TicketDataAccess
from Services import FireStore
from Tools.Tools import Tools
Database_Service: FireStore = FireStore.FireStoreService()
TicketData: TicketDataAccess = TicketDataAccess.TicketDataAccess(Database_Service)

def  test_Get_Page():
    results = TicketData.GetOnlyTickets()
    paged = Tools.Get_Page(results,2,1)
    assert len(paged["results"]) == 1 and paged["page"] == 2 and paged["page_size"] == 1

def  test_Get_Attribute():
    Obj = {"Test":12}
    assert Tools.Get_Attribute(Obj,"Test") == 12

def  test_Filter_Columns():
    Obj = [{"Test":12, "Test1":4},{"Test":12, "Test1":4}]
    coll = ["Test"]
    assert "Test1" not in (Tools.Filter_Columns(Obj,coll)[0])

def  test_Sort_List():
    Obj = [{"Test":12, "Test1":4},{"Test":12, "Test1":1},{"Test":12, "Test1":55},{"Test":12, "Test1":11}]
    list = Tools.Sort_List(Obj,"Test1",False)
    assert list[0]["Test1"] >  list[1]["Test1"]

def  test_is_date():
    assert Tools.is_date("2021-09-21")