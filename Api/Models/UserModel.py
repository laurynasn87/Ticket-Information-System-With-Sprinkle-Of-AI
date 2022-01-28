class User:
    id: int = 0
    name: str = ''
    created_at: str = ''
    updated_at: str = ''
    email: str = ''
    time_zone: str = ''
    phone: str = ''
    organization_id = ''
    role: str = ''
    verified: bool = False
    active: bool = False
    last_login_at: str =''
    signature: str = ''
    default_group_id = ''

    @staticmethod
    def from_dict(my_dict):
        new_usr:User = User()
        for key in my_dict:
            if key == 'id':
                new_usr.id=my_dict[key]
            if key == 'name':
                new_usr.name = my_dict[key]
            if key == 'created_at':
                new_usr.created_at = my_dict[key]
            if key == 'updated_at':
                new_usr.updated_at=my_dict[key]
            if key == 'email':
                new_usr.email=my_dict[key]
            if key == 'time_zone':
                new_usr.time_zone=my_dict[key]
            if key == 'phone':
                new_usr.phone=my_dict[key]
            if key == 'organization_id':
                new_usr.organization_id=my_dict[key]
            if key == 'role':
                new_usr.role=my_dict[key]
            if key == 'verified':
                new_usr.verified=my_dict[key]
            if key == 'active':
                new_usr.active=my_dict[key]
            if key == 'last_login_at':
                new_usr.last_login_at=my_dict[key]
            if key == 'signature':
                new_usr.signature=my_dict[key]
            if key == 'default_group_id':
                new_usr.default_group_id=my_dict[key]
        return new_usr

    def Resolve_Id_Fields(self,Zendesk_Organizaitons:list,Zendesk_Group:list):
         if isinstance(self.default_group_id,int) and self.default_group_id > 0:
             group: Models.GroupModel.Group = [group for group in Zendesk_Group if group.id == self.default_group_id]
             if len(group) > 0:
                self.default_group_id ={'id': self.default_group_id,
                                'name': group[0].name}
         if isinstance(self.organization_id,int) and self.organization_id > 0:
             organization:Models.OrganizationModel.Organization  = [org for org in Zendesk_Organizaitons if org.id == self.organization_id]
             if len(organization) > 0:
                 self.organization_id = {'id': self.organization_id,
                                  'name': organization[0].name}
    @staticmethod
    def Resolve_All_Id_Fields(Users_List:list,Zendesk_Organizaitons:list,Zendesk_Group:list):
        for user in Users_List:
            user.Resolve_Id_Fields(Zendesk_Organizaitons,Zendesk_Group)
        return Users_List

    def Query_For_Database_Tickets(self):
        data = {
            u'id': self.id,
            u'created_at': self.created_at,
            u'updated_at': self.updated_at,
            u'name': self.name,
            u'email': self.email,
            u'time_zone': self.time_zone,
            u'phone': self.phone,
            u'organization_id': self.organization_id,
            u'role': self.role,
            u'verified': self.verified,
            u'active': self.active,
            u'last_login_at': self.last_login_at,
            u'signature': self.signature,
            u'default_group_id': self.default_group_id
        }
        return data
