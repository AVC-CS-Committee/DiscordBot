from dotenv import load_dotenv
import os
import discord
# import discord.ext
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


# ref = db.reference("py/")
# db = firestore.client()

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
        userid = str(ctx.author.id)
        username = ctx.author.name

        user_ref = db.child('users').child(userid)
        user_data = user_ref.get()

        if user_data:   # check for account existence
            await ctx.send('You already have an account')
            return
        else:
            users_ref = db.child('users')  # Adjust path if needed for database
            user_path = users_ref.child(userid)
            user_data = {
                'Username': username,
                'Coins': 20,
                'attendance': 0
            }
            user_path.set(user_data)
            await ctx.send(f"Account created for {username}")

    elif arg == "info":
        userid = str(ctx.author.id)
        user_ref = db.child('users').child(userid)  #  Adjust path if needed for database
        user_data = user_ref.get()

        if user_data:
            username = user_data.get('Username')
            coins_value = user_data.get('Coins')
            attendance_value = user_data.get('attendance')
            await ctx.send(f"User: {username}\nCoins: {coins_value}\nAttendance: {attendance_value}")
        else:
            await ctx.send("No data found for this user.")
    else:
        await ctx.send("Not a valid command. Should be 'account join' or 'account info'.")



@bot.command()
async def give(ctx, recipient: discord.User, amount: int):
    try:
        sender_id = ctx.author.id
        recipient_id = recipient.id

        if sender_id == recipient_id:
            await ctx.send("You cannot send coins to yourself.")
            return

        # Construct paths for the sender and recipient
        sender_path = f'users/{sender_id}'
        recipient_path = f'users/{recipient_id}'

        sender_ref = db.child(sender_path)
        recipient_ref = db.child(recipient_path)

        # Check if the sender and recipient exist in the database
        sender_data = sender_ref.get()
        recipient_data = recipient_ref.get()

        if sender_data is None:
            await ctx.send("Sender does not exist in the database.")
            return

        if recipient_data is None:
            await ctx.send("Recipient does not exist in the database.")
            return

        sender_coins = sender_data.get('Coins')
        if sender_coins < amount:
            await ctx.send("You do not have enough coins to send.")
            return

        sender_new_balance = sender_coins - amount
        recipient_coins = recipient_data.get('Coins')
        recipient_new_balance = recipient_coins + amount

        sender_ref.update({'Coins': sender_new_balance})
        recipient_ref.update({'Coins': recipient_new_balance})

        sender_name = ctx.author.name
        recipient_name = recipient.name

        await ctx.send(f"{sender_name} sent {amount} coins to {recipient_name}.")
    except ValueError:
        await ctx.send("Invalid recipient. Please mention a valid user in the format `@username`.")



@bot.hybrid_command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(disc_token)  # runs the bot with the given api key
