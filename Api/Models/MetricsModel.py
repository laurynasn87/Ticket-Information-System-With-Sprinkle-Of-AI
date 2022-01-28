import datetime
class Metrics:
    ticket_id: int = 0
    agent_wait_time_in_minutes = {}
    assignee_stations: int = 0
    assigned_at: datetime = datetime.datetime.now()
    assignee_updated_at: datetime = datetime.datetime.now()
    created_at: datetime = datetime.datetime.now()
    updated_at: datetime = datetime.datetime.now()
    first_resolution_time_in_minutes = {}
    full_resolution_time_in_minutes = {}
    initially_assigned_at: datetime = datetime.datetime.now()
    latest_comment_added_at: datetime = datetime.datetime.now()
    on_hold_time_in_minutes = {}
    reopens: int = 0
    replies: int = 0
    reply_time_in_minutes = {}
    requester_updated_at: datetime = datetime.datetime.now()
    requester_wait_time_in_minutes: datetime = datetime.datetime.now()
    solved_at: datetime = datetime.datetime.now()
    status_updated_at: datetime = datetime.datetime.now()


    @staticmethod
    def from_dict(my_dict):
        new_met: Metrics = Metrics()
        for key in my_dict:
            if key == 'ticket_id':
                new_met.ticket_id = my_dict[key]
            if key == 'agent_wait_time_in_minutes':
                new_met.agent_wait_time_in_minutes = my_dict[key]
            if key == 'assignee_stations':
                new_met.assignee_stations = my_dict[key]
            if key == 'assigned_at':
                new_met.assigned_at = my_dict[key]
            if key == 'assignee_updated_at':
                new_met.assignee_updated_at = my_dict[key]
            if key == 'created_at':
                new_met.created_at = my_dict[key]
            if key == 'updated_at':
                new_met.updated_at = my_dict[key]
            if key == 'first_resolution_time_in_minutes':
                 new_met.first_resolution_time_in_minutes = my_dict[key]
            if key == 'full_resolution_time_in_minutes':
                new_met.full_resolution_time_in_minutes = my_dict[key]
            if key == 'initially_assigned_at':
                new_met.initially_assigned_at = my_dict[key]
            if key == 'latest_comment_added_at':
                new_met.latest_comment_added_at = my_dict[key]
            if key == 'on_hold_time_in_minutes':
                new_met.on_hold_time_in_minutes = my_dict[key]
            if key == 'reopens':
                new_met.reopens = my_dict[key]
            if key == 'replies':
                new_met.replies = my_dict[key]
            if key == 'reply_time_in_minutes':
                new_met.reply_time_in_minutes = my_dict[key]
            if key == 'requester_updated_at':
                new_met.requester_updated_at = my_dict[key]
            if key == 'requester_wait_time_in_minutes':
                new_met.requester_wait_time_in_minutes = my_dict[key]
            if key == 'solved_at':
                new_met.solved_at = my_dict[key]
            if key == 'status_updated_at':
                new_met.status_updated_at = my_dict[key]
        return new_met

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