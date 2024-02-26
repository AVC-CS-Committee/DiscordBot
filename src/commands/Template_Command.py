import asyncio

from discord.ext import commands
from dotenv import load_dotenv

# this loads the env file with the API key to be stored
# locally make sure you have your .env file set
load_dotenv('../.env')


# this is the template command file, this is NOT a slash command, this is a normal command that is called with a prefix
# the prefix is set in the main.py file
# the prefix is the character that comes before the command
# for example if the prefix is "!!" then the command would be called like this
# !!template

# if you want to use slash commands, commands you can see when you type / in the chat refer to other files in the folder
# for example account_command.py they are more complex and require more setup

class TemplateCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("template online")

    # Command goes here how to respond to the users command delete_after=x will delete the message after x seconds,
    # remove if not needed should be used on menus to keep chat clean
    # arg1 and arg2 are the arguments that the user can pass to the command, you can add more arguments if needed
    # arg1 can be anything, arg2 is a string, you can change the type of the argument to int, float, etc.
    # you can also add default values to the arguments, for example arg2: str = "default value"
    # if the user does not pass a value for arg2, it will default to "default value"
    # you can get users name, id, etc. with ctx.author.name, ctx.author.id, etc.
    # you can get the channel id, name, etc. with ctx.channel.name, ctx.channel.id, etc.
    # can also get the guild id, name, etc. with ctx.guild.name, ctx.guild.id, etc.

    @commands.command(name='template', description="Template command for new commands")
    async def template(self, ctx, arg1, arg2: str = "hello"):
        username = ctx.author.name
        channelid = ctx.channel.id
        channelname = ctx.channel.name
        guildid = ctx.guild.id
        guildname = ctx.guild.name

        message = await ctx.send(
            f"Hello {username} you called the command in the channel {channelname} with the id {channelid} in the guild "
            f"{guildname} with the id {guildid} and passed the arguments {arg1} and {arg2}")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2', '3']

        # this is how you can wait for a response from the user, you can add a timeout to the wait_for function
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await message.edit('You did not reply in time.',delete_after=20)
        else:
            if msg.content == '1':
                await message.edit(content='You selected option 1. Now choose between 4, 5, 6.', delete_after=10)
            elif msg.content == '2':
                await message.edit(content='You selected option 2. Now choose between 4, 5, 6.', delete_after=10)
            elif msg.content == '3':
                await message.edit(content='You selected option 3. Now choose between 4, 5, 6.', delete_after=10)

            # this is how you can wait for a response from the user again can be done over and over
            def check2(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content in ['4', '5', '6']

            try:
                msg2 = await self.bot.wait_for('message', check=check2, timeout=60.0)
            except asyncio.TimeoutError:
                await message.edit('You did not reply in time.', delete_after=20)
            else:
                if msg2.content == '4':
                    await message.edit(content='You selected option 4.', delete_after=10)
                elif msg2.content == '5':
                    await message.edit(content='You selected option 5.', delete_after=10)
                elif msg2.content == '6':
                    await message.edit(content='You selected option 6.', delete_after=10)


async def setup(bot):
    await bot.add_cog(TemplateCommand(bot))
