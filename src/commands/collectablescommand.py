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
# locally make sure you have your .env file set in your scr directory
# you need two credentials.json files one in the scr and the other in the commands folder
load_dotenv('.env')
credential_path = "credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
cred = credentials.Certificate(credential_path)

db = firestore.Client()
users_ref = db.collection('users')  # reference to the users collection


class CollectablesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Collectables online")

    @app_commands.command(name='collectables')
    async def collectables(self, interaction: discord.Interaction):
        userid = str(interaction.user.id)
        user_ref = users_ref.document(userid)  # reference to the exact users document
        user_data = user_ref.get()

        if user_data: # if the user data exists
            users_collectables = user_data.get('collectables')

            embed = discord.Embed(title="Collectables",
                                  description='\n'.join(
                                      [f"{item} x {qty} " for item, qty in users_collectables.items()]),
                                  color=discord.Color.dark_purple())

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Make an account first please.")


async def setup(bot):
    await bot.add_cog(CollectablesCommand(bot))
