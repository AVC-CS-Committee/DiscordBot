from dotenv import load_dotenv
import os
import discord
#import discord.ext
from discord.ext import commands
from discord import app_commands

from gambling import blackjack, coinflip, roulette


# this loads the env file with the API key to be stored
# locally make sure you have your .env file set

load_dotenv('.env')
disc_token: str = os.getenv('DISC_TOKEN')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print("bot is online")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Commands")
    except Exception as e:
        print(e)

@bot.tree.command(name='hello')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello !", ephemeral=False)

@bot.command()
async def games(ctx, option: int):
    if option == 1:
        await ctx.send("You selected game 1.")
    elif option == 2:
        await ctx.send("You selected game 2.")
    elif option == 3:
        await ctx.send("You selected game 3.")
    elif option == 4:
        await ctx.send("You selected game 4.")
    elif option == 5:
        await ctx.send("You selected game 5.")
    else:
        await ctx.send("Invalid option. Please select a number between 1 and 5.")


@bot.command()
async def gamble(ctx):
    await ctx.send("Please select a game: blackjack, coinflip, or roulette.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and \
            m.content.lower() in ['blackjack', 'coinflip', 'roulette']

    msg = await bot.wait_for('message', check=check)

    if msg.content.lower() == 'blackjack':
        game_state = blackjack()
        await ctx.send(f"Your cards: {game_state['player_hand']}, current score: {game_state['player_score']}")
        await ctx.send(f"Computer's first card: {game_state['computer_hand'][0]}")

        game_over = False
        while not game_over:
            await ctx.send("Type 'y' to get another card, 'n' to pass: ")
            msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['y', 'n'])
            if msg.content.lower() == 'y':
                game_state = blackjack()
                await ctx.send(f"Your cards: {game_state['player_hand']}, current score: {game_state['player_score']}")
            else:
                game_over = True

        await ctx.send(f"Your final hand: {game_state['player_hand']}, final score: {game_state['player_score']}")
        await ctx.send(f"Computer's final hand: {game_state['computer_hand']}, final score: {game_state['computer_score']}")
    elif msg.content.lower() == 'coinflip':
        result = coinflip()
        await ctx.send(result)
    elif msg.content.lower() == 'roulette':
        result = roulette()
        await ctx.send(result)

@bot.command()
async def add(ctx, arg, arg2):
    arg3 = int(arg) + int(arg2)
    await ctx.send(arg3)


@bot.hybrid_command()
async def test(ctx, arg):
    await ctx.send(arg)


bot.run(disc_token)  # runs the bot with the given api key
