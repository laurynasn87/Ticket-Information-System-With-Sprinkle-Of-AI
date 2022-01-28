#!/usr/bin/env python

ZendeskSource = {
    "url": "xxxxxxxxxxxxxxx",
    "ticket_url": "tickets.json",
    "Users": "users",
    "Organizations":"organizations",
    "Groups": "groups",
    "Comments":"tickets/{Ticket_Id}/comments",
    "Metrics":"tickets/{Ticket_Id}/metrics"
}
Fire_Store_Cred_Path = './data/xxxx-firebase-adminsdk-39n2t-01fd637433.json'
Front_End_Path="xxxxxxxxxxxx"
Cache_Config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
Save_Models=True
GoogleCloud = False