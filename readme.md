# Rob Bot



## What is it?

The Rob Bot project is a chat bot, specifically written to be of assistance for me and my college mates.

The initial purpose was to inform us in the chat every morning which classroom we were seated in for the day. However this quickly opened up my eyes as to just how much the bot could actually do for us. Reminders, automatic messages on schedule, scraping the lunch menu site, Google Custom Search integration etcetera. 

## Features

* Integration with the TimeEdit server used by our college
  This integration allows the bot to subscribe to the schedule for our class. It allows the bot to automatically
  inform students of which classroom is being used each morning, or any time during the day. 
  It also returns the schedule as far in the future as is allowed by the Discord char limit of 2000 chars.
  
* Integration with Google Custom Search Engine
  This feature allows the bot to answer virtually any question. If the bot recognizes a message as a question 
  for this integration, a JSON response from CSE is parsed and returned in chat.
  
* Integration with Reddit
  This feature is just for fun. At the time of writing, the bot uses this integration to fetch random jokes from r/jokes and r/ProgrammerHumor when asked in chat.
  
* Integration with a custom web scraper
  This feature answers the question "What's on the menu for today?" and similar queries. It scrapes the lunch menu for the local cafeteria on campus, yielding the menu for today. 
  
* Custom reminders
  The reminders feature is pretty cool - the bot will remember things that people ask for it to remember and then sends a message in the #general channel at provided date and time. This feature is creating instances of the **Event** class.
  The **Event** class is also used to create automatic reminders. Every night at 00:10, the bot will re-load the TimeEdit-calling **Schedule** object and generate automatic **Event** instances with alarms set. This allows the bot to automatically write in the #General channel every morning at 8:00AM and at lunch time, with information about the upcoming lesson with location and time info.

## Mentions

This project would not have been possible if it were not for these 3rd party libraries which are hereby mentioned with the utmost gratitude:

* google-api-python-client (Apache License 2.0)  https://github.com/googleapis/google-api-python-client
* BeautifulSoup4 (MIT License) https://pypi.org/project/beautifulsoup4/
* discord.py (MIT License) https://github.com/Rapptz/discord.py
* praw (BSD 2-Clause "Simplified" License) https://github.com/praw-dev/praw
* ics (Apache License 2.0) https://pypi.org/project/ics/

## Contributions

Do you want to contribute to this project? Want one of these bots for your college class?
Clone and send a PR or email me at dotchetter@protonmail.ch to get in touch.