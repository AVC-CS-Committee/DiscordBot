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


class CraftCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("craft online")
    @app_commands.command(name='craft')
    async def craft(self, interaction: discord.Interaction):
        userid = interaction.user.id
        user_path = f'users/{userid}'  # Construct user document path as a string
        user_ref = db.document(user_path)
        user_data = user_ref.get()
        temp = 'Slot Machine'

        if user_data.exists:
            inv = user_data.get('inventory')
            collectables_ref = db.collection('collectables')
            craft_ref = collectables_ref.document(temp)
            craft_data = craft_ref.get()
            craft_list = craft_data.get('requirements')
            missing_items = {}

            for key, value in craft_list.items():
                if key in inv:
                    qty_needed = value - inv[key]
                    if qty_needed > 0:
                        missing_items[key] = qty_needed
                else:
                    missing_items[key] = value

            if not missing_items:
                # User has all required items, so update collectables and remove items from inventory
                user_collectables = user_data.get('collectables')
                user_collectables[temp] = user_collectables.get(temp, 0) + 1  # Increment collectables

                # Update the collectables in the user's document
                user_ref.update({'collectables': user_collectables})

                # Remove the required items from the inventory
                for key, value in craft_list.items():
                    inv[key] -= value

                # Update the inventory in the user's document
                user_ref.update({'inventory': inv})

                await interaction.response.send_message("You have successfully crafted a Slot Machine.")
            else:
                missing_items_str = '\n'.join([f"{item} x {qty} " for item, qty in missing_items.items()])
                await interaction.response.send_message(f"You are missing:\n{missing_items_str}")
        else:
            await interaction.response.send_message("User not found.")

async def setup(bot):
    await bot.add_cog(CraftCommand(bot))
