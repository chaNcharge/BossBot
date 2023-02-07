import discord
import time
import json
import sqlite3

from discord.ext import commands
from discord.ext.commands import errors, Cog
from collections import namedtuple



def readConfig(file):
    try:
        with open(file, encoding='utf8') as data:
            return json.load(data, object_hook=lambda d: namedtuple("Config", d.keys())(*d.values()))
    except AttributeError:
        raise AttributeError("Unknown argument")
    except FileNotFoundError:
        raise FileNotFoundError("JSON file wasn't found")


# Config and bot object
config = readConfig("config.json")
bot = commands.Bot(
    command_prefix=config.prefix, prefix=config.prefix, command_attrs=dict(
        hidden=True),
    intents=discord.Intents(guilds=True, messages=True, members=True)
)


class BossBot(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.conn = sqlite3.connect("schedule.db")
        self.cursor = self.conn.cursor()

        self.cursor.excute("""
            CREATE TABLE IF NOT EXIST schedule( 
            user_id TEXT,
            work_week TEXT,
            holiday TEXT
            )
        """)


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
    

    @commands.Cog.listener()
    # hello bot function
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f"Hello! Welcome {member.mention} to the server!")

bot.add_cog(BossBot(bot))
bot.run(config.token)
