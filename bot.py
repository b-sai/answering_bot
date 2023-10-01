import discord
from dotenv import load_dotenv
import os
from discord.ext import commands

load_dotenv()

token = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    # await bot.load_extension("cogs.message_part")
    await bot.load_extension("cogs.answering")

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await load_extensions()


bot.run(token)