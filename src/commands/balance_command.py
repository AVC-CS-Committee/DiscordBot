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


class BalanceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("balance online")

    @app_commands.command(name='balance', description="Used to check balance")
    @app_commands.checks.has_any_role("admin", "Moderator")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 10.0)
    async def balance(self, interaction: discord.Interaction):
        userid = str(interaction.user.id)
        user_ref = users_ref.document(userid)
        user_data = user_ref.get()

        if user_data is None:
            await interaction.response.send_message("You need to create an account to start")
        else:
            coins_value = user_data.get('coins')
            embed = discord.Embed(title="Balance", description=f"Coins: {coins_value}", color=discord.Color.dark_purple())
            await interaction.response.send_message(embed=embed)


    @balance.error
    async def bal_error(self, interation: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandTree):
            await interation.response.send_message(content=f"You can only do this command every 10.0 seconds {str(error)}",
                                                   ephemeral=True)
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await interation.response.send_message(content=f"You dont have the proper permissions {str(error)}",
                                                   ephemeral=True)
        else:
            await interation.response.send_message(content=f"Error occurred Try again in 10 seconds{str(error)}",
                                                   ephemeral=True)

async def setup(bot):
    await bot.add_cog(BalanceCommand(bot))
