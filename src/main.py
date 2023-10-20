from dotenv import load_dotenv
import os
import discord
#import discord.ext
from discord.ext import commands
from discord import app_commands
import firebase_admin
from firebase_admin import db, credentials



# ref = db.reference("py/")
# users_ref = ref.child('Users')
# users_ref.set({
#     'TestName': {
#         'Coins': 99,
#         "attendance": 0
#     }
# })
#
# ref.get()
# db.reference("/Username")
#
# test_ref = users_ref.child('TestName')
# test_ref.update({
#     "Coins": 15
# })
# print(ref.get("/coins"))


# this loads the env file with the API key to be stored
# locally make sure you have your .env file set

load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')
firebase_url: str = os.getenv('FIREBASE_URL')

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": firebase_url})

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

ref = db.reference("py/")

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

@bot.command()
async def account(ctx, arg):
    if arg == "join":
        username = ctx.author.name
        users_ref = ref.child('Users')
        users_ref.update({
            username: {
                'Coins': 20,
                "attendance": 0
            }
        })
        await ctx.send(username)
    elif arg == "info":
        username = ctx.author.name
        ref.child(username)
        await ctx.send(ref.get("/coins"))
    else:
        await ctx.send("Not valid Command should be account join or info")


@bot.hybrid_command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(disc_token)  # runs the bot with the given api key
