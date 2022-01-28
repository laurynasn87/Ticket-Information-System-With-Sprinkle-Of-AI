import re
from Models.ConditionModel import ConditionModel

from Services.ConfigService import ConfigService
from Models import OrganizationModel

class OrganizationDataAccess:
    FireStore = {}
    Config_Service:ConfigService = {}
    def __init__(self, FireStoreService, ConfigSvc={}):
        self.FireStore = FireStoreService
        if ConfigSvc == {}:
            self.configService = ConfigService(FireStoreService)
        else:
            self.configService = ConfigService

    def Get_Organizations(self, Filter: str = ''):
        Organization_List =[]
        ResultsJson = self.FireStore.GetData(self.configService.Get_Database_Name("Organizations"))
        for singular_Result in ResultsJson:
            org = OrganizationModel.Organization.from_dict(singular_Result.to_dict())
            if Filter != '':
                if not re.search(Filter, org.name, re.IGNORECASE):
                  continue

            Organization_List.append(org)

        return Organization_List
    @staticmethod
    def Calculate_Custom_Fields_For_Organization(Organization,Ticket_List=[]):
        Open_Tickets: int = 0
        Raised_Tickets: int = 0;

        Raised_Tickets = sum(ticket.organization_id == Organization.id for ticket in Ticket_List)
        Open_Tickets = sum(ticket.organization_id == Organization.id and ticket.status != 'closed' for ticket in Ticket_List)

        setattr(Organization, 'Custom_Open_Tickets', Open_Tickets)
        setattr(Organization, 'Custom_Raised_Tickets', Raised_Tickets)

        return Organization

    def Get_Organization_By_Id(self,id):
        Conditions = []
        org = {}
        if not isinstance(id,int):
            id = int(id)
        users_condition: ConditionModel = ConditionModel("id", "==", id)
        Conditions.append(users_condition)
        results = self.FireStore.GetDataWithConditions(self.configService.Get_Database_Name("Organizations"), Conditions)
        for result in results:
            org = OrganizationModel.Organization.from_dict(result.to_dict())

        return org

    def Calculate_Custom_Fields(self,Organization_List= [],Ticket_List=[]):
        for org in Organization_List:
           Open_Tickets: int = 0
           Raised_Tickets: int = 0;

           Raised_Tickets = sum(ticket.organization_id == org.id for ticket in Ticket_List)
           Open_Tickets = sum(ticket.organization_id == org.id and ticket.status != 'closed' for ticket in Ticket_List)

           setattr(org,'Custom_Open_Tickets', Open_Tickets)
           setattr(org, 'Custom_Raised_Tickets', Raised_Tickets)

        return Organization_List