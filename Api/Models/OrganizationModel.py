import datetime
from Models import GroupModel
class Organization:
    id: int = 0
    name: str = ''
    created_at: datetime = datetime.datetime.now()
    updated_at: datetime = datetime.datetime.now()
    group_id = ''
    tags: list = []
    domain_names = []

    @staticmethod
    def from_dict(my_dict):
        new_org:Organization = Organization()
        for key in my_dict:
            if key == 'id':
                new_org.id=my_dict[key]
            if key == 'name':
                new_org.name = my_dict[key]
            if key == 'created_at':
                new_org.created_at = my_dict[key]
            if key == 'updated_at':
                new_org.updated_at=my_dict[key]
            if key == 'group_id':
                new_org.group_id=my_dict[key]
            if key == 'tags':
                new_org.tags=my_dict[key]
            if key == 'domain_names':
                new_org.domain_names=my_dict[key]
        return new_org
    @staticmethod
    def Resolve_All_Id_Fields(Organizations: list,Zendesk_Group:list):
        for org in Organizations:
            org.Resolve_Id_Fields(Zendesk_Group)
        return Organizations

    def Resolve_Id_Fields(self,Zendesk_Group:list):
         if self.group_id is not None and self.group_id > 0:
             group: GroupModel.Group = [group for group in Zendesk_Group if group.id == self.group_id]
             if len(group) > 0:
                self.group_id ={'id': self.group_id,
                                'name': group[0].name}

    def Query_For_Database_Tickets(self):
        data = {
            u'id': self.id,
            u'created_at': self.created_at,
            u'updated_at': self.updated_at,
            u'name': self.name,
            u'group_id': self.group_id,
            u'tags': self.tags,
            u'domain_names': self.domain_names
        }
        return data