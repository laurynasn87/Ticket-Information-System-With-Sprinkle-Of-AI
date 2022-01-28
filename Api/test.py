from DataAccess.TicketDataAccess import TicketDataAccess
from Services import FireStore
import Controller
Database_Service: FireStore = FireStore.FireStoreService()
TicketData = TicketDataAccess(Database_Service)
Controller.Get_Tiles()