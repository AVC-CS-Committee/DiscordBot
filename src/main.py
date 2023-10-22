from dotenv import load_dotenv
import os
import discord
from discord import app_commands, guild
from discord.ext import commands, tasks
import asyncio
import firebase_admin
from firebase_admin import db, credentials, firestore

# this loads the env file with the API key to be stored
# locally make sure you have your .env file set
load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')
# firebase_url: str = os.getenv('FIREBASE_URL')


credential_path = "credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.Client()
users_ref = db.collection('users')

# cred = credentials.Certificate("credentials.json")
# firebase_admin.initialize_app(cred, {"databaseURL": firebase_url})
# db = firebase_admin.db.reference('/py/users')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!!', intents=intents)


@bot.event
async def on_ready():
    print("bot is online")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Commands")
    except Exception as e:
        print(e)


@bot.tree.command(name='hello')
@app_commands.checks.cooldown(1, 30.0)
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello !", ephemeral=False)


@bot.tree.command(name="daily", description="Daily coins")
@app_commands.checks.cooldown(1, 86400)
async def daily(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    daily_coin = 5
    userid = str(interaction.user.id)  # gets users id to find the index
    user_path = f'users/{userid}'  # sets the path to the users id

    if user_path:
        user_ref = db.document(user_path)  # sets the ref to the users file
        user_data = user_ref.get()  # sets the ref for getting the users data for read only

        coin_bal = user_data.get('Coins')  # reads the users data

        coin_new_bal = coin_bal + daily_coin  # adds users coins + the daily to make new amount

        user_ref.update({'Coins': coin_new_bal})  # updates coins based on user ref

        await interaction.followup.send(f"You got {daily_coin} coins. Your new balance is {coin_new_bal}.")
    else:
        await interaction.followup.send("You need to make an account first, try /account create")



@daily.error
async def daily_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message(content=f"You can only do this command once a day {str(error)}",
                                                ephemeral=True)


@bot.tree.command(name='account', description="Used to manage/create an account")
@app_commands.checks.cooldown(1, 60.0)
@app_commands.describe(arg="type 'Create' to make and account or 'Info' to see your account info")
async def account(interaction: discord.Interaction, arg: str):
    if arg.lower() == "create":
        userid = str(interaction.user.id)
        username = interaction.user.name

        user_ref = users_ref.document(userid)

        user_data = user_ref.get()

        if user_data.exists:
            await interaction.response.send_message('You already have an account.')
            return
        else:
            user_data = {
                'Username': username,
                'Coins': 20,
                'attendance': 0,
                'wins': 0,
                'loses': 0,
                'games played': 0
            }
            user_ref.set(user_data)
            await interaction.response.send_message(f"Account created for {username}")

    elif arg.lower() == "info":
        userid = str(interaction.user.id)
        user_ref = users_ref.document(userid)

        user_data = user_ref.get()

        if user_data.exists:
            username = user_data.get('Username')
            coins_value = user_data.get('Coins')
            attendance_value = user_data.get('attendance')
            await interaction.response.send_message(
                f"User: {username}\nCoins: {coins_value}\nAttendance: {attendance_value}", ephemeral=True)
        else:
            await interaction.response.send_message("No data found for this user.")
    else:
        await interaction.response.send_message("Not a valid command. Should be 'account create' or 'account info'.")


@account.error
async def acc_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandTree):
        await interaction.response.send_message(content=f"You can only do this command every 60.0 seconds {str(error)}",
                                                ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Error occurred Try again in 60 seconds {str(error)}",
                                                ephemeral=True)


@bot.tree.command(name='balance', description="Used to check balance")
# @app_commands.checks.has_any_role("admin", "Moderator")
# @app_commands.checks.has_permissions(manage_messages=True)
@app_commands.checks.cooldown(1, 10.0)
async def balance(interaction: discord.Interaction):
    userid = str(interaction.user.id)
    user_ref = users_ref.document(userid)
    user_data = user_ref.get()

    if user_data is None:
        await interaction.response.send_message("You need to create an account to start")
    else:
        coins_value = user_data.get('Coins')
        await interaction.response.send_message(f"Your AVC coin balance is **{coins_value}**")


@balance.error
async def bal_error(interation: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandTree):
        await interation.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
                                               ephemeral=True)
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await interation.response.send_message(content=f"You dont have the proper permissions {str(error)}",
                                               ephemeral=True)
    else:
        await interation.response.send_message(content=f"Error occurred Try again in 10 seconds{str(error)}",
                                               ephemeral=True)


@bot.tree.command(name='give', description="Used to give coins")
@app_commands.checks.cooldown(1, 10.0)
@app_commands.describe(recipient="recipient's @", amount="Amount of coins to give")
async def give(interaction: discord.Interaction, recipient: discord.User, amount: int):
    try:
        if amount < 1:
            await interaction.response.send_message("Only enter valid numbers")
            return
        sender_id = interaction.user.id
        recipient_id = recipient.id

        if sender_id == recipient_id:
            await interaction.response.send_message("You cannot send coins to yourself.")
            return

        # Construct paths for the sender and recipient
        sender_path = f'users/{sender_id}'
        recipient_path = f'users/{recipient_id}'

        sender_ref = db.document(sender_path)
        recipient_ref = db.document(recipient_path)

        # Check if the sender and recipient exist in the database
        sender_data = sender_ref.get()
        recipient_data = recipient_ref.get()

        if sender_data is None:
            await interaction.response.send_message("Sender does not exist in the database.")
            return

        if recipient_data is None:
            await interaction.response.send_message("Recipient does not exist in the database.")
            return

        sender_coins = sender_data.get('coins')
        if sender_coins < amount:
            await interaction.response.send_message("You do not have enough coins to send.")
            return

        sender_new_balance = sender_coins - amount
        recipient_coins = recipient_data.get('Coins')
        recipient_new_balance = recipient_coins + amount

        sender_ref.update({'Coins': sender_new_balance})
        recipient_ref.update({'Coins': recipient_new_balance})

        sender_name = interaction.user.name
        recipient_name = recipient.name

        await interaction.response.send_message(f"{sender_name} sent {amount} coins to {recipient_name}.")
    except ValueError:
        await interaction.response.send_message(
            "Invalid recipient. Please mention a valid user in the format `@username`.")


@give.error
async def give_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandTree):
        await interaction.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
                                                ephemeral=True)
    else:
        await interaction.response.send_message(content="Error occurred Try again in 10 seconds", ephemeral=True)


@bot.command()
async def add(ctx, arg, arg2):
    arg3 = int(arg) + int(arg2)
    await ctx.send(arg3)


bot.run(disc_token)  # runs the bot with the given api key
