class Group:
    id:int = 0
    name:str = ''
    description: str = ''

    @staticmethod
    def from_dict(my_dict):
        new_group:Group = Group()
        for key in my_dict:
            if key == 'id':
                new_group.id=my_dict[key]
            if key == 'name':
                new_group.name = my_dict[key]
            if key == 'description':
                new_group.description = my_dict[key]
        return new_group

    def Query_For_Database_Tickets(self):
        data = {
            u'id': self.id,
            u'name': self.name,
            u'description': self.description
        }
        return data