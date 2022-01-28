import datetime


class Comment:
    id:int = 0
    type: str = ''
    author_id: int = 0
    body: str = ''
    html_body: str = ''
    plain_body: str = ''
    public: bool = True
    attachments: list = []
    created_at: datetime = datetime.datetime.now()

    @staticmethod
    def from_dict(my_dict):
        new_com:Comment = Comment()
        for key in my_dict:
            if key == 'id':
                new_com.id=my_dict[key]
            if key == 'type':
                new_com.type = my_dict[key]
            if key == 'author_id':
                new_com.author_id = my_dict[key]
            if key == 'body':
                new_com.body = my_dict[key]
            if key == 'html_body':
                new_com.html_body = my_dict[key]
            if key == 'plain_body':
                new_com.plain_body = my_dict[key]
            if key == 'public':
                new_com.public = my_dict[key]
            if key == 'attachments':
                new_com.attachments = my_dict[key]
            if key == 'created_at':
                new_com.created_at = my_dict[key]
        return new_com

    def Query_For_Database_Tickets(self):
        data = {
            u'id': self.id,
            u'type': self.type,
            u'author_id': self.author_id,
            u'html_body': self.html_body,
            u'plain_body': self.plain_body,
            u'public': self.public,
            u'attachments': self.attachments,
            u'created_at': self.created_at
        }
        return data

    @staticmethod
    def Resolve_Assignee(Comments_List:list,Zendesk_Users:list):
        comments = Comments_List
        if 'data' in Comments_List:
            comments = Comments_List["data"]

        for comment in comments:
            if isinstance(comment.author_id,int) and comment.author_id > 0:
                user: Models.UserModel.User = [usr for usr in Zendesk_Users if
                                               usr.id == comment.author_id]
                if len(user) > 0:
                    comment.author_id = {'id': comment.author_id,
                                         'name': user[0].name}

        return Comments_List