import discord
import time
import json
import sqlite3
import asyncio
import re
import datetime
import requests
import bs4
import pymongo


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
work_week TEXT,
holiday TEXT,
last_punch TIMESTAMP
);""")



# Webscrape for holidays
def get_holidays():
    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["website_db"]
    collection = db["website_data"]
    
    # List of websites to scrape
    websites = [
        "https://www.qppstudio.net/public-holidays/north-america.htm",
        "https://www.qppstudio.net/public-holidays/central-america.htm",
        "https://www.qppstudio.net/public-holidays/south-america.htm",
        "https://www.qppstudio.net/public-holidays/europe.htm",
        "https://publicholidays.ru/2023-dates/",
        "https://www.qppstudio.net/public-holidays/asia.htm",
        "https://www.qppstudio.net/public-holidays/middle-east.htm",
        "https://www.qppstudio.net/public-holidays/africa.htm",
        "https://www.qppstudio.net/public-holidays/oceania.htm",
        "https://www.qppstudio.net/public-holidays/world.htm"
        ]
    
    # List of Regions by the 
    Region = [
        "North America",
        "Central America",
        "South america",
        "Europe",
        "Russia",
        "Asia",
        "Middle East",
        "Africa",
        "Oceania",
        "World"
    ]
    
     # Replace with the website that contains the holiday information
    url = "https://www.example.com/holidays"
    for websites in websites:

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    holidays = []
    # Extract the holiday dates from the website and add them to the list
    for holiday_element in soup.find_all('div', {'class': 'holiday'}):
        holiday_date = holiday_element.find('span', {'class': 'date'}).text
        holidays.append(holiday_date)
    return holidays


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
        date = datetime.datetime.strptime(
            userResponse.content.split(" ")[0], "%m/%d/%Y")

        cur.execute(f"""INSERT INTO {table_name} (user_id, name, birthday, has_role) 
        VALUES ({ctx.author.id}, "{name}", "{date.strftime("%Y-%m-%d")} 00:00:00", False)""")
        con.commit()

        await ctx.send(f"Registered as {name} with birthday {date.strftime('%B %d, %Y')}.")


asyncio.run(bot.add_cog(BossBot(bot)))
bot.run(config.token)
