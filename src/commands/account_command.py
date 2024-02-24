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


class account_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Account online")

    @app_commands.command(name='account')
    async def account(self, interaction: discord.Interaction, arg: str):
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

async def setup(bot):
    await bot.add_cog(account_command(bot))
