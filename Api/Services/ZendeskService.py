import datetime
import json
import os

from numpy import number
import numpy
from Services import ConfigService
import time
import Models.TicketModel as Ticket
import config
import requests

from Tools.Tools import Tools


class ZendeskService:
    Updated_On= ''
    Base_Url= ''
    Ticket_Endpoint= ''
    Assignee_Endpoint= ''
    Tickets_To_Insert: list = []
    Config_Service : ConfigService = {}
    ZendeskCredentials = {}

    def __init__(self,CfgService):
        self.configService = CfgService
        ZendeskSource = self.configService.Get_Setting_By_Name("ZendeskSource",True)
        self.Base_Url=ZendeskSource["url"]
        self.Ticketurl = ZendeskSource["ticket_url"]
        self.Updated_On = datetime.datetime.min
        f = open(os.path.abspath(os.curdir) + '/data/ZendeskCredentials.json')
        self.ZendeskCredentials = json.load(f)

    def Get_ZendeskData(self,Zendesk_endpoint:str, data_name:str = '', parameters_Dict = {}):
        Data_List = []
        ZendeskSource = self.configService.Get_Setting_By_Name("ZendeskSource",True)
        if "user" in  self.ZendeskCredentials and "password" in  self.ZendeskCredentials and "url" in ZendeskSource:
            url: str = self.Base_Url + Zendesk_endpoint
            for key in parameters_Dict:
                if ("{" + key + "}") in url:
                 url = url.replace(("{" + key + "}"),str(parameters_Dict[key]))
            resp = None
            while url != '' and url is not None:
                resp = requests.get(url, auth=(self.ZendeskCredentials["user"], self.ZendeskCredentials["password"]))
                if resp.status_code == 200:
                    Dict = resp.json()
                    if (data_name == ''):
                        if isinstance(Dict, dict):
                            Data_List.append(Dict)
                        else:
                            Data_List.extend(Dict)
                    else:
                        if isinstance(Dict[data_name],dict):
                            Data_List.append(Dict[data_name])
                        else:
                            Data_List.extend(Dict[data_name])
                    if "next_page" in Dict:
                        url = Dict["next_page"]
                    else:
                        url = ''
                else:
                     url = ''

        return Data_List
    
    def init_Data_Sync(self,Old_Ticket_List:list):
        data_Changed: bool = False;
        self.Tickets_To_Insert = []
        if self.configService.Get_Setting_By_Name("UpdateFromZendesk",True):
            print("Zendesk Data update - Started")
            self.Updated_On = datetime.datetime.now()
            New_Tickets: list = self.Get_ZendeskData(config.ZendeskSource["ticket_url"],"tickets")
            New_Tickets = [Ticket.Ticket.Json_to_ticket(newTicket) for newTicket in New_Tickets]
            if len(Old_Ticket_List) == 0:
                self.Tickets_To_Create = New_Tickets
                data_Changed = True
            else:
                for ticket in New_Tickets:
                    old_Ticket = next((tickets for tickets in Old_Ticket_List if tickets.id == ticket.id),None)
                    if old_Ticket == None or ticket != old_Ticket:
                        if not data_Changed:
                            data_Changed = True
                        
                        self.Tickets_To_Insert.append(ticket)

        print("Zendesk Data update - Ticket Data Recieved " + str(len(self.Tickets_To_Insert)) )
        return data_Changed

    def Secondary_Data_Sync_Check(self,TicketList:list, data:list, ticket_field_name, secondary_field_name):
        for ticket in TicketList:
            if not any(Tools.Get_Attribute(x,secondary_field_name) == Tools.Get_Attribute(ticket,ticket_field_name) for x in data):
                return True
        return False

    def Get_Comments(self,Ticket_List):
        results = []
        if self.configService.Get_Setting_By_Name("UpdateFromZendesk",True):
            for ticket in Ticket_List:
                params = {}
                params["Ticket_Id"] = ticket.id
                params["data"] = self.Get_ZendeskData(config.ZendeskSource["Comments"],"comments",params)

                results.append(params)
            
        return results


            
    def is_Time_For_Update(self):
        min_time_diff = self.configService.Get_Setting_By_Name("Data_Update_Every_n_Hours",True)
        if min_time_diff == None:
            return False
        time_diff = datetime.datetime.now() - self.Updated_On
        return (bool(time_diff.seconds / 3600 >= min_time_diff))

    def Add_Comment(self,id:int, body:str, is_public = True):
        if (self.configService.Get_Setting_By_Name("Allow_Comments",True)):
            url = config.ZendeskSource["url"] + "tickets/"+ id +".json?"
            ticket_Data = {"ticket": {"comment": { "body": body, "public": is_public }}}
            resp = requests.post(url, auth=(self.ZendeskCredentials["user"], self.ZendeskCredentials["password"]), data=ticket_Data) 
            if resp.status_code == 200:
                return True
            else:
                return False
        else:
            return False
