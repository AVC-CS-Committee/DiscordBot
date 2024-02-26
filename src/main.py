from dotenv import load_dotenv
import os
import discord
from discord.ext import commands, tasks
import asyncio

# this loads the env file with the API key to be stored
# locally make sure you have your .env file set
load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='!!', intents=intents)


async def load():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')

async def main():
    await load()
    await bot.start(disc_token)
@bot.event
async def on_ready():
    print("bot is online")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Commands")
        for command in synced:
            print(command.name)
    except Exception as e:
        print(e)
asyncio.run(main())
#
#
# @bot.tree.command(name='hello')
# @app_commands.checks.cooldown(1, 30.0)
# async def hello(interaction: discord.Interaction):
#     await interaction.response.send_message(f"Hello !", ephemeral=False)
#
#
# @bot.tree.command(name='collectables')
# async def collectables(interaction: discord.Interaction):
#     userid = str(interaction.user.id)
#     user_ref = users_ref.document(userid)
#     user_data = user_ref.get()
#
#     if user_data:
#         collec = user_data.get('collectables')
#
#         embed = discord.Embed(title="Collectables",
#                               description='\n'.join([f"{item} x {qty} " for item, qty in collec.items()]),
#                               color=discord.Color.dark_purple())
#
#         await interaction.response.send_message(embed=embed)
#     else:
#         await interaction.response.send_message("Make an account first please.")
#
#
# @bot.tree.command(name='craft')
# async def craft(interaction: discord.Interaction):
#     userid = interaction.user.id
#     user_path = f'users/{userid}'  # Construct user document path as a string
#     user_ref = db.document(user_path)
#     user_data = user_ref.get()
#     temp = 'Slot Machine'
#
#     if user_data.exists:
#         inv = user_data.get('inventory')
#         collectables_ref = db.collection('collectables')
#         craft_ref = collectables_ref.document(temp)
#         craft_data = craft_ref.get()
#         craft_list = craft_data.get('requirements')
#         missing_items = {}
#
#         for key, value in craft_list.items():
#             if key in inv:
#                 qty_needed = value - inv[key]
#                 if qty_needed > 0:
#                     missing_items[key] = qty_needed
#             else:
#                 missing_items[key] = value
#
#         if not missing_items:
#             # User has all required items, so update collectables and remove items from inventory
#             user_collectables = user_data.get('collectables')
#             user_collectables[temp] = user_collectables.get(temp, 0) + 1  # Increment collectables
#
#             # Update the collectables in the user's document
#             user_ref.update({'collectables': user_collectables})
#
#             # Remove the required items from the inventory
#             for key, value in craft_list.items():
#                 inv[key] -= value
#
#             # Update the inventory in the user's document
#             user_ref.update({'inventory': inv})
#
#             await interaction.response.send_message("You have successfully crafted a Slot Machine.")
#         else:
#             missing_items_str = '\n'.join([f"{item} x {qty} " for item, qty in missing_items.items()])
#             await interaction.response.send_message(f"You are missing:\n{missing_items_str}")
#     else:
#         await interaction.response.send_message("User not found.")
#
#
# @bot.tree.command(name='leaderboard', description='Leaderboard')
# @app_commands.checks.cooldown(1, 30)
# async def leaderboard(interaction: discord.Interaction):
#     await interaction.response.defer(ephemeral=False)
#
#     users_ref = db.collection('users')
#
#     # (order by 'coins' field in descending order)
#     leaderboard_query = users_ref.order_by('coins', direction=firestore.Query.DESCENDING).limit(10)
#
#     leaderboard_data = leaderboard_query.stream()
#
#     if not leaderboard_data:
#         await interaction.followup.send("No users found in the leaderboard.")
#         return
#
#     leaderboard_message = "Leaderboard:\n"
#     position = 1
#
#     for doc in leaderboard_data:
#         user_data = doc.to_dict()
#         username = user_data['username']
#         coins = user_data['coins']
#         leaderboard_message += f"{position}. {username}: {coins} coins\n"
#         position += 1
#
#     await interaction.followup.send(leaderboard_message)
#
#
# @bot.tree.command(name="daily", description="Daily coins")
# @app_commands.checks.cooldown(1, 86400)
# async def daily(interaction: discord.Interaction):
#     await interaction.response.defer(ephemeral=False)
#     daily_coin = 5
#     userid = str(interaction.user.id)  # gets users id to find the index
#     user_path = f'users/{userid}'  # sets the path to the users id
#
#     if user_path:
#         user_ref = db.document(user_path)  # sets the ref to the users file
#         user_data = user_ref.get()  # sets the ref for getting the users data for read only
#
#         coin_bal = user_data.get('coins')  # reads the users data
#
#         coin_new_bal = coin_bal + daily_coin  # adds users coins + the daily to make new amount
#
#         user_ref.update({'coins': coin_new_bal})  # updates coins based on user ref
#
#         await interaction.followup.send(f"You got {daily_coin} coins. Your new balance is {coin_new_bal}.")
#     else:
#         await interaction.followup.send("You need to make an account first, try /account create")
#
#
# @daily.error
# async def daily_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
#     await interaction.response.send_message(content=f"You can only do this command once a day {str(error)}",
#                                             ephemeral=True)
#
#
# @bot.tree.command(name='account', description="Used to manage/create an account")
# @app_commands.checks.cooldown(1, 1.0)
# @app_commands.describe(arg="type 'Create' to make and account or 'Info' to see your account info")
# async def account(interaction: discord.Interaction, arg: str):
#     if arg.lower() == "create":
#         userid = str(interaction.user.id)
#         username = interaction.user.name
#
#         user_ref = users_ref.document(userid)
#
#         user_data = user_ref.get()
#
#         if user_data.exists:
#             await interaction.response.send_message('You already have an account.')
#             return
#         else:
#             # sample user info
#             sample_user_ref = db.collection('users').document('sample')
#             sample_user_data = sample_user_ref.get()
#
#             # makes sure sample user file is there
#             if sample_user_data.exists:
#                 sample_user_dict = sample_user_data.to_dict()
#
#                 sample_user_dict['username'] = username  # sets username to the users name
#                 new_user_ref = db.collection('users').document(userid)
#                 new_user_ref.set(sample_user_dict)
#
#                 await interaction.response.send_message(f"Account created for {username}")
#
#     elif arg.lower() == "info":
#         userid = str(interaction.user.id)
#         user_ref = users_ref.document(userid)
#
#         user_data = user_ref.get()
#
#         if user_data.exists:
#             username = user_data.get('username')
#             coins_value = user_data.get('coins')
#             attendance_value = user_data.get('attendance')
#             embed = discord.Embed(title="Account Info",
#                                   description=f"User: {username}\nCoins: {coins_value}\nAttendance: {attendance_value}",
#                                   color=discord.Color.dark_purple())
#             await interaction.response.send_message(embed=embed, ephemeral=True)
#         else:
#             await interaction.response.send_message("No data found for this user.")
#     else:
#         await interaction.response.send_message("Not a valid command. Should be 'account create' or 'account info'.")
#
#
# @bot.tree.command(name='user_update', description="Used to update all users")
# @app_commands.checks.cooldown(1, 10.0)
# @app_commands.checks.has_role('DB')
# @app_commands.checks.has_permissions(administrator=True)
# async def user_update(interaction: discord.Interaction):
#     await interaction.response.defer(ephemeral=False)
#
#     sample_user_ref = db.collection('users').document('sample')
#     sample_user_data = sample_user_ref.get()
#
#     if sample_user_data.exists:
#         sample_user_dict = sample_user_data.to_dict()
#         users_ref = db.collection('users')
#         users = users_ref.stream()
#
#         for user in users:
#             user_id = user.id
#             user_ref = db.collection('users').document(user_id)
#             user_data = user_ref.get()
#
#             if user_data.exists:
#                 user_dict = user_data.to_dict()
#
#                 # Preserve the user's existing username
#                 sample_user_dict.pop('username', None)
#
#                 # Merge the old and new data manually
#                 for key, value in sample_user_dict.items():
#                     if key not in user_dict:
#                         user_dict[key] = value
#                     elif key == 'inventory' and isinstance(value, dict) and isinstance(user_dict.get(key), dict):
#                         # Merge the inventory maps, preserving existing values
#                         for item, quantity in value.items():
#                             user_dict[key][item] = user_dict[key].get(item, 0) + quantity
#                     elif key == 'collectables' and isinstance(value, dict) and isinstance(user_dict.get(key), dict):
#                         # Merge the collectables maps, preserving existing values
#                         for collectable, count in value.items():
#                             user_dict[key][collectable] = user_dict[key].get(collectable, 0) + count
#
#                 user_ref.set(user_dict)
#
#                 print(f"Updated user {user_id}")
#
#         await interaction.followup.send("Updated all users.")
#     else:
#         await interaction.followup.send("No template user found.")
#
#
# @user_update.error
# async def user_update_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
#     await interaction.response.send_message(f"You dont have the required roles for this command{error}", ephemeral=True)
#
#
# @account.error
# async def acc_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
#     if isinstance(error, discord.app_commands.CommandTree):
#         await interaction.response.send_message(content=f"You can only do this command every 60.0 seconds {str(error)}",
#                                                 ephemeral=True)
#     else:
#         await interaction.response.send_message(content=f"Error occurred Try again in 60 seconds {str(error)}",
#                                                 ephemeral=True)
#
#
# @bot.tree.command(name='balance', description="Used to check balance")
# # @app_commands.checks.has_any_role("admin", "Moderator")
# # @app_commands.checks.has_permissions(manage_messages=True)
# @app_commands.checks.cooldown(1, 10.0)
# async def balance(interaction: discord.Interaction):
#     userid = str(interaction.user.id)
#     user_ref = users_ref.document(userid)
#     user_data = user_ref.get()
#
#     if user_data is None:
#         await interaction.response.send_message("You need to create an account to start")
#     else:
#         coins_value = user_data.get('coins')
#         embed = discord.Embed(title="Balance", description=f"Coins: {coins_value}", color=discord.Color.dark_purple())
#         await interaction.response.send_message(embed=embed)
#
#
# @balance.error
# async def bal_error(interation: discord.Interaction, error: app_commands.AppCommandError):
#     if isinstance(error, discord.app_commands.CommandTree):
#         await interation.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
#                                                ephemeral=True)
#     elif isinstance(error, discord.app_commands.MissingPermissions):
#         await interation.response.send_message(content=f"You dont have the proper permissions {str(error)}",
#                                                ephemeral=True)
#     else:
#         await interation.response.send_message(content=f"Error occurred Try again in 10 seconds{str(error)}",
#                                                ephemeral=True)
#
#
# @bot.tree.command(name='give', description="Used to give coins")
# @app_commands.checks.cooldown(1, 10.0)
# @app_commands.describe(recipient="recipient's @", amount="Amount of coins to give")
# async def give(interaction: discord.Interaction, recipient: discord.User, amount: int):
#     try:
#         if amount < 0:
#             await interaction.response.send_message("Only enter valid numbers")
#             return
#         sender_id = interaction.user.id
#         recipient_id = recipient.id
#
#         if sender_id == recipient_id:
#             await interaction.response.send_message("You cannot send coins to yourself.")
#             return
#
#         # Construct paths for the sender and recipient
#         sender_path = f'users/{sender_id}'
#         recipient_path = f'users/{recipient_id}'
#
#         sender_ref = db.document(sender_path)
#         recipient_ref = db.document(recipient_path)
#
#         # Check if the sender and recipient exist in the database
#         sender_data = sender_ref.get()
#         recipient_data = recipient_ref.get()
#
#         if sender_data is None:
#             await interaction.response.send_message("Sender does not exist in the database.")
#             return
#
#         if recipient_data is None:
#             await interaction.response.send_message("Recipient does not exist in the database.")
#             return
#
#         sender_coins = sender_data.get('coins')
#         if sender_coins < amount:
#             await interaction.response.send_message("You do not have enough coins to send.")
#             return
#
#         sender_new_balance = sender_coins - amount
#         recipient_coins = recipient_data.get('coins')
#         recipient_new_balance = recipient_coins + amount
#
#         sender_ref.update({'coins': sender_new_balance})
#         recipient_ref.update({'coins': recipient_new_balance})
#
#         sender_name = interaction.user.name
#         recipient_name = recipient.name
#
#         await interaction.response.send_message(f"{sender_name} sent {amount} coins to {recipient_name}.")
#     except ValueError:
#         await interaction.response.send_message(
#             "Not valid Username.")
#
#
# @give.error
# async def give_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
#     if isinstance(error, discord.app_commands.CommandTree):
#         await interaction.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
#                                                 ephemeral=True)
#     else:
#         await interaction.response.send_message(content=f"Error occurred Try again in 10 seconds {str(error)}",
#                                                 ephemeral=True)
#
#
# @bot.command()
# async def add(ctx, arg, arg2):
#     arg3 = int(arg) + int(arg2)
#     await ctx.send(arg3)

