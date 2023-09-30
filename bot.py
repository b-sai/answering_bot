import discord
from dotenv import load_dotenv
import os
from discord.ext import commands

load_dotenv()

token = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    

async def get_last_n_msgs(n: int, channel_id: int):
    channel = bot.get_channel(channel_id)
    async for msg in channel.history(limit=n):
        print(f"{msg.author}: {msg.content}")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if message.content.endswith('?'):
        channel = message.channel
        await get_last_n_msgs(5, channel.id)
        await message.channel.send('Hello!')

bot.run(token)