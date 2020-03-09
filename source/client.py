import os
import json
import discord
import asyncio
import schedule
from datetime import datetime, time, timedelta
from source.commandintegrator.framework import CommandProcessor, PronounLookupTable
from source.commandintegrator.logger import logger
from dotenv import load_dotenv
from pathlib import Path
from source.custom_errs import *
from source.event import Event
from source.weekdays import Weekdays
from source.features.LunchMenuFeature import LunchMenuFeature
from source.features.RedditJokeFeature import RedditJokeFeature
from source.features.ScheduleFeature import ScheduleFeature
from source.features.CoronaSpreadFeature import CoronaSpreadFeature

'''
Details:
    2019-09-25

Module details:
    Service main executable

Synposis:
    Initialize the bot with api reference to Discords
    services. Instantiate bot intelligence from separate
    modules. 
'''

class RobBotClient(discord.Client):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop.create_task(self.run_scheduler())  
        self._guild = kwargs['DISCORD_GUILD']
        self.processor = commandprocessor= (
            ScheduleFeature(url = kwargs['TIMEEDIT_URL']),
            LunchMenuFeature(url = kwargs['LUNCH_MENU_URL']),
            RedditJokeFeature(client_id = kwargs['REDDIT_CLIENT_ID'], 
                client_secret = kwargs['REDDIT_CLIENT_SECRET'],
                user_agent = kwargs['REDDIT_USER_AGENT']))
    @logger
    async def on_ready(self):
        '''
        This method is called as soon as the bot is online.
        '''
        for guild_name in client.guilds:
            if guild_name == self._guild:
                break

    @logger
    async def on_member_join(self, member):
        '''
        If a new member just joined our server, greet them warmly!
        '''
        greeting_phrase = self.brain.greet(member.name)
        await member.create_dm()
        await member.dm_channel.send(greeting_phrase)
        

    @logger
    async def on_message(self, message):
        '''
        Respond to a message in the channel if someone
        calls on the bot by name, asking for commands.
        '''
        now = datetime.now().strftime('%Y-%m-%d -- %H:%M:%S')    
        if message.content.lower().startswith('rob') and message.author != client.user:
            await message.channel.send(processor.process(message).response())
                
    
    @logger
    async def run_scheduler(self):
        '''
        Loop indefinitely and send messages that are pre-
        defined on a certain day and a certain time. 
        '''

        await client.wait_until_ready()
        channel = self.get_channel(651080743388446750) # Private. Edit on server.
        
        while not self.is_closed():            
            result = schedule.run_pending()
            if result: channel.send(result)
    
    @logger
    async def purge_runtime(self):
        '''
        Refresh the Schedule object with a new updated
        variant of the schedule from the web by using
        its own method for this. Perform this action
        daily at midnight.
        '''
        await client.wait_until_ready()
        while not self.is_closed():

            now = self.brain.schedule.current_time
            midnight = datetime(now.year, now.month, now.day, 0, 10, 0)
            time_left = (midnight - now)

            await asyncio.sleep(time_left.seconds)
                        
            try:
                self.brain.schedule.set_calendar()
                self.brain.schedule.truncate_event_name()
                self.brain.schedule.adjust_event_hours(hourdelta = self._hourdelta)
                self.setup_reminders()
                removed_activities = self.brain.reminder.purge()
                self.brain.lunch_menu_scraper.purge_cache()

            except Exception:
                pass
            else:                
                await asyncio.sleep(1)

    @logger
    def setup_reminders(self, reoccuring = []):
        '''
        Create Event instances and keep them in Reminders object
        for each day. If lessons or events are encountered for given 
        current day, these will be represented by an Event instance.
        '''

        if len(self.brain.schedule.todays_events):
            for element in self.brain.schedule.todays_events:
                self.brain.reminder.add(Event(
                    body = element.name, 
                    date = element.begin.date(),
                    time = element.begin.adjusted_time,
                    location = element.location,
                    curriculum_event = True,
                    alarm = timedelta(hours = 1)))

        if len(reoccuring):
            for element in reoccuring:
                self.brain.reminder.add_reoccuring(element)


def load_environment(env_var_strings: list):
    
    load_dotenv()
    var_dict = {}

    for var in env_var_strings:
        var_dict[var] = os.getenv(var)

    return var_dict

if __name__ == '__main__':

    enviromnent_strings = [
        'DISCORD_GUILD',
        'TIMEEDIT_URL',
        'LUNCH_MENU_URL',
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'REDDIT_USER_AGENT',
        'GOOGLE_API_KEY',
        'GOOGLE_CSE_ID',
        'DISCORD_TOKEN',
        'CORONA_API_URI',
        'CORONA_API_RAPIDAPI_HOST',
        'CORONA_API_RAPIDAPI_KEY'
    ]


    with open('C:\\users\\admin\\git\\robbottherobot\\source\\commandintegrator\\commandintegrator.settings.json', 'r', encoding = 'utf-8') as f:
        default_responses = json.loads(f.read())['default_responses']

    environment_vars = load_environment(enviromnent_strings)
    
    processor = CommandProcessor(
        pronoun_lookup_table = PronounLookupTable(), 
        default_responses = default_responses
    )
    
    lunchmenu_ft = LunchMenuFeature(url = environment_vars['LUNCH_MENU_URL'])
    schedule_ft = ScheduleFeature(url = environment_vars['TIMEEDIT_URL'])
    corona_ft = CoronaSpreadFeature(
                    CORONA_API_URI = environment_vars['CORONA_API_URI'],
                    CORONA_API_RAPIDAPI_HOST = environment_vars['CORONA_API_RAPIDAPI_HOST'],
                    CORONA_API_RAPIDAPI_KEY = environment_vars['CORONA_API_RAPIDAPI_KEY'],
                    translation_file_path = 'C:\\users\\admin\\git\\robbottherobot\\source\\country_eng_swe_translations.json'
                )

    redditjoke_ft = RedditJokeFeature(
                        client_id = environment_vars['REDDIT_CLIENT_ID'], 
                        client_secret = environment_vars['REDDIT_CLIENT_SECRET'],
                        user_agent = environment_vars['REDDIT_USER_AGENT']
                    )
    
    processor.features = (lunchmenu_ft, lunchmenu_ft, corona_ft, redditjoke_ft)    
    
    schedule.every().day.at('08:00').do(schedule_ft.get_todays_lessons, scheduled_call = True)
    schedule.every(5).seconds.do(schedule_ft.get_todays_lessons, scheduled_call = True)

    client = RobBotClient(**environment_vars)
    client.run(environment_vars['DISCORD_TOKEN'])