import pytest

from DataAccess import TicketDataAccess
from Models.TicketModel import Ticket
from Services import FireStore

Database_Service: FireStore = FireStore.FireStoreService()
TicketData = TicketDataAccess.TicketDataAccess(Database_Service)

def test_init():
   assert TicketData.FireStore != {} and TicketData.configService != {} and TicketData.ZendeskService != {}

def test_Load_data():
    assert len(TicketData.TicketDataMap) > 0 and len(TicketData.UsersList) > 0 and len(TicketData.OrganizationsList) > 0 and len(TicketData.FieldMap) > 0 and len(TicketData.GroupsList)

def test_Set_data():
    tickets = [TicketData.TicketDataMap[0]["Ticket"],TicketData.TicketDataMap[1]["Ticket"]]
    comments = [TicketData.TicketDataMap[0]["Comment"],TicketData.TicketDataMap[1]["Comment"]]
    metrics = [TicketData.TicketDataMap[0]["Metric"],TicketData.TicketDataMap[1]["Metric"]]

    TicketData.TicketDataMap = []
    
    TicketData.Set_data(tickets,comments,metrics)

    assert len(TicketData.TicketDataMap) > 0

    TicketDataAccess.__init__("",Database_Service)

@pytest.mark.parametrize('collection_name',['SystemUser','Organization','Fieldmap',"Groups","TicketMetrics","Comments"])
def test_Get_Reference_Data(collection_name):
    results = TicketData.Get_Reference_Data(collection_name)
    assert len(results) > 0

def test_Get_Database_Tickets():
   assert len(TicketData.Get_Database_Tickets()) > 0

def test_GetOnlyTickets():
    results = TicketData.GetOnlyTickets()
    assert isinstance(results[0],Ticket)

def test_GetTicketsMergedWithComments():
    results = TicketData.GetTicketsMergedWithComments()
    assert results[0].comments != None

def test_GetTickets():
    results = TicketData.GetTickets()
    assert len(results) > 0

def test_Get_Ticket_By_Id():
    results = TicketData.Get_Ticket_By_Id(2657)
    assert results != None

def test_Get_Tiles():
    results = TicketData.Get_Tiles()
    assert len(results) > 0  