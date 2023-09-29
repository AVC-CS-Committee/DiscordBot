# This example requires the 'message_content' intent.
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands


#this loads the env file with the API key to be stored locally make sure you have your .env file set
load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')
channel_id = 1096188770421846038


intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents=intents)

@bot.event
async def on_ready():
    print("bot is online")


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(disc_token) #runs the bot with the given api key