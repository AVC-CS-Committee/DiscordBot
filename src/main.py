from dotenv import load_dotenv
import os
import discord
#import discord.ext
from discord.ext import commands
from discord import app_commands
import firebase_admin
from firebase_admin import db, credentials



# this loads the env file with the API key to be stored
# locally make sure you have your .env file set
load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')
firebase_url: str = os.getenv('FIREBASE_URL')

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": firebase_url})
db = firebase_admin.db.reference('/py/users')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!!', intents=intents)

#ref = db.reference("py/")
#db = firestore.client()

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
        users_ref = db
        users_ref.update({
            username: {
                'Coins': 20,
                'attendance': 0
            }
        })
        await ctx.send(username)
    elif arg == "info":
        username = ctx.author.name
        user_ref = db.child(username)  # Adjust the path as per your database structure

        user_data = user_ref.get()

        if user_data:
            coins_value = user_data.get('Coins')
            attendance_value = user_data.get('attendance')
            await ctx.send(f"User: {username}\nCoins: {coins_value}\nAttendance: {attendance_value}")
        else:
            await ctx.send("No data found for this user.")
    else:
        await ctx.send("Not a valid command. Should be 'account join' or 'account info'.")


@bot.command()
async def give(ctx, recipient: discord.Member, amount: int):
    # Get the sender's and recipient's usernames
    sender_username = ctx.author.name
    recipient_username = recipient.name

    # Check if the sender and recipient are the same user
    if sender_username == recipient_username:
        await ctx.send("You cannot send coins to yourself.")
        return

    # Create references to the sender's and recipient's user data
    sender_ref = db.child(sender_username)
    recipient_ref = db.child(recipient_username)

    # Check if the sender exists in the database
    sender_data = sender_ref.get()
    if sender_data is None:
        await ctx.send("Sender does not exist in the database.")
        return

    # Check if the recipient exists in the database
    recipient_data = recipient_ref.get()
    if recipient_data is None:
        await ctx.send("Recipient does not exist in the database.")
        return

    # Check if the sender has enough coins to send
    sender_coins = sender_data.get('Coins')
    if sender_coins < amount:
        await ctx.send("You do not have enough coins to send.")
        return

    # Update the sender's and recipient's coin balances
    sender_new_balance = sender_coins - amount
    recipient_coins = recipient_data.get('Coins')
    recipient_new_balance = recipient_coins + amount

    sender_ref.update({'Coins': sender_new_balance})
    recipient_ref.update({'Coins': recipient_new_balance})

    await ctx.send(f"{ctx.author.mention} sent {amount} coins to {recipient.mention}.")

@bot.hybrid_command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(disc_token)  # runs the bot with the given api key
