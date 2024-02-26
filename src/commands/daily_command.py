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
load_dotenv('.env')
credential_path = "credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
cred = credentials.Certificate(credential_path)

db = firestore.Client()
users_ref = db.collection('users')


class DailyCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Daily online")

    @app_commands.command(name='daily')
    @app_commands.checks.cooldown(1, 86400)
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        daily_coin = 5
        userid = str(interaction.user.id)  # gets users id to find the index
        user_path = f'users/{userid}'  # sets the path to the users id

        if user_path:
            user_ref = db.document(user_path)  # sets the ref to the users file
            user_data = user_ref.get()  # sets the ref for getting the users data for read only

            coin_bal = user_data.get('coins')  # reads the users data

            coin_new_bal = coin_bal + daily_coin  # adds users coins + the daily to make new amount

            user_ref.update({'coins': coin_new_bal})  # updates coins based on user ref

            await interaction.followup.send(f"You got {daily_coin} coins. Your new balance is {coin_new_bal}.")
        else:
            await interaction.followup.send("You need to make an account first, try /account create")


    @daily.error
    async def daily_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        await interaction.response.send_message(content=f"You can only do this command once a day {str(error)}",
                                                ephemeral=True)


async def setup(bot):
    await bot.add_cog(DailyCommand(bot))
