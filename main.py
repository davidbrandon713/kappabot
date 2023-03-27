import os

from dotenv import load_dotenv
import traceback
import discord
from discord.ext import commands
import numpy as np
import random

load_dotenv()
description = 'A bot used for practicing Python'
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


def command_prefix(bot, message):
    """Command prefix"""
    if message.guild is None:
        return ''
    else:
        return '!'


bot = commands.Bot(command_prefix=command_prefix, description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    try:
        ctx = await bot.get_context(message)
        if not ctx.command or not ctx.valid:
            return
        await bot.process_commands(message)
        print(f"{message.author} said '{message.content}' in {message.channel} ({message.guild})")
    except Exception as e:
        print(e)


@bot.event
async def on_command_error(ctx, error):
    """Command error handler"""

    if isinstance(error, commands.CommandOnCooldown):
        if ctx.message.guild:
            await ctx.message.delete()
        await ctx.send(f"Command on cooldown. Try again after {error.retry_after:.0f}s.", delete_after=2)

    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.message.guild:
            await ctx.message.delete()
        await ctx.send(f"Missing required argument", delete_after=2)

    else:
        print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
        return


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def roll(ctx, dice: str = commands.parameter(default="1d6", description=": must be NdN format")):
    """rolls dice in NdN format"""
    try:
        rolls, limit = map(int, dice.split('d'))
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        if ctx.message.guild:
            await ctx.message.delete()
        await ctx.send(result)
    except Exception as e:
        print(e)
        await ctx.send("Format has to be in NdN!", delete_after=2)
        return


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def flip(ctx):
    """flip a coin"""
    number = random.randint(1, 2)
    try:
        coin = 'Heads' if number == 1 else 'Tails'
        if ctx.message.guild:
            await ctx.message.delete()
        await ctx.send(coin, delete_after=10)
    except Exception as e:
        print(e)
        await ctx.send(f"Something went wrong", delete_after=2)
        return


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def teams(ctx, *args):
    """team randomizer"""
    try:
        players = list(args)
        random.shuffle(players)
        team_a = ', '.join(players[:len(players)//2]).title()
        team_b = ', '.join(players[len(players)//2:]).title()
        if ctx.message.guild:
            await ctx.message.delete()
        await ctx.send(f"```Team 1: {team_a}\nTeam 2: {team_b}```")
    except Exception as e:
        print(e)
        await ctx.send(f"Something went wrong", delete_after=2)
        return


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def schmee(ctx):
    """Schmeeee gambler"""
    try:
        rand_array = np.random.normal(int(5), int(10), int(100))
        rand_num = abs(int(rand_array[0]))
        if ctx.message.guild:
            await ctx.message.delete()
            await ctx.send(f"<@{ctx.message.author.id}> Schm{'e'*rand_num} ({rand_num})")
        else:
            await ctx.send(f"Schm{'e'*rand_num} ({rand_num})")
    except Exception as e:
        print(e)
        await ctx.send(f"Something went wrong", delete_after=2)
        return


bot.run(os.environ.get("token"))
