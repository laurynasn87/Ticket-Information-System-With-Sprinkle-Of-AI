import os
import threading
from multiprocessing import freeze_support
from flask_caching import Cache
from flask_httpauth import HTTPTokenAuth
import TicketComparisonAi
from flask import Flask, request, abort, jsonify
import config
from flask_cors import CORS
Controller = Flask(__name__)
if __name__ == '__main__':
    freeze_support()
CORS(Controller)
Controller.config['CORS_HEADERS'] = 'Content-Type'
Controller.config.from_mapping(config.Cache_Config)
cache = Cache(Controller)
auth = HTTPTokenAuth(scheme='Bearer')
from DataAccess import TicketDataAccess, UserDataAccess, OrganizationDataAccess
import json
from Services import ConfigService, FireStore
import Models.TrainedModel
import Tools.Tools as Tools
Database_Service: FireStore = FireStore.FireStoreService()
SettingData = ConfigService.ConfigService(Database_Service)
TicketData: TicketDataAccess = TicketDataAccess.TicketDataAccess(Database_Service,SettingData)
OrganizationData: OrganizationDataAccess = OrganizationDataAccess.OrganizationDataAccess(Database_Service)
UserData: UserDataAccess = UserDataAccess.UserDataAccess(Database_Service)
TicketAi = TicketComparisonAi.TicketComparisonAi(TicketData.GetTicketsMergedWithComments(),SettingData,TicketData.OrganizationsList,TicketData.UsersList, Database_Service)

@auth.verify_token
def verify_token(token):
    if token != "":
        uid = Database_Service.Verify_Token(token) 
        if  uid == None:
            return jsonify({"message":"Authorization failed"}),403
        return uid

@Controller.route('/Tickets', methods=['GET'])
@auth.login_required
@cache.cached(timeout=100, query_string=True)
def Get_All_Tickets():
    filter = request.args.get('filter', default='', type=str)
    Tickets = TicketData.GetTickets(filter)
    Tickets = Handle_Main_Params(Tickets)

    return ObjectToJson(Tickets)

@Controller.route('/Organizations', methods=['GET'])
@auth.login_required
@cache.cached(timeout=100, query_string=True)
def Get_All_Organizations():
    filter = request.args.get('filter', default='', type=str)
    orgs = OrganizationData.Calculate_Custom_Fields(OrganizationData.Get_Organizations(filter),TicketData.GetOnlyTickets())
    orgs = Handle_Main_Params(orgs)

    return ObjectToJson(orgs)

@Controller.route('/Users', methods=['GET'])
@auth.login_required
@cache.cached(timeout=100,query_string=True)
def Get_All_Users():
    filter = request.args.get('filter', default='', type=str)
    usrs = UserData.Calculate_Custom_Fields(UserData.Get_Users(filter,TicketData.OrganizationsList,TicketData.GroupsList),TicketData.GetOnlyTickets())
    usrs = Handle_Main_Params(usrs)


    return ObjectToJson(usrs)

@Controller.route('/Users/<id>', methods=['GET'])
@auth.login_required
@cache.cached(timeout=100,query_string=True)
def Get_User_By_Id(id:int):
    user = UserData.Get_User_By_Id(id)
    if user != {}:
        user.Resolve_Id_Fields(TicketData.OrganizationsList,TicketData.GroupsList)
        user = UserData.Calculate_Custom_Fields_For_User(user, TicketData.GetOnlyTickets())
    return ObjectToJson(user)

@Controller.route('/Organizations/<id>', methods=['GET'])
@auth.login_required
@cache.cached(timeout=100,query_string=True)
def Get_Organization_By_Id(id:int):
    org = OrganizationData.Get_Organization_By_Id(id)
    if org != {}:
        org.Resolve_Id_Fields(TicketData.GroupsList)
        org = OrganizationData.Calculate_Custom_Fields_For_Organization(org,TicketData.GetOnlyTickets())
    return ObjectToJson(org)

@Controller.route('/Tickets/<id>', methods=['GET'])
@auth.login_required
def Get_Ticket_By_Id(id:int):
    ticket = TicketData.Get_Ticket_By_Id(int(id))
    return ObjectToJson(ticket)

@Controller.route('/Tickets/UpdateComments/<id>', methods=['PUT'])
@auth.login_required
def Update_Ticket_Comments(id):
    if TicketData.Update_Ticket_Comments(int(id)):
        ticket = TicketData.Get_Ticket_By_Id(id)
        return ObjectToJson(ticket)
    else:
        abort(400)


@Controller.route('/Tickets/Update/<id>', methods=['POST'])
@auth.login_required
def UpdateTicket(id:int):
    data = request.json.get('data')
    result = TicketData.UpdateTicket(id,data)
    if result:
        TicketAi.TicketData =  TicketData.GetTicketsMergedWithComments()
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/Tickets/Delete/<id>', methods=['POST'])
@auth.login_required
def DeleteTicket(id:int):
    result = TicketData.DeleteTicket(id)
    if result:
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/Tickets/Create', methods=['POST'])
@auth.login_required
def Create_Ticket():
    Name = request.json.get('name')
    Description = request.json.get('description')
    Priority = request.json.get('priority')
    SubType = request.json.get('subtype')
    Organisation = request.json.get('organization')
    User = request.json.get('user')
    Caller = request.json.get('caller')
    success, message = TicketData.Create_Ticket(Name,Description,Priority,SubType,Organisation,User,Caller)
    if success:
        ticket_id = message.split('/')
        ticket_id = ticket_id[len(ticket_id)-1]
        ticket_id = int(ticket_id)
        TicketMap = next((ticketmap for ticketmap in TicketData.TicketDataMap if ticketmap["Ticket"].id == ticket_id),{})
        if TicketMap != {}:
            TicketAi.Add_New_Ticket(TicketMap)
            TicketAi.TicketData =  TicketData.GetTicketsMergedWithComments()
        cache.clear()
        return {"url": message} 
    else:
        abort(400, {'message': message})

@Controller.route('/TicketAi/<id>', methods=['GET'])
@auth.login_required
def Get_Closest_Tickets_by_Id(id:int):
    results  = {}
    outdated = TicketAi.Is_Model_Outdated()
    if outdated:
        TicketAi.Initate_model_creation(TicketData.GetTicketsMergedWithComments())
    results["Closest_Main_Data"]=TicketAi.Find_Most_Similar_Ticket(int(id),Models.TrainedModel.TrainedModels.Model_Types.Main_Data_Model)
    if not outdated and TicketAi.Is_Model_Outdated(Models.TrainedModel.TrainedModels.Model_Types.Full_Data_Model):
        TicketAi.Initate_model_creation(TicketData.GetTicketsMergedWithComments())
    results["Closest_Full_Data"]=TicketAi.Find_Most_Similar_Ticket(int(id),Models.TrainedModel.TrainedModels.Model_Types.Full_Data_Model)
    if ("Closest_Main_Data" in results and "Closest_Full_Data" in results and  results["Closest_Full_Data"] != None and  results["Closest_Main_Data"] != None):
        results["Most_Experience_User"]=TicketAi.Find_Best_Asignee(results["Closest_Main_Data"]+results["Closest_Full_Data"],TicketData.UsersList)

    return ObjectToJson(results)

@Controller.route('/TicketAiByOrg/<id>', methods=['GET'])
@auth.login_required
def Get_Closest_Tickets_by_Id_Within_Organization(id:int):
    results  = {}
    if TicketAi.Is_Ticket_Organization_Model_Outdated(int(id),TicketData.GetOnlyTickets()):
        TicketAi.Initiate_model_creation_Organization(int(id),TicketData.GetTicketsMergedWithComments())
    results["Closest_Main_Data"]=TicketAi.Find_Most_Similar_Ticket(int(id),Models.TrainedModel.TrainedModels.Model_Types.Main_Data_Model,True)

    return ObjectToJson(results)

@Controller.route('/TicketAi', methods=['GET'])
@auth.login_required
def Get_All_Ai():
    temp =[]
    mode = SettingData.Get_Setting_By_Name("mode", True)
    for model in TicketAi.Ticket_Models:
        if  model.Ai_Model_Type == mode:
            temp.append({"Name":model.Type,"Coherence":model.Coherence,"Organization":next((org for org in TicketData.OrganizationsList if org.id == model.Organization_id),model.Organization_id),"TicketCount": str(len(model.Corpus)),"TopicCount": model.Get_Topic_Count()})
    return ObjectToJson(temp)

@Controller.route('/Tiles', methods=['PUT'])
@auth.login_required
def Get_Tiles():
    userId: int =request.json.get('userId')
    requester: bool = request.json.get("requester")
    return ObjectToJson(TicketData.Get_Tiles(userId,requester))

@Controller.route('/Settings', methods=['GET'])
@auth.login_required
def Get_All_Settings():
    Force_Refresh = request.args.get('refresh', default=True, type=bool)
    if Force_Refresh:
        SettingData.Get_All_Settings()
    return ObjectToJson(SettingData.All_Settings)

@Controller.route('/Settings/<Name>', methods=['GET'])
@auth.login_required
def Get_Settings_By_Name(Name:str):
    Setting = SettingData.Get_Setting_By_Name(Name)
    return ObjectToJson(Setting)

@Controller.route('/Settings', methods=['PUT'])
@auth.login_required
def Set_Settings_By_Name():
    if not request.json:
        abort(400)
    if 'Name' not in request.json and 'Value' not in request.json:
        abort(400)
    Name: str =request.json.get('Name')
    Value: str = request.json.get('Value')

    if SettingData.Set_Setting_By_Name(Name,Value):
        t1 = threading.Thread(target=BespokeSettingChangeEvents, args=[Name])
        t1.setDaemon(True)
        t1.start()   
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/SystemAccounts')
@auth.login_required
def Get_System_Accounts():
    database_system_accounts = [account.to_dict() for account in Database_Service.GetData(SettingData.Get_Database_Name("Accounts"))]
    system_Accounts = Tools.Tools.Merge_FireAuth_Users_With_Database_Users(Database_Service.Get_Users(),database_system_accounts)
    system_Accounts = Tools.Tools.Filter_Columns(system_Accounts,SettingData.Get_Setting_By_Name("Default_System_Users_Columns",True))
    return ObjectToJson(system_Accounts)


@Controller.route('/SystemAccounts', methods=['POST'])
@auth.login_required
def Create_System_Account():
    if not request.json:
        abort(400)
    if 'email' not in request.json and 'password' not in request.json and 'password' not in request.json and 'role' not in request.json and 'displayName' not in request.json:
        abort(400)
    email = request.json.get('email')
    password = request.json.get('password')
    role = request.json.get('role')
    displayName = request.json.get('displayName')
    userId = request.json.get('userid')
    organizationId = request.json.get('organization')
    sucess, err =  Database_Service.Create_User(email,password,displayName,role,organizationId,userId)
    if sucess:
        return jsonify(success=True)
    else:
        abort(400, {'message': err})

@Controller.route('/SystemAccounts/<uid>', methods=['POST'])
@auth.login_required
def Edit_System_Account(uid):
    if not request.json:
        abort(400)
    if 'role' not in request.json and 'displayName' not in request.json:
        abort(400)
    
    role = request.json.get('role')
    displayName = request.json.get('displayName')
    userId = request.json.get('userid')
    org = request.json.get('organization')
    if Database_Service.Update_User(uid,displayName,role,userId,org):
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/SystemAccounts/<uid>', methods=['DELETE'])
@auth.login_required
def Delete_System_Account(uid):
    if Database_Service.Delete_User(uid):
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/SystemAccounts/DisableUser/<uid>', methods=['PUT'])
@auth.login_required
def Disable_System_Account(uid):
    if Database_Service.Set_User_Disable(uid):
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/SystemAccounts/EnableUser/<uid>', methods=['PUT'])
@auth.login_required
def Enable_System_Account(uid):
    if Database_Service.Set_User_Disable(uid,False):
        return jsonify(success=True)
    else:
        abort(400)

@Controller.route('/RefreshZendeskData')
@auth.login_required
def Refresh_Zendesk_Data():
    TicketData.GetTickets(Bypass_Time_Count = True)
    return jsonify(success=True)

@Controller.route('/ClearCache')
@auth.login_required
def ClearCache():
    cache.clear()
    return jsonify(success=True)

@Controller.route('/Tickets/WriteResponse/<uid>', methods=['POST'])
@auth.login_required
def Write_Response(uid):
    if not request.json:
        abort(400)
    if 'message' not in request.json and 'public' not in request.json:
        abort(400)
    Message = request.json.get('message')
    Public = request.json.get('public')
    Caller = request.json.get('caller')
    Requester = request.json.get('requester')
    if TicketData.Write_Response(int(uid),Message,Public,Caller,Requester):
        return jsonify(success=True)
    else:
        abort(400)

def ObjectToJson(Object):
    return (json.dumps(Object, default = lambda Element: Element.__dict__))
def BespokeSettingChangeEvents(SettingName):
    if SettingName == "mode" or SettingName == "Topics_Count":
        print("Initiated new Ai instance")
        TicketAi.__init__(TicketData.GetTicketsMergedWithComments(),SettingData,TicketData.OrganizationsList,TicketData.UsersList,Database_Service)
        print("Initiated new Ai instance - Done")



def Handle_Main_Params(data):
    page = request.args.get('page', default=1, type=int)
    OrderField = request.args.get('orderby', default='', type=str)
    Ascending = request.args.get('asc', default='true', type=str)
    Ascending = True if (Ascending == 'true') else False
    additional_Filters = request.args.get('additionalfilters', default='', type=str)

    if (additional_Filters != ''):
        data = Tools.Tools.Handel_Additional_Filters(data,additional_Filters)
    if OrderField != '':
        data = Tools.Tools.Sort_List(data, OrderField, Ascending)
    if page > 0:
        data = Tools.Tools.Get_Page(data, page, SettingData.Get_Setting_By_Name("RecordsPerPage",True))

    return data

