import discord
import time
import json
import sqlite3
import asyncio
import re
import datetime

from dayQuote import get_quote_of_the_day
from regionHoliday import get_RegionHDays
from discord.ext import commands
from discord.ext.commands import errors, Cog
from collections import namedtuple

def readConfig(file):
    try:
        with open(file, encoding='utf8') as data:
            return json.load(data, object_hook=lambda d: namedtuple("Config", d.keys())(*d.values()))
    except AttributeError as exc:
        raise AttributeError("Unknown argument") from exc
    except FileNotFoundError as exc:
        raise FileNotFoundError("JSON file wasn't found") from exc

# Initialization
config = readConfig("config.json")  # Config
bot = commands.Bot(
    command_prefix=config.prefix, prefix=config.prefix, command_attrs=dict(
        hidden=True),
    intents=discord.Intents.all()
)  # Bot object
# We can set isolation_level to None for auto commit, but worse performance
con = sqlite3.connect("schedule.db")
# Use cur.execute("sql string") to execute sql on storage.db, then con.commit() when done
cur = con.cursor()

# Table creation
# (Note that when we create new columns mid development,
# a new table will have to be created or an existing table manually edited)
table_name = "schedule"
cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
user_id INTEGER NOT NULL,
name TEXT NOT NULL,
birthday TIMESTAMP NOT NULL,
has_role BOOLEAN NOT NULL,
region TEXT NOT NULL,
holiday TEXT,
last_punch TIMESTAMP,
Monday_start TIME,
Monday_end TIME,
Tuesday_start TIME,
Tuesday_end TIME,
Wednesday_start TIME,
Wednesday_end TIME,
Thursday_start TIME,
Thursday_end TIME,
Friday_start TIME,
Friday_end TIME,
Saturday_start TIME,
Saturday_end TIME,
Sunday_start TIME,
Sunday_end TIME 
);""")
 
class BossBot(Cog):
    def __init__(self, bot):
        self.bot = bot

        print("Logging in...")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(
                ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            await ctx.send(f"There was an error processing the command\n{err}")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')
        await self.bot.change_presence(
            activity=discord.Activity(type=3, name="Do your job!"),
            status=discord.Status.online
        )

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("Loading...")
        ping = int((time.monotonic() - before) * 1000)
        await message.edit(content=f"Pong! WS: {before_ws}ms  |  REST: {ping}ms")

    @commands.command()
    async def echo(self, ctx, toecho):
        """ Repeats what is entered in echo command argument """
        await ctx.send(toecho)

    @commands.Cog.listener()
    # hello bot function
    async def on_member_join(self, member): 
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Hello! Welcome {member.mention} to the server!")

    @commands.command()
    async def register(self, ctx):
        """ Register new user information. Starts multiple prompts. """
        # Full name prompt
        start_msg = await ctx.send(f"Hello there **{ctx.author.name}**, please enter your real first and last name.")

        def check_name(m):  # No requirements for name, whatever the user inputs, that's their name
            return True
        try:
            userResponse = await self.bot.wait_for('message', timeout=30.0, check=check_name)
        except asyncio.TimeoutError:
            return await start_msg.edit(
                content=f"~~{start_msg.clean_content}~~\n\nTimed out, please run register again."
            )
        name = userResponse.content

        # Birthday prompt
        # Using RegEx to check if user input matches what is expected
        re_timestamp = r"^(0[1-9]|1[0-2])\/(0[0-9]|1[0-9]|2[0-9]|3[0-1])\/([1-2]{1}[0-9]{3})"
        birthday_msg = await ctx.send(f"Hello, **{name}**, now enter your date of birth in the following format `MM/DD/YYYY`")

        def check_timestamp(m):
            if (m.author == ctx.author and m.channel == ctx.channel):
                if re.compile(re_timestamp).search(m.content):
                    return True
            return False

        try:
            userResponse = await self.bot.wait_for('message', timeout=30.0, check=check_timestamp)
        except asyncio.TimeoutError:
            return await birthday_msg.edit(
                content=f"~~{start_msg.clean_content}~~\n\nTimed out or invalid inputs, please run register again."
            )
        
        try:
            date = datetime.datetime.strptime(userResponse.content.split(" ")[0], "%m/%d/%Y")
        except ValueError:
            return await birthday_msg.edit( content=f"~~{start_msg.clean_content}~~\n\nInvalid date format. Please run register again.")
        
        # Region prompt
        region_msg = await ctx.send(f"Hello, **{name}**, now enter your region form the fallowing Region list: `North America`,`Central America`,`South America`,`Europe`,`Asia`,`Middle East`,`Africa`,`Oceania`,`World`")

        def check_region(m):
            if (m.author == ctx.author and m.channel == ctx.channel):
                return True
            return False
        try:
            userResponse = await self.bot.wait_for('message', timeout=30.0, check=check_region)
        except asyncio.TimeoutError:
            return await region_msg.edit(
                content=f"~~{region_msg.clean_content}~~\n\nTimed out, please run `!register` again."
                )
        region = userResponse.content
        # TODO: Test this real quick for error checking, fix if time (done)

        # insert holidays based on region
        # inserts as abbreviated month
        # Example: datetime.datetime.strptime('Mar\xa23','%b\xa%d').strftime('%m/%d')
        holidays = get_RegionHDays(region)
        try:
            cur.execute(f"""INSERT INTO {table_name} (user_id, name, birthday, region, holiday, has_role) 
                VALUES ({ctx.author.id}, "{name}", "{date.strftime("%Y-%m-%d")} 00:00:00", "{region}", "{','.join(holidays)}", False)""")
        except sqlite3.Error as e:
            return await ctx.send(f"An error occurred while registering: {e}. PLEASE RETRY `!register` and ensure to enter data in the correct format")
        
        con.commit()
        await ctx.send(f"Registered as {name} from {region} with birthday {date.strftime('%B %d, %Y')}.")
        
    @commands.command()
    async def today(self, ctx):
        """Shows data for data base on todays date based off in put form user"""
        #TODO Finish quote of the day (done)
        quote = get_quote_of_the_day()
        cur.execute(f"SELECT holiday FROM schedule WHERE user_id = {ctx.author.id}")
        holidays = cur.fetchone()[0]
        today = datetime.date.today().strftime('%Y-%m-%d')
        await ctx.send(f"{quote}")
        holidays = holidays.split(",")
        if today in holidays:
            await ctx.send(f"Today is a holiday in your Region. Enjoy the day off!")
        else:
            await ctx.send("Get back to work! Today is not a holiday in your region. If you are not sure if you work try `!work_schedule`.")

    @commands.command()
    async def schedule(self, ctx):
        """Prompts the user to enter their work week schedule."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
        for day in days:
            start_msg = await ctx.send(f"Enter start and end time for **{day}** (or enter 'none' if you don't wish to work). Enter the start and end time range as 24 hour time hh:mm hh:mm, separated by a space. Example `9:00 17:00` to start at 9:00 and end at 17:00.")
            # No requirements for name, whatever the user inputs, that's their name
            def check_time(m):
                return True
            try:
                response = await self.bot.wait_for('message', timeout=30.0, check=check_time)
            except asyncio.TimeoutError:
                return await start_msg.edit(
                    content=f"~~{start_msg.clean_content}~~\n\nTimed out, please run schedule again."
            )
            if response.content.lower() == 'none':
                continue
            else:
                start, end = response.content.split() # start and end times
                cur.execute(f'UPDATE {table_name} SET {day}_start="{start}", {day}_end="{end}" WHERE user_id={ctx.author.id};')
                con.commit()
        #TODO Add confirm message (done)
        await ctx.send(f"Thank you for entering your schedule. Welcome to Umbrella Corp. Enjoy your stay!")

    @commands.command()
    async def check_work(self, ctx):
        """Checks if a user is offline during their work hours Uses punch in time and punch out time."""
        # get the current time
        now = datetime.datetime.now()
        current_hour = now.hour

        # get the user's work hours from the database
        con.execute("SELECT day, start_time, end_time FROM workweek WHERE user_id=?", (ctx.author.id,))
        work_hours = con.fetchone()
        if work_hours is None:
            await ctx.send("You haven't set your work week schedule yet. Please use the `!schedule` command to set it.")
            return

        day = datetime.datetime.today().strftime('%A')
        if day == work_hours[0] and (current_hour >= int(work_hours[1]) and current_hour <= int(work_hours[2])):
            if ctx.author.status == discord.Status.offline:
                await ctx.send(f"{ctx.author.mention} get back to work!")
    
    @commands.command()
    async def work_schedule(self, ctx):
        """Retrieves the user's schedule for a specific date."""
        await ctx.send("Please enter the date you would like to know about in the following format `MM/DD/YYYY`:")
        response = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
        date_str = response.content
        try:
            date = datetime.datetime.strptime(date_str, '%m/%d/%Y').date()
        except ValueError:
            await ctx.send("Invalid date format. Please enter a date in the following format `MM/DD/YYYY`.")
            return
        user_id = ctx.author.id
        cur.execute("SELECT * FROM schedule WHERE user_id=?", (user_id,))
        result = cur.fetchone()
        if result:
            day_of_week = date.strftime('%A').lower()
            day_of_week = day_of_week[0].upper() + day_of_week[1:].lower()
            dow_start = day_of_week + '_start'
            dow_end = day_of_week + '_end'
            start_time_index = None
            end_time_index = None
            bday_index = 2
            holiday_index = 5
            for i, column in enumerate(cur.description):
                if column[0] ==  dow_start:
                    start_time_index = i
                elif column[0] == dow_end:
                    end_time_index = i
            if start_time_index is None or end_time_index is None:
                await ctx.send(f"You have not entered a schedule for {day_of_week.capitalize()} ({date_str}).")
                return
            start_time = result[start_time_index]
            end_time = result[end_time_index]
            if start_time and end_time:
                # Check for holiday
                holidays = result[holiday_index]
                date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
                date_form = date.strftime('%Y-%m-%d')
                holidays = holidays.split(",")
                if date_form in holidays:
                    await ctx.send(f"Today is a holiday and you have the day off!")
                    return
                # Check for birthday
                birthday = result[bday_index]
                bday = datetime.datetime.strptime(birthday,'%Y-%m-%d %H:%M:%S')
                bdFomat = bday.strftime('%m/%d')
                if bdFomat == date_str[0:5]:
                    await ctx.send(f"Today is your birthday and you have the day off!")
                    return
                await ctx.send(f"Your schedule for {date_str} ({day_of_week.capitalize()}) is from {start_time} to {end_time}.")
            else:
                await ctx.send(f"You have not entered a schedule for {day_of_week.capitalize()} ({date_str}).")
        else:
            await ctx.send("You have not set up a schedule yet. Please run `!schedule`!")
        #TODO Remove redundancy, rework to print the work schedule
    

    # punch in famework added to help aliviate code stress on ethan
    # time punch in command
    #@commands.command()
    #async def punch_in(ctx):
        """Punches the user in for their shift."""
        """user_id = ctx.author.id
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con.execute("INSERT INTO {table_name} (user_id, punch_in) VALUES (?, ?)", (user_id, now))
        con.commit()"""

    # time punch out command
    #@commands.command()
    #async def punch_out(ctx):
        """Punches the user out from their shift."""
        """ user_id = ctx.author.id
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con.execute("UPDATE {table_name} SET punch_out = ? WHERE user_id = ? AND punch_out IS NULL", (now, user_id))
        con.commit()
        if con.rowcount == 1:
            await ctx.send(f"You have been punched out at {now}.")
        else:
            await ctx.send("You are not currently punched in. Please Punch in")"""


         


asyncio.run(bot.add_cog(BossBot(bot)))
bot.run(config.token)
