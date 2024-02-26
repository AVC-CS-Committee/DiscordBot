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


class InventoryCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Inventory online")

    @app_commands.command(name='inventory')
    async def inventory(self, interaction: discord.Interaction):
        userid = str(interaction.user.id)
        user_ref = users_ref.document(userid)
        user_data = user_ref.get()

        if user_data:
            inv = user_data.get('inventory')

            embed = discord.Embed(title="Inventory",
                                  description='\n'.join([f"{item} x {qty} " for item, qty in inv.items()]),
                                  color=discord.Color.dark_purple())

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Make an account first please.")

async def setup(bot):
    await bot.add_cog(InventoryCommand(bot))
