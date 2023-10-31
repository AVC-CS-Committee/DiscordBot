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

@bot.tree.command(name="craft_test")
async def craft_test(interaction: discord.Interaction):

    userid = str(interaction.user.id)
    user_ref = users_ref.document(userid)
    user_data = user_ref.get()

    if user_data:
        inv = user_data.get("inventory")
        items_ref = db.collection('items')
        item_ref = items_ref.document()
        item_data = item_ref.get()
        item_list = item_data.to.list()
        keys = list(inv.keys())

        for i in item_data:
            if keys == item_list:
                await interaction.response.send_message("Item Crafted", ephemeral=True)
                return
            else:
                await interaction.response.send_message("Item Not Crafted", ephemeral=True)
                return
@bot.tree.command(name='inv_test')
async def inv_test(interaction: discord.Interaction):
    userid = str(interaction.user.id)
    user_ref = users_ref.document(userid)
    user_data = user_ref.get()

    if user_data:
        inv = user_data.get('inventory')
        keys = list(inv.keys())
        values = list(inv.values())
        inv_string = ""
        for i in range(len(inv)):
            inv_string += f"{keys[i]} x {values[i]}\n"

        embed = discord.Embed(title="Inventory", description=f"{inv_string}", color=discord.Color.dark_purple())

        await interaction.response.send_message(embed=embed)


@bot.tree.command(name='leaderboard', description='Leaderboard')
@app_commands.checks.cooldown(1, 30)
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)

    users_ref = db.collection('users')

    # (order by 'Coins' field in descending order)
    leaderboard_query = users_ref.order_by('Coins', direction=firestore.Query.DESCENDING).limit(10)

    leaderboard_data = leaderboard_query.stream()

    if not leaderboard_data:
        await interaction.followup.send("No users found in the leaderboard.")
        return

    leaderboard_message = "Leaderboard:\n"
    position = 1

    for doc in leaderboard_data:
        user_data = doc.to_dict()
        username = user_data['username']
        coins = user_data['coins']
        leaderboard_message += f"{position}. {username}: {coins} coins\n"
        position += 1

    await interaction.followup.send(leaderboard_message)


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
@app_commands.checks.cooldown(1, 1.0)
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
            # sample user info
            sample_user_ref = db.collection('users').document('sample')
            sample_user_data = sample_user_ref.get()

            # makes sure sample user file is there
            if sample_user_data.exists:
                sample_user_dict = sample_user_data.to_dict()

                sample_user_dict['username'] = username  # sets username to the users name
                new_user_ref = db.collection('users').document(userid)
                new_user_ref.set(sample_user_dict)

                await interaction.response.send_message(f"Account created for {username}")

    elif arg.lower() == "info":
        userid = str(interaction.user.id)
        user_ref = users_ref.document(userid)

        user_data = user_ref.get()

        if user_data.exists:
            username = user_data.get('username')
            coins_value = user_data.get('coins')
            attendance_value = user_data.get('attendance')
            embed = discord.Embed(title="Account Info",
                                  description=f"User: {username}\nCoins: {coins_value}\nAttendance: {attendance_value}",
                                  color=discord.Color.dark_purple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("No data found for this user.")
    else:
        await interaction.response.send_message("Not a valid command. Should be 'account create' or 'account info'.")


@bot.tree.command(name='user_update', description="Used to update all users")
@app_commands.checks.cooldown(1, 1800.0)
@app_commands.checks.has_role('DB')
@app_commands.checks.has_permissions(administrator=True)
async def user_update(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)

    sample_user_ref = db.collection('users').document('sample')
    sample_user_data = sample_user_ref.get()

    if sample_user_data.exists:
        sample_user_dict = sample_user_data.to_dict()
        users_ref = db.collection('users')
        users = users_ref.stream()

        for user in users:
            user_id = user.id
            user_ref = db.collection('users').document(user_id)
            user_data = user_ref.get()

            if user_data.exists:
                user_dict = user_data.to_dict()
                sample_user_dict.pop('username', None)
                user_dict.update(sample_user_dict)
                user_ref.set(user_dict)

                print(f"Updated user {user_id}")

        await interaction.followup.send("Updated all users.")
    else:
        await interaction.followup.send("No template user found.")


@user_update.error
async def user_update_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message("You dont have the required roles for this command", ephemeral=True)


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
        coins_value = user_data.get('coins')
        embed = discord.Embed(title="Balance", description=f"Coins: {coins_value}", color=discord.Color.dark_purple())
        await interaction.response.send_message(embed=embed)


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
        if amount < 0:
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
        recipient_coins = recipient_data.get('coins')
        recipient_new_balance = recipient_coins + amount

        sender_ref.update({'coins': sender_new_balance})
        recipient_ref.update({'coins': recipient_new_balance})

        sender_name = interaction.user.name
        recipient_name = recipient.name

        await interaction.response.send_message(f"{sender_name} sent {amount} coins to {recipient_name}.")
    except ValueError:
        await interaction.response.send_message(
            "Not valid Username.")


@give.error
async def give_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandTree):
        await interaction.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
                                                ephemeral=True)
    else:
        await interaction.response.send_message(content=f"Error occurred Try again in 10 seconds {str(error)}",
                                                ephemeral=True)


@bot.command()
async def add(ctx, arg, arg2):
    arg3 = int(arg) + int(arg2)
    await ctx.send(arg3)


bot.run(disc_token)  # runs the bot with the given api key
