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


class LeaderboardCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("leaderboard online")

    @app_commands.command(name='leaderboard')
    @app_commands.checks.cooldown(1, 30)
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        # (order by 'coins' field in descending order)
        leaderboard_query = users_ref.order_by('coins', direction=firestore.Query.DESCENDING).limit(10)

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


async def setup(bot):
    await bot.add_cog(LeaderboardCommand(bot))
