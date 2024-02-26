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


class UserUpdateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("user update online")

    @app_commands.command(name='user_update', description="Used to update all users")
    @app_commands.checks.cooldown(1, 10.0)
    @app_commands.checks.has_role('DB')
    @app_commands.checks.has_permissions(administrator=True)
    async def user_update(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        sample_user_ref = db.collection('users').document('sample')
        sample_user_data = sample_user_ref.get()

        if sample_user_data.exists:
            sample_user_dict = sample_user_data.to_dict()
            users_ref = db.collection('users')
            users = users_ref.stream()

            for user in users:
                user_id = user.id
                user_ref = db.collection('users').document(user_id)
                user_data = user_ref.get()

                if user_data.exists:
                    user_dict = user_data.to_dict()

                    # Preserve the user's existing username
                    sample_user_dict.pop('username', None)

                    # Merge the old and new data manually
                    for key, value in sample_user_dict.items():
                        if key not in user_dict:
                            user_dict[key] = value
                        elif key == 'inventory' and isinstance(value, dict) and isinstance(user_dict.get(key), dict):
                            # Merge the inventory maps, preserving existing values
                            for item, quantity in value.items():
                                user_dict[key][item] = user_dict[key].get(item, 0) + quantity
                        elif key == 'collectables' and isinstance(value, dict) and isinstance(user_dict.get(key), dict):
                            # Merge the collectables maps, preserving existing values
                            for collectable, count in value.items():
                                user_dict[key][collectable] = user_dict[key].get(collectable, 0) + count

                    user_ref.set(user_dict)

                    print(f"Updated user {user_id}")

            await interaction.followup.send("Updated all users.")
        else:
            await interaction.followup.send("No template user found.")

    @user_update.error
    async def user_update_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "You don't have the required roles or permissions for this command.", ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message("This command is on cooldown. Please try again later.",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(UserUpdateCommand(bot))
