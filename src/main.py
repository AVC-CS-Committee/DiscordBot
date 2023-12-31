from dotenv import load_dotenv
import os
import discord
#import discord.ext
from discord.ext import commands
from discord import app_commands

# this loads the env file with the API key to be stored
# locally make sure you have your .env file set

load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print("bot is online")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Commands")
    except Exception as e:
        print(e)


@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello !", ephemeral=False)


@bot.command()
async def add(ctx, arg, arg2):
    arg3 = int(arg) + int(arg2)
    await ctx.send(arg3)


@bot.hybrid_command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(disc_token)  # runs the bot with the given api key
