import datetime
import json

import Models.GroupModel
import Models.OrganizationModel
import Models.UserModel
from Tools.Tools import Tools


class Ticket:
    id:int = 0
    url: str = ''
    created_at: datetime = datetime.datetime.now()
    updated_at: datetime = datetime.datetime.now()
    type: str = ''
    subject: str = ''
    raw_subject: str = ''
    description: str = ''
    priority: str = ''
    status: str = ''
    requester_id = 0
    submitter_id = 0
    assignee_id = 0
    group_id = 0
    organization_id = 0
    Status_Reason: str = ''
    comments: list = []
    follower_ids: list = []
    collaborator_ids: list = []
    tags: list = []
    fields: list = []

    def __init__(self, id: int):
        self.id = id

    def __init__(self, input):
        if type(input) is str:
            self.Json_to_ticket(input)
        if type(input) is int:
            self.id = input

    def __str__(self):
        return f"Ticket ID: {self.id} Ticket Description: {self.description}"

    @staticmethod
    def Json_to_ticket(Json):
        NewTicket:Ticket = Ticket(0)
        if 'id' in Json:
            NewTicket.id = Json['id']
        if 'Id' in Json:
            NewTicket.id = Json['Id']
        if 'url' in Json:
            NewTicket.url =Json['url']
        if 'created_at' in Json:
            NewTicket.created_at =Json['created_at']
        if 'updated_at' in Json:
            NewTicket.updated_at = Json['updated_at']
        if 'type' in Json:
            NewTicket.type =Json['type']
        if 'subject' in Json:
            NewTicket.subject =Json['subject']
        if 'raw_subject' in Json:
            NewTicket.raw_subject =Json['raw_subject']
        if 'description' in Json:
            NewTicket.description =Json['description']
        if 'priority' in Json:
            NewTicket.priority =Json['priority']
        if 'status' in Json:
            NewTicket.status =Json['status']
        if 'requester_id' in Json:
            NewTicket.requester_id =Json['requester_id']
        if 'submitter_id' in Json:
            NewTicket.submitter_id =Json['submitter_id']
        if 'assignee_id' in Json:
            NewTicket.assignee_id =Json['assignee_id']
        if 'group_id' in Json:
            NewTicket.group_id = Json['group_id']
        if 'organization_id' in Json:
            NewTicket.organization_id =Json['organization_id']
        if 'fields' in Json:
            NewTicket.fields = Json['fields']
        if 'comments' in Json:
            NewTicket.comments =Json['comments']
        if 'follower_ids' in Json:
            NewTicket.follower_ids = Json['follower_ids']
        if 'collaborator_ids' in Json:
            NewTicket.collaborator_ids = Json['collaborator_ids']
        if 'tags' in Json:
            NewTicket.tags = Json['tags']
        return NewTicket

    @staticmethod
    def JsonToTicketList(Json: list, isFireBaseJson: bool = False):
        Ticket_ist: list = []
        for ticket in Json:
            if isFireBaseJson:
                Ticket_ist.append(Ticket(0).Json_to_ticket(ticket.to_dict()))
            else:
                Ticket_ist.append(Ticket(0).Json_to_ticket(ticket))
        return Ticket_ist

    def toJSON(self):
        return json.dumps(self, default=lambda obj: obj.__dict__)  # , sort_keys=True, indent=4)

    def MapCustomFields(self,Mapping: list):
        if len(self.fields) > 0 and  len(Mapping) > 0 and  'name'not in self.fields[0]:
            Old_Fields = self.fields
            self.fields = []
            for field in Old_Fields:
                for map in Mapping:
                    if 'id' in field and 'Id' in map and field['id'] == map['Id']:
                        self.fields.append({"name": map["Name"],"value": field["value"]})
                        break

    def MapCustomFieldsList(self, Tickets:list,Mapping: list):
        for ticket in Tickets:
            ticket.MapCustomFields(Mapping)

    def Get_Field_By_Name(self, Property_Name:str):
        fld = [field for field in self.fields if field['name'] == Property_Name]
        if len(fld) > 0:
            fld = fld[0]
        return fld

    @staticmethod
    def Resolve_All_Id_Fields(Tickets: list,Zendesk_Users:list, Zendesk_Organizaitons:list,Zendesk_Group:list):
        for ticket in Tickets:
            ticket.Resolve_Id_Fields(Zendesk_Users,Zendesk_Organizaitons,Zendesk_Group)
        return Tickets

    def Resolve_Id_Fields(self,Zendesk_Users:list, Zendesk_Organizaitons:list,Zendesk_Group:list):
         if isinstance(self.group_id, int) and self.group_id > 0:
             group: Models.GroupModel.Group = [group for group in Zendesk_Group if group.id == self.group_id]
             if len(group) > 0:
                self.group_id ={'id': self.group_id,
                                'name': group[0].name}
         if isinstance(self.organization_id, int) and self.organization_id > 0:
             organization:Models.OrganizationModel.Organization  = [org for org in Zendesk_Organizaitons if org.id == self.organization_id]
             if len(organization) > 0:
                 self.organization_id = {'id': self.organization_id,
                                  'name': organization[0].name}

         if isinstance(self.assignee_id, int) and self.assignee_id > 0:
             user: Models.UserModel.User = [usr for usr in Zendesk_Users if
                                                                    usr.id == self.assignee_id]
             if len(user) > 0:
                 self.assignee_id = {'id': self.assignee_id,
                                         'name': user[0].name}

         if isinstance(self.requester_id, int) and self.requester_id > 0:
             user: Models.UserModel.User = [usr for usr in Zendesk_Users if
                                            usr.id == self.requester_id]
             if len(user) > 0:
                 self.requester_id = {'id': self.requester_id,
                                     'name': user[0].name}

         if isinstance(self.submitter_id, int) and self.submitter_id > 0:
             user: Models.UserModel.User = [usr for usr in Zendesk_Users if
                                            usr.id == self.submitter_id]
             if len(user) > 0:
                 self.submitter_id = {'id': self.submitter_id,
                                      'name': user[0].name}

         for id in self.follower_ids:
            user: Models.UserModel.User = [usr for usr in Zendesk_Users if
                                           usr.id == id]
            if len(user) > 0:
                id = {'id': id,
                                     'name': user[0].name}

         for id in self.collaborator_ids:
             user: Models.UserModel.User = [usr for usr in Zendesk_Users if
                                       usr.id == id]
             if len(user) > 0:
                id = {'id': id,
                  'name': user[0].name}



    def Query_For_Database_Tickets(self):
        data = {
            u'id': self.id,
            u'created_at': self.created_at,
            u'updated_at': self.updated_at,
            u'type': self.type,
            u'subject': self.subject,
            u'raw_subject': self.raw_subject,
            u'url': self.url,
            u'description': self.description,
            u'priority': self.priority,
            u'status': self.status,
            u'requester_id': self.requester_id,
            u'submitter_id': self.submitter_id,
            u'assignee_id': self.assignee_id,
            u'organization_id': self.organization_id,
            u'group_id': self.group_id,
            u'collaborator_ids': self.collaborator_ids,
            u'follower_ids': self.follower_ids,
            u'tags': self.tags
        }
        return data
    def Query_For_Database_Fields(self,Field):
        data = {
            u'id': Field["id"],
            u'value': Field["value"],
            u'ticket_id': self.id
        }
        return data
    def Compare_Fields(self,other):
        result = True;
        if isinstance(other,dict):
            Transformed = self.Json_to_ticket(other)
        else:
            Transformed = other

        if len(self.fields) != len(Transformed.fields):
            result = False
        else:
            for field in self.fields:
                if not any(Tools.Get_Attribute(x,'id') == Tools.Get_Attribute(field,'id') and Tools.Get_Attribute(x,'value') == Tools.Get_Attribute(field,'value') for x in other.fields):
                    result = False
                    break
        return result


    def __eq__(self, other):
        if other == {} or other == [] or other == None:
            return False
 
        s = len(vars(self))
        g = len(vars(other))
        if (len(vars(self)) != len(vars(other))):
            return False

        for property in self.__dict__:
            if property !="fields" and (Tools.Get_Attribute(self,property) != Tools.Get_Attribute(other,property)):
                return False

        fields_Same = self.Compare_Fields(other)
        return fields_Same
