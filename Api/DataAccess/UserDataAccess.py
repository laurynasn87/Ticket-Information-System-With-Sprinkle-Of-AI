import re
from Services import ConfigService

import Models.ConditionModel as ConditionModel
import Models.UserModel


class UserDataAccess:
    FireStore = {}
    Config_Service : ConfigService = {}
    def __init__(self, FireStoreService, ConfigSvc = {}):
        self.FireStore = FireStoreService
        self.FireStore = FireStoreService
        if ConfigSvc == {}:
            self.configService = ConfigService.ConfigService(FireStoreService)
        else:
            self.configService = ConfigService

    def Get_Users(self, Filter: str = '', Zendesk_Organizaitons:list = [],Zendesk_Group:list = []):
        User_List =[]
        ResultsJson = self.FireStore.GetData(self.configService.Get_Database_Name("Users"))
        for singular_Result in ResultsJson:
            usr = Models.UserModel.User.from_dict(singular_Result.to_dict())
            if Filter != '':
                if not re.search(Filter, usr.name, re.IGNORECASE):
                  continue

            New_Usr = Models.UserModel.User()
            for default_column in self.configService.Get_Setting_By_Name("Default_Users_Columns",True):
                setattr(New_Usr,default_column,getattr(usr,default_column))
            if len(Zendesk_Organizaitons) >0 and len(Zendesk_Group) > 0:
                New_Usr.Resolve_Id_Fields(Zendesk_Organizaitons,Zendesk_Group)
            User_List.append(New_Usr)

        return User_List
    def Get_User_By_Id(self,id):
        Conditions = []
        user = {}
        users_condition: ConditionModel.ConditionModel = ConditionModel.ConditionModel("id", "==", int(id))
        Conditions.append(users_condition)
        results = self.FireStore.GetDataWithConditions(self.configService.Get_Database_Name("Users"), Conditions)
        for result in results:
            user = Models.UserModel.User.from_dict(result.to_dict())

        return user

    @staticmethod
    def Calculate_Custom_Fields_For_User(user,Ticket_List=[]):
        Open_Tickets: int = 0
        Raised_Tickets: int = 0;

        #    Awaiting_Response = sum(ticket.organization_id == org.id for ticket in Ticket_List)
        Open_Tickets = sum(ticket.assignee_id == user.id and ticket.status != 'closed' for ticket in Ticket_List)

        setattr(user, 'Custom_Open_Tickets', Open_Tickets)
        setattr(user, 'Custom_Raised_Tickets', Raised_Tickets)

        return user

    @staticmethod
    def Calculate_Custom_Fields(User_List= [],Ticket_List=[]):
        for usr in User_List:
            Open_Tickets: int = 0
            Raised_Tickets: int = 0;

            #    Awaiting_Response = sum(ticket.organization_id == org.id for ticket in Ticket_List)
            Open_Tickets = sum(ticket.assignee_id == usr.id and ticket.status != 'closed' for ticket in Ticket_List)
            Raised_Tickets = sum(ticket.requester_id == usr.id for ticket in Ticket_List)

            setattr(usr, 'Custom_Open_Tickets', Open_Tickets)
            setattr(usr, 'Custom_Raised_Tickets', Raised_Tickets)

        return User_List