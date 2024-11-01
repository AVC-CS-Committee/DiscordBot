from dotenv import load_dotenv
import os
import discord
from discord import app_commands
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, firestore
import time
from collections import defaultdict

# Load environment variables and credentials
load_dotenv('.env')
credential_path = "credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
cred = credentials.Certificate(credential_path)

# Initialize Firestore
db = firestore.Client()
users_ref = db.collection('users')

# Cache setup for leaderboard data
leaderboard_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 1800  # (30 mins) Cache duration in seconds


class LeaderboardCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Leaderboard online")

    async def get_leaderboard_data(self):
        # Check if cache is valid
        current_time = time.time()
        if leaderboard_cache["data"] and (current_time - leaderboard_cache["timestamp"]) < CACHE_DURATION:
            return leaderboard_cache["data"]

        # Fetch fresh data from Firestore if cache has expired
        leaderboard_query = users_ref.order_by('coins', direction=firestore.Query.DESCENDING).limit(10)
        leaderboard_data = leaderboard_query.stream()

        # Format leaderboard data
        leaderboard_list = []
        position = 1
        for doc in leaderboard_data:
            user_data = doc.to_dict()
            username = user_data.get('username', 'Unknown')
            coins = user_data.get('coins', 0)
            leaderboard_list.append(f"{position}. {username}: {coins} coins")
            position += 1

        # Update cache with new data
        leaderboard_message = "Leaderboard:\n" + "\n".join(leaderboard_list)
        leaderboard_cache["data"] = leaderboard_message
        leaderboard_cache["timestamp"] = current_time

        return leaderboard_message

    @app_commands.command(name='leaderboard')
    @app_commands.checks.cooldown(1, 30)
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        leaderboard_message = await self.get_leaderboard_data()
        await interaction.followup.send(leaderboard_message)


async def setup(bot):
    await bot.add_cog(LeaderboardCommand(bot))
