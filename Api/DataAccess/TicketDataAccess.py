import datetime
import json
import multiprocessing
import os
import re
from copy import copy, deepcopy
import threading
from flask import config
import numpy as np
from numpy import number
import numpy
import pandas
import requests
male_Names = np.loadtxt("data/nltk/male.txt", dtype=str, usecols=0)
female_Names = np.loadtxt("data/nltk/female.txt", dtype=str, usecols=0)
stopwords = np.loadtxt("data/nltk/english.txt", dtype=str, usecols=0)
import Models.CommentModel
import Models.ConditionModel as ConditionModel
import Models.GroupModel
import Models.MetricsModel
import Models.OrganizationModel
import Models.TicketModel as Ticket
import Models.UserModel 
import Services.ZendeskService as ZendeskService
import Services.ConfigService as ConfigService
import config as cfg
class TicketDataAccess:
    # np array naudojamas siam kintamajam del jo mazo resursu naudojimo (palyginus su list)
    TicketDataMap=[]
    UsersList=[]
    OrganizationsList=[]
    GroupsList=[]
    FieldMap=[]
    ZendeskService: ZendeskService
    FireStore= {}
    Stop_Words = []
    configService:ConfigService = {}
    DataRetrieved = {}
    def __init__(self, FireStoreService,ConfigSvc = {}):
        self.FireStore = FireStoreService
        if ConfigSvc == {}:
            self.configService = ConfigService.ConfigService(FireStoreService)
        else:
            self.configService = ConfigSvc
        self.ZendeskService = ZendeskService.ZendeskService(self.configService)
        self.Load_data()
        if cfg.GoogleCloud:
            self.SaveData()
        self.DataRetrieved = datetime.datetime.now()

    def Load_data(self):
        self.Set_data(self.Get_Database_Tickets(),
                      self.Get_Reference_Data(self.configService.Get_Database_Name("Comments")),
                      self.Get_Reference_Data(self.configService.Get_Database_Name("Metrics")))
        self.UsersList = numpy.array(self.Get_Reference_Data(self.configService.Get_Database_Name("Users")))
        self.OrganizationsList = self.Get_Reference_Data(self.configService.Get_Database_Name("Organizations"))
        self.GroupsList = self.Get_Reference_Data(self.configService.Get_Database_Name("Groups"))
        self.FieldMap = self.Get_Reference_Data(self.configService.Get_Database_Name("FieldMap"))

    def TicketDataRefresh(self):
        time_diff = {}
        DataUpdateTimer = self.configService.Get_Setting_By_Name("DataUpdateTimer",True)
        if DataUpdateTimer == None:
            DataUpdateTimer = 10
        if (self.DataRetrieved != {}):
            time_diff = datetime.datetime.now() - self.DataRetrieved
        if self.DataRetrieved == {} or bool(time_diff.seconds / 3600 >= DataUpdateTimer):
            self.DataRetrieved = datetime.datetime.now()
            self.Set_data(self.Get_Database_Tickets(),
                self.Get_Reference_Data(self.configService.Get_Database_Name("Comments")),
                self.Get_Reference_Data(self.configService.Get_Database_Name("Metrics")))
        
    def Set_data(self,TicketList,CommentList,MetricList):
        self.TicketDataMap = numpy.array([])
        temp = []
        for ticket in TicketList:
            metric = next((metric for metric in MetricList if metric.ticket_id == ticket.id),{})
            comment = next((comment for comment in CommentList if comment["Ticket_Id"] == ticket.id),{})
            temp.append({"Ticket": ticket,"Comment":comment,"Metric":metric})
        self.TicketDataMap = numpy.array(temp)

    def Get_Reference_Data(self,collection_name):
        result: list = []
        ResultsJson = self.FireStore.GetData(collection_name)
        for singular_Result in ResultsJson:
            if (collection_name == self.configService.Get_Database_Name("Users")):
                result.append(Models.UserModel.User.from_dict(singular_Result.to_dict()))
            elif (collection_name == self.configService.Get_Database_Name("Organizations")):
                result.append(Models.OrganizationModel.Organization.from_dict(singular_Result.to_dict()))
            elif (collection_name == self.configService.Get_Database_Name("Groups")):
                result.append(Models.GroupModel.Group.from_dict(singular_Result.to_dict()))
            elif (collection_name == self.configService.Get_Database_Name("Metrics")):
                result.append(Models.MetricsModel.Metrics.from_dict(singular_Result.to_dict()))
            elif (collection_name == self.configService.Get_Database_Name("Comments")):
                dict = singular_Result.to_dict()
                Comments = []
                if "data" in dict:
                    for record in dict["data"]:
                        Comments.append(Models.CommentModel.Comment.from_dict(record))
                    dict["data"] = Comments
                    result.append(dict)
            elif (collection_name == self.configService.Get_Database_Name("FieldMap")):
                result.append(singular_Result.to_dict())
        return result

    def Get_Database_Tickets(self):
        tickets = self.FireStore.GetData(self.configService.Get_Database_Name("Tickets"))
        fields = self.FireStore.GetData(self.configService.Get_Database_Name("Fields"))
        fields = numpy.array([field.to_dict() for field in fields])
        Ticket_List = numpy.array(Ticket.Ticket.JsonToTicketList(tickets,True))
        for ticket in Ticket_List:
            ticket.fields = [field for field in fields if "ticket_id" in field and field["ticket_id"] == ticket.id]
            [field.pop("ticket_id",None) for field in ticket.fields]

        return Ticket_List
    def GetOnlyTickets(self):
        self.TicketDataRefresh()
        if cfg.GoogleCloud == True:
            self.LoadData()
        return [ticket["Ticket"] for ticket in deepcopy(self.TicketDataMap)]

    def GetTicketsMergedWithComments(self):
        self.TicketDataRefresh()
        if cfg.GoogleCloud == True:
            self.LoadData() 
        ticketsmap = deepcopy(self.TicketDataMap)
        return [self.Resolve_Comments(ticket["Ticket"],False,ticket) for ticket in ticketsmap]

    def GetTickets(self, Filter: str = '', Bypass_Time_Count: bool = False):
        self.TicketDataRefresh()
        if self.ZendeskService.is_Time_For_Update() or Bypass_Time_Count:
            t1 = threading.Thread(target=self.initiate_Date_Update, args=[Bypass_Time_Count])
            t1.setDaemon(True)
            t1.start()
        if cfg.GoogleCloud == True:
            self.LoadData()
        Tickets_Short_Info =[]
        for ticket in self.TicketDataMap:
            if Filter != '':
              if not re.search(Filter, ticket["Ticket"].subject, re.IGNORECASE) and not re.search(Filter, str(ticket["Ticket"].id), re.IGNORECASE):
                  continue
            temp_ticket = deepcopy(ticket["Ticket"])
            temp_ticket.MapCustomFields(self.FieldMap)
            if (ticket["Comment"] != {}):
                setattr(temp_ticket, "comments", deepcopy(ticket["Comment"]["data"]))
            new_Ticket = self.Filter_Not_Default_Fields(temp_ticket)
            new_Ticket.Resolve_Id_Fields(self.UsersList,self.OrganizationsList,self.GroupsList)
            Tickets_Short_Info.append(new_Ticket)
        return Tickets_Short_Info
    
    def initiate_Date_Update(self,Bypass_Time_Count: bool):
        if self.Data_Update(Bypass_Time_Count):
            self.Load_data()

    
    def Filter_Not_Default_Fields(self,Ticket_To_Filter):
        Filtered_Ticket = Ticket.Ticket(Ticket_To_Filter.id)
        for default_column in self.configService.Get_Setting_By_Name("Default_Ticket_Columns",True):
            if re.search('fields', default_column, re.IGNORECASE):
                setattr(Filtered_Ticket, default_column.split('.')[1],
                        Ticket_To_Filter.Get_Field_By_Name(default_column.split('.')[1]))
            else:
                setattr(Filtered_Ticket, default_column, getattr(Ticket_To_Filter, default_column))
        return Filtered_Ticket

    def Data_Update(self,Bypass_Time_Count: bool = False):
        data_updated: bool = False
        if (Bypass_Time_Count) or self.configService.Get_Setting_By_Name("UpdateFromZendesk",True):
            data_updated = self.ZendeskService.init_Data_Sync(self.GetOnlyTickets())
            if data_updated:
                print("Zendesk Data update - Secondary data check")
                if self.ZendeskService.Secondary_Data_Sync_Check((self.ZendeskService.Tickets_To_Insert),self.UsersList,"assignee_id","id"):
                    self.Refresh_Secondary_Data("Users","Users",'users')
                    print("Zendesk Data update - Users update")
                if self.ZendeskService.Secondary_Data_Sync_Check((self.ZendeskService.Tickets_To_Insert),self.UsersList, "organization_id", "id"):
                    self.Refresh_Secondary_Data("Organizations","Organizations","organizations")
                    print("Zendesk Data update - Organizations update")
                if self.ZendeskService.Secondary_Data_Sync_Check(self.OrganizationsList,self.GroupsList, "group_id", "id"):
                    self.Refresh_Secondary_Data("Groups","Groups","groups")
                    print("Zendesk Data update - Groups update")
                print("Zendesk Data update - Inserting new tickets")
                self.Create_Update_Tickets(self.ZendeskService.Tickets_To_Insert)
                print("Zendesk Data update - Comments Update")
                self.Update_Comments(self.ZendeskService.Tickets_To_Insert)
                print("Zendesk Data update - Metrics Update")
                self.Update_Metrics(self.ZendeskService.Tickets_To_Insert)
                print("Zendesk Data update - Done")
        return data_updated

    def Update_Comments(self,TicketList):
        results = self.ZendeskService.Get_Comments(TicketList)
        temp = []
        if len(results)>0:
            for result in results:
                Comments = []
                for comment in result["data"]:
                    Comments.append(Models.CommentModel.Comment.from_dict(comment).__dict__)
                query= {
                'Ticket_Id': result["Ticket_Id"],
                'data': Comments
                }
                temp.append(query)
        self.FireStore.Batch_Add_Document(temp, self.configService.Get_Database_Name('Comments'),"Ticket_Id")

    def Update_Ticket_Comments(self,Ticket_id:int):
        try:
            ticket = next((ticket["Ticket"] for ticket in self.TicketDataMap if ticket["Ticket"].id == Ticket_id),{})
            Ticket_list: list = []
            Ticket_list.append(ticket)
            self.Update_Comments(Ticket_list)
            self.Load_data()

            return True
        except:
            return False

    def Update_Metrics(self,TicketList):
        temp = []
        for ticket in TicketList:
            parameter = {"Ticket_Id": ticket.id}
            result = self.ZendeskService.Get_ZendeskData(cfg.ZendeskSource["Metrics"],"ticket_metric",parameter)
            if len(result) > 0:
                new_Metric = Models.MetricsModel.Metrics.from_dict(result[0])
                temp.append(new_Metric.__dict__)
                
        if len(temp)>0:
            self.FireStore.Batch_Add_Document(temp, self.configService.Get_Database_Name('Metrics'),"ticket_id")

    def Refresh_Secondary_Data(self,collection_name,endpoint_name,data_name):
        if self.configService.Get_Setting_By_Name("UpdateFromZendesk",True):
            ResultList: list = []
            Results = self.ZendeskService.Get_ZendeskData(cfg.ZendeskSource[endpoint_name] ,data_name)
            for i in Results:
                if collection_name == 'Users':
                    new_usr:Models.UserModel.User = Models.UserModel.User.from_dict(i)
                    self.FireStore.Add_Document(new_usr.Query_For_Database_Tickets(),self.configService.Get_Database_Name(collection_name),str(new_usr.id))
                if collection_name == 'Organizations':
                    new_org:Models.OrganizationModel.Organization = Models.OrganizationModel.Organization.from_dict(i)
                    self.FireStore.Add_Document(new_org.Query_For_Database_Tickets(),self.configService.Get_Database_Name(collection_name),str(new_org.id))
                if collection_name == 'Groups':
                    new_grp:Models.GroupModel.Group = Models.GroupModel.Group.from_dict(i)
                    self.FireStore.Add_Document(new_grp.Query_For_Database_Tickets(),self.configService.Get_Database_Name(collection_name),str(new_grp.id))


    def Get_Ticket_By_Id(self,id:int,Bypass_Time_Count: bool = False ):
        if self.ZendeskService.is_Time_For_Update():
            t1 = threading.Thread(target=self.initiate_Date_Update, args=[Bypass_Time_Count])
            t1.setDaemon(True)
            t1.start()
        if not isinstance(id,int):
            id = int(id)
        ticket = {}
        Conditions = []
        Ticket_condition: ConditionModel.ConditionModel = ConditionModel.ConditionModel("id", "==", id)
        Conditions.append(Ticket_condition)
        results = self.FireStore.GetDataWithConditions(self.configService.Get_Database_Name("Tickets"),Conditions)
        for result in results:
            ticket = Ticket.Ticket.Json_to_ticket(result.to_dict())
            ticket.fields = deepcopy([ticket["Ticket"].fields for ticket in self.TicketDataMap if ticket["Ticket"].id == id])
            if len(ticket.fields) > 0:
                ticket.fields = ticket.fields[0]
            self.Resolve_Comments(ticket,True)
            ticket.Resolve_Id_Fields(self.UsersList, self.OrganizationsList, self.GroupsList)
            ticket.MapCustomFields(self.FieldMap)
            for field in ticket.fields:
                setattr(ticket,field["name"],field["value"])
            metrics = next((met for met in self.TicketDataMap if met["Metric"] != {} and met["Metric"].ticket_id  == ticket.id),{})
            if metrics != {}:
                metrics = metrics["Metric"]
                ticket = {**ticket.__dict__,**metrics.__dict__}

        if ticket == {}:
            temp_list = self.TicketDataMap.tolist()
            idx = next((map for map in self.TicketDataMap if map["Ticket"].id == id),{})
            idx = temp_list.index(idx) if idx in temp_list else -1
            if idx != -1:
                self.TicketDataMap = np.delete(self.TicketDataMap, idx)
        return ticket

    def Resolve_Comments(self, ticket, Resolve_Id_Fields = False,FullTicketMap={}):
        if FullTicketMap != {}:
            Ticket_Info = FullTicketMap
        else:
            Ticket_Info = next((resolved_ticket for resolved_ticket in self.TicketDataMap if resolved_ticket["Ticket"].id == ticket.id),{})
        if Ticket_Info != {}:
            if Ticket_Info["Comment"] != {} and Ticket_Info["Comment"] != []:
                setattr(ticket, "comments", deepcopy(Ticket_Info["Comment"]["data"]))
                if Resolve_Id_Fields:
                    ticket.comments = Models.CommentModel.Comment.Resolve_Assignee(ticket.comments, self.UsersList)

        return ticket

    def Create_Update_Tickets(self, Tickets:list):
        self.FireStore.Batch_Add_Document([ticket.Query_For_Database_Tickets() for ticket in Tickets], self.configService.Get_Database_Name('Tickets'),"id")
        for ticket in Tickets:
            for field in ticket.fields:
                self.FireStore.Add_Document(ticket.Query_For_Database_Fields(field), self.configService.Get_Database_Name("Fields"),str(ticket.id) + "-" + str(field['id']))

    #Worst function you've seen, I know...
    #Due to deadlines, was forced to cut some corners and save time
    def Get_Tiles(self, userId:number = 0,requester=False):
        records_counts=self.configService.Get_Setting_By_Name("Tile_Lines",True)
        Tickets = self.GetOnlyTickets()
        for ticket in Tickets:
            ticket.MapCustomFields(self.FieldMap)
            ticket.Resolve_Id_Fields(self.UsersList, self.OrganizationsList, self.GroupsList)

        newest =  deepcopy(sorted(Tickets, key=lambda x: datetime.datetime.strptime(x.created_at, '%Y-%m-%dT%H:%M:%SZ'), reverse=True))
        if userId > 0:
            if requester:
                my_recently_active = deepcopy(sorted(Tickets, key=lambda x: datetime.datetime.strptime(x.updated_at, '%Y-%m-%dT%H:%M:%SZ'), reverse=True))
                my_recently_active =  [ticket for ticket in my_recently_active if ticket.requester_id == userId or (isinstance(ticket.requester_id,dict)and 'id' in ticket.requester_id and ticket.requester_id["id"] == userId) ][:records_counts]
                my_newest =  [ticket for ticket in newest if ticket.requester_id == userId or (isinstance(ticket.requester_id,dict)and 'id' in ticket.requester_id and ticket.requester_id["id"] == userId)][:records_counts]
            else:
                my_recently_active = deepcopy(sorted(Tickets, key=lambda x: datetime.datetime.strptime(x.updated_at, '%Y-%m-%dT%H:%M:%SZ'), reverse=True))
                my_recently_active =  [ticket for ticket in my_recently_active if ticket.assignee_id == userId or (isinstance(ticket.assignee_id,dict) and 'id' in ticket.assignee_id and ticket.assignee_id["id"] == userId)][:records_counts]
                my_newest =  [ticket for ticket in newest if ticket.assignee_id == userId or (isinstance(ticket.assignee_id,dict) and 'id' in ticket.assignee_id and ticket.assignee_id["id"] == userId)][:records_counts] 
        awaiting_assigning = [ticket for ticket in newest if ticket.assignee_id == 0 or ticket.assignee_id  is None][:records_counts]
        newest = newest[:records_counts]
        awaiting_response = []
        for ticket in Tickets:
            if (len(ticket.fields) > 0):
               for field in ticket.fields:
                    if (field["name"] == "Ticket Status" and field["value"] == "12._client_response_received" and not requester):
                        awaiting_response.append(ticket)
                    if (field["name"] == "Ticket Status" and field["value"] == "awaiting_customer" and requester):  
                        awaiting_response.append(ticket)
        awaiting_response = sorted(awaiting_response, key=lambda x: datetime.datetime.strptime(x.updated_at, '%Y-%m-%dT%H:%M:%SZ'), reverse=False)
        if userId > 0:
            if requester:
                my_awaiting_response = [ticket for ticket in awaiting_response if ticket.requester_id == userId or (isinstance(ticket.requester_id,dict)and 'id' in ticket.requester_id and ticket.requester_id["id"] == userId)][:records_counts]
            else:
                my_awaiting_response = [ticket for ticket in awaiting_response if ticket.assignee_id == userId or (isinstance(ticket.assignee_id,dict) and 'id' in ticket.assignee_id and ticket.assignee_id["id"] == userId)][:records_counts]
        
        awaiting_response=awaiting_response[:records_counts]
        recently_closed = deepcopy(sorted(Tickets, key=lambda x: datetime.datetime.strptime(x.updated_at, '%Y-%m-%dT%H:%M:%SZ'), reverse=True))
        if userId > 0:
            if requester:
                my_recently_closed = [ticket for ticket in recently_closed if ticket.requester_id == userId or (isinstance(ticket.requester_id,dict)and 'id' in ticket.requester_id and ticket.requester_id["id"] == userId) and ticket.status == 'closed'] [:records_counts]
            else:
                my_recently_closed = [ticket for ticket in recently_closed if ticket.assignee_id == userId or (isinstance(ticket.assignee_id,dict) and 'id' in ticket.assignee_id and ticket.assignee_id["id"] == userId) and ticket.status == 'closed'] [:records_counts]
    
        recently_closed = [ticket for ticket in recently_closed if ticket.status == 'closed'][:records_counts]
        
        if userId == 0:
            return {"awaiting_assigning":awaiting_assigning, "recently_closed":recently_closed,"awaiting_response":awaiting_response,"newest":newest}
        if userId > 0:
            return {"awaiting_assigning":awaiting_assigning, "recently_closed":recently_closed,"awaiting_response":awaiting_response,"newest":newest,"my_recently_closed":my_recently_closed,"my_awaiting_response":my_awaiting_response,"my_newest":my_newest,"my_recently_active":my_recently_active}

    def Write_Response(self,Ticket_id: int, Message: str, is_Public = True, Caller = 0, Requester = False):
        if Caller == None or Caller == 0:
            if (self.configService.Get_Setting_By_Name("Allow_Comments",True)):
                if self.ZendeskService.Add_Comment(Ticket_id,Message,is_Public):
                    return True
                else:
                    return False
            else:
                return False
        else:
            Caller = next((user for user in self.UsersList if user.id == Caller),{})
            this_ticket_map = next((ticket_map for ticket_map in self.TicketDataMap if ticket_map["Ticket"].id == Ticket_id),{})
            if Caller == {} or this_ticket_map == {}:
                return 
            ticket_comments = this_ticket_map["Comment"]
            if ticket_comments == {}:
                ticket_comments = {"Ticket_Id":Ticket_id, "data":[]}
                initial_comm = Models.CommentModel.Comment()
                initial_comm.id = 0
                initial_comm.plain_body = this_ticket_map["Ticket"].description
                initial_comm.body = this_ticket_map["Ticket"].description
                initial_comm.type ="Comment"
                initial_comm.created_at = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
                initial_comm.public = True
                initial_comm.attachments =[]
                initial_comm.author_id = this_ticket_map["Ticket"].requester_id
                ticket_comments["data"].append(initial_comm)
                
                this_ticket_map["Ticket"].status = "open"
                
                
            new_comment = Models.CommentModel.Comment()
            new_comment.id = 0
            new_comment.plain_body = Message
            new_comment.body = Message
            new_comment.type ="Comment"
            new_comment.created_at = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
            new_comment.public = is_Public
            new_comment.attachments =[]
            new_comment.author_id = Caller.id
            
            ticket_comments["data"].append(new_comment)
            

            Comments = []
            for comment in ticket_comments["data"]:
                Comments.append(comment.__dict__)
            query= {
            'Ticket_Id': Ticket_id,
            'data': Comments
            }
            this_ticket_map["Ticket"].updated_at = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
            if Requester:
                field_update = {"id":114103095933,"value":"12._client_response_received","ticket_id":Ticket_id}
            else:
                field_update = {"id":114103095933,"value":"awaiting_customer","ticket_id":Ticket_id}
                
            for field in this_ticket_map["Ticket"].fields:
                if field["id"] == 114103095933:
                    field["value"] = field_update["value"]
            self.FireStore.Add_Document(field_update, self.configService.Get_Database_Name('Fields'),str(Ticket_id) + "-" + str(field_update["id"]))
            self.FireStore.Add_Document(this_ticket_map["Ticket"].Query_For_Database_Tickets(), self.configService.Get_Database_Name('Tickets'),str(Ticket_id))
            self.FireStore.Add_Document(query, self.configService.Get_Database_Name('Comments'),str(Ticket_id))
            this_ticket_map["Comment"] = ticket_comments
            return True


            

    
    def Create_Ticket(self,Name,Decription,Priority,SubType,Organization,Requester_User,Caller):
        id = 0
        i = 0
        try:
            while id == 0:
                i = i +1
                if next((ticket for ticket in self.TicketDataMap if ticket["Ticket"].id == i),{}) == {}:
                    id = i
            database_system_accounts = [account.to_dict() for account in self.FireStore.GetData(self.configService.Get_Database_Name("Accounts"))]
            this_user = next((usr for usr in database_system_accounts if "uid" in usr and usr["uid"] == Caller),"")
            new_Ticket:Ticket.Ticket= Ticket.Ticket(id)
            new_Ticket.priority = Priority
            new_Ticket.subject = Name
            new_Ticket.raw_subject = Name
            new_Ticket.description = Decription
            new_Ticket.created_at = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
            new_Ticket.updated_at = new_Ticket.created_at
            new_Ticket.type = "incident"
            new_Ticket.url = cfg.Front_End_Path + "Ticket/" + str(id)
            new_Ticket.status = "new"
            new_Ticket.organization_id = next((org.id for org in self.OrganizationsList if org.name == Organization),"")
            new_Ticket.group_id = next((org.group_id for org in self.OrganizationsList if org.name == Organization),"")
            new_Ticket.requester_id = next((user.id for user in self.UsersList if user.name == Requester_User),"")
            if new_Ticket.requester_id == "":
                new_User:Models.UserModel.User = Models.UserModel.User()
                i = 0
                user_id =0
                while user_id==0:
                    i = i +1
                    if next((user for user in self.UsersList if user.id == i),{}) == {}:
                        user_id = i
                new_User.id = user_id
                new_User.name = Requester_User
                new_User.organization_id = new_Ticket.organization_id
                new_User.verified = True
                new_User.active = True
                new_User.created_at = new_Ticket.created_at
                new_User.updated_at = new_Ticket.created_at
                new_User.default_group_id =  new_Ticket.group_id
        
                if this_user["role"] == "Requester":
                    new_User.role = "end-user"
                else:
                    new_User.role = "admin"
                new_User.email = this_user["email"]
                self.FireStore.Add_Document(new_User.Query_For_Database_Tickets(),self.configService.Get_Database_Name("Users"),str(new_User.id))
                self.UsersList.append(new_User)
                new_Ticket.requester_id = user_id
                new_Ticket.assignee_id = 0
                this_user["userId"] =  user_id
                self.FireStore.Update_User(this_user["uid"],this_user["displayName"],this_user["role"],this_user["userId"], this_user["organization"])

        
            new_Ticket.tags = ["TIS"]
            Fields =[]
            Fields.append({"id":114097135214,"value":"","ticket_id":id})
            Fields.append({"id":38966609,"value":SubType,"ticket_id":id})
            Fields.append({"id":114103050694,"value":"to_be_determined","ticket_id":id})
            Fields.append({"id":114103095933,"value":"new","ticket_id":id})
            for Field in Fields:
                self.FireStore.Add_Document(Field, self.configService.Get_Database_Name('Fields'),str(id) + "-" + str(Field["id"]))
                del Field['ticket_id']
            self.FireStore.Add_Document(new_Ticket.Query_For_Database_Tickets(), self.configService.Get_Database_Name('Tickets'),str(new_Ticket.id))
            new_Ticket.fields = Fields
            temp_list = self.TicketDataMap.tolist()
            temp_list.append({"Ticket":new_Ticket,"Comment":{},"Metric":{}})
            self.TicketDataMap=numpy.array(temp_list)
            if cfg.GoogleCloud == True:
                self.SaveData()
        except Exception as e:
            return False, "There has been an error"
        return True, new_Ticket.url

    def UpdateTicket(self,id,data):
        id = int(id)
        TicketMap = next((ticket for ticket in self.TicketDataMap if ticket["Ticket"].id == id),{})
        data_seperated = data.split(";")
        if TicketMap == {}:
            return False
        for change in data_seperated:
            if (len(change.split("=")) == 2):
                field = change.split("=")[0]
                value = change.split("=")[1]
            
                value, result = self.intTryParse(value)
                corresponding_Field = next((fieldmap for fieldmap in self.FieldMap if fieldmap["Name"]==field),{})
                if corresponding_Field != {}:
                    field = "field." + field
                
                if field in Models.MetricsModel.Metrics.__dict__:
                    field = "metric." + field

                if "field." in field:
                    field_id = next((map for map in self.FieldMap if map["Name"] == field.split(".")[1]),{})
                    if (field_id != {}):
                        field_id=field_id["Id"]
                        field_existing = next((field for field in TicketMap["Ticket"].fields if field["id"] == field_id),{})
                        if (field_existing):
                            index = TicketMap["Ticket"].fields.index(field_existing)
                            if index > 0:
                                del TicketMap["Ticket"].fields[index]
                            field_existing["value"] = value
                            self.FireStore.Add_Document({"id":field_id,"value":value,"ticket_id":id}, self.configService.Get_Database_Name('Fields'),str(id) + "-" + str(field_id))
                            TicketMap["Ticket"].fields.append(field_existing)

                elif "metric." in field:
                    if (TicketMap["Metric"] == {}):
                        new_Metric = Models.MetricsModel.Metrics()
                        new_Metric.ticket_id = id
                        TicketMap["Metric"] = new_Metric
                    setattr(TicketMap["Metric"], field.split(".")[1], value)
                else:
                    if isinstance(value,str) and "||" in value:
                        value = value.split("||")
                    setattr(TicketMap["Ticket"], field, value)
                
        TicketMap["Ticket"].updated_at = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.FireStore.Add_Document(TicketMap["Ticket"].Query_For_Database_Tickets(), self.configService.Get_Database_Name('Tickets'),str(TicketMap["Ticket"].id))
        if cfg.GoogleCloud == True:
            self.SaveData()
        if TicketMap["Metric"] != {}:
            self.FireStore.Add_Document(TicketMap["Metric"].__dict__, self.configService.Get_Database_Name('Metrics'),str(TicketMap["Ticket"].id))
        return True

    def DeleteTicket(self,id):
        if isinstance(id,str):
            id = int(id)
        ticket_map = next((tick_map for tick_map in self.TicketDataMap if tick_map["Ticket"].id == id),{})
        if ticket_map == {}:
            return False
        self.FireStore.Delete_Document(self.configService.Get_Database_Name('Tickets'),str(id))
        if ticket_map["Metric"] != {}:
            self.FireStore.Delete_Document(self.configService.Get_Database_Name('Metrics'), str(id))
        if ticket_map["Comment"] != {}:
            self.FireStore.Delete_Document(self.configService.Get_Database_Name('Metrics'), str(id))
        for field in ticket_map["Ticket"].fields:
            self.FireStore.Delete_Document(self.configService.Get_Database_Name('Fields'), str(id) + "-" + str(field["id"]))
        temp_list = self.TicketDataMap.tolist()
        idx = temp_list.index(ticket_map)
        self.TicketDataMap = np.delete(self.TicketDataMap, idx)
        if cfg.GoogleCloud == True:
            self.SaveData()
        return True
        
    def SaveData(self):
        np.save("/tmp/Data.npy",self.TicketDataMap)
        print("Saved data")


    def LoadData(self):
        if os.path.exists("/tmp/Data.npy"):
            self.TicketDataMap = np.load("/tmp/Data.npy", allow_pickle=True)
            print("Loaded data")
        
    def intTryParse(self,value):
        try:
            return int(value), True
        except ValueError:
            return value, False


        






