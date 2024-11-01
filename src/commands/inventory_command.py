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

# Cache setup for user inventory data
inventory_cache = defaultdict(lambda: {"data": None, "timestamp": 0})
CACHE_DURATION = 60  # Cache duration in seconds


class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Inventory online")

    async def get_user_inventory(self, user_id):
        # Check if cache is valid
        current_time = time.time()
        if inventory_cache[user_id]["data"] and (current_time - inventory_cache[user_id]["timestamp"]) < CACHE_DURATION:
            return inventory_cache[user_id]["data"]

        # Fetch fresh data from Firestore if cache has expired
        user_ref = users_ref.document(user_id)
        user_data = user_ref.get()

        if user_data.exists:
            inv = user_data.get('inventory')
            inventory_cache[user_id] = {"data": inv, "timestamp": current_time}
            return inv
        else:
            return None

    @app_commands.command(name='inventory')
    async def inventory(self, interaction: discord.Interaction):
        try:
            user_id = str(interaction.user.id)
            user_inventory = await self.get_user_inventory(user_id)

            if user_inventory:
                embed = discord.Embed(
                    title="Inventory",
                    description='\n'.join([f"{item} x {qty}" for item, qty in user_inventory.items()]),
                    color=discord.Color.dark_purple()
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Make an account first please.")
        except Exception as e:
            print(e)
            await interaction.response.send_message("An error occurred.")


async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
