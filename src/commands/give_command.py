from dotenv import load_dotenv
import os
import discord
from discord import app_commands, guild
from discord.ext import commands, tasks
import asyncio
import firebase_admin
from firebase_admin import db, credentials, firestore
import src

# this loads the env file with the API key to be stored
# locally make sure you have your .env file set
load_dotenv('../.env')
credential_path = "credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
cred = credentials.Certificate(credential_path)

db = firestore.Client()
users_ref = db.collection('users')


class give_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("give online")

    @app_commands.command(name='give', description="Used to give coins")
    @app_commands.checks.cooldown(1, 10.0)
    @app_commands.describe(recipient="recipient's @", amount="Amount of coins to give")
    async def give(self, interaction: discord.Interaction, recipient: discord.User, amount: int):
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
    async def give_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandTree):
            await interaction.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(content=f"Error occurred Try again in 10 seconds {str(error)}",
                                                    ephemeral=True)

async def setup(bot):
    await bot.add_cog(give_command(bot))
