# Ticket Information System
 
##### Libs/Technologies:
 * Flask
 * Angular
 * Gensim
 * Material

##### Summary:
Ticket information system is a system developed by me, which main goal was to develop a base for new helpdesk with functionalities that were lacking in the old one, so it could replace it at some time.

System currently is hosted on a website for easy reach.
System gets its data from old system and adds some of its own, data received from old system is filtered if any new changes were made and if there was, only those will proceed to the next steps of their data getting pulled. This was done to lower amount of request to the system, as they are costly.




#### Pages:
##### Login:
![Login](https://raw.githubusercontent.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/main/images/login.png?raw=true)

Login in the system is implemented with the help of firebase auth which helps me ensure the upmost security.
Firebase login token is reused when sending queries to API

##### Home:
![Home](https://raw.githubusercontent.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/main/images/home.png?raw=true)

Once logged in, user is welcomed with information tiles that show what has happened during the time off, it's very useful tool which brings attention to issues that need it the most and quickly.

##### Search:
![Search](https://raw.githubusercontent.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/main/images/search.png?raw=true)

System search lets all of the users to find the ticket/organization/user they want.

##### My Tickets:
![MyTickets](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/raw/main/images/my_tickets.png?raw=true)

My ticket helps to stay on top of users tickets, as it only shows user from older system which is connected to current one, tickets. Views are selectable and configurable in the admin panel.

##### Statistics:
![Statistics](https://raw.githubusercontent.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/main/images/statistics.png)

In the old system, it was quite common for team leaders to export whole ticket file and analyse them in excel or any other program. Because of that reason, my system consists of config created diagrams of each entity in system.

##### New Ticket Form:
![NewTicketForm](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/new_ticket.png?raw=true)

Usual new ticket form with 3 tier info gathering.

##### Old System Ticket:
![Old Ticket](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/recieved.png?raw=true?)

Old system ticket among the details also contains metrics that new system does not have. Old system tickets have a handicap when it comes to functionality, it's not as easy to refresh it or to leave a comment. Those things have to get from old system, so all you can do is press a button to refresh comments or create one, which will run the data refresh for this ticket.

Among other things, this page has "Ai" section which provides closes tickets as described below.

![Ai](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/ai.png?raw=true?)
Main Data Tile- Shows closes by ticket name and description
Full data Tile - By main data and comments
Within X - shows by main data with same organization.
Most experienced user- this user is retrieved from previously showed tickets by their percentages summed up.

Those percentages show how likely it is from the same topic as this topic according to AI

##### This System Ticket:
![New Ticket](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/internal.png?raw=true)

Main difference between old system ticket and new, it's that in the new system you are able to change fields and leave comments instantly.

##### Admin Panel:
![Admin](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/admin%20panel.png?raw=true)

Admin panel main purpose to manage this website.
This panel helps you manage users

![settings](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/settings.png?raw=true)
This panel also lets you configure main settings like data retrieval from old system, if it's on, it will run every x hours according to config in the next section.
Additionally you can change AI type, comments to old system status, topic count

![config](https://github.com/laurynasn87/Ticket-Information-System-With-Sprinkle-Of-AI/blob/main/images/config.png?raw=true)
Config section lets you change quite a few things in the system, from every what hours does Ai model create new one, data is refreshed... to chart configs in statistic tab and columns in system tables.


#### Ai:
##### Types:
In this system, there are two types of AI, they both are a part of machine learning branch, Topic modelling.
LDA (Latent Dirichlet allocation)
HDP (Hierarchical Dirichlet process)
##### Basis:
During my time in Tech Support for CRM products, it was quite common for the same issues to appear for different products. The problem would arise when the same problem would be allocated to different person every time it was raised, so in turn costing company extra resources to analyse, develop, test it. To avoid this problem, I created AI to find the closest ticket and the best user to solve it, so we wouldn't waste time, but use the previous solution (if there is) and assign it to someone with experience.
##### Road of the Data
To prepare data, each sentence has to be parsed into words.
each non essential word (you, please, and...) be removed
each name, be removed
each word be lemmatized
each word have to be assigned to vectorial point value via the dictionary
##### How does it work for me?
As you might know, topic modelling assigns words to self created topics within itself.
Which in turn lets me input my ticket information and get the result to which topic, my ticket is closest (by portraying probability)
When I know each of my tickets probabilities to every topic, I search for closest probability scores among other tickets with Jensen–Shannon divergence - probability distance counter.
That is how those percentages in the Ai section of the ticket are formed.
