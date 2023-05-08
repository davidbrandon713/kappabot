import os
import json
import requests
import traceback
import discord
from discord.ext import commands
import random
import numpy as np
from dotenv import load_dotenv
load_dotenv()


# Initializing bot and intents
description = 'A bot used for practicing Python'
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


# Prefix '!' in servers, no prefix in DMs
def command_prefix(bot, message):
    if message.guild is None:
        return ''
    else:
        return '!'


# Assigning intents *REQUIRED TO ACCESS MESSAGE CONTENTS*
bot = commands.Bot(command_prefix=command_prefix, description=description, intents=intents)


# =================== Triggers one time upon startup =======================
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('--------------------------------------------------------')


# ============= Triggers every time a message is sent ==================
@bot.event
async def on_message(message):
    # if the bot wrote the message, ignore
    if message.author == bot.user:
        return
    try:
        # determine if message is command or not
        ctx = await bot.get_context(message)
        if not ctx.command or not ctx.valid:
            return
        # message is command, process the command and log to console
        await bot.process_commands(message)
        print(f"{message.author} said '{message.content}' in {message.channel} ({message.guild})")
    except Exception:
        pass


# ============ Triggers any time an error occurs ==============
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


# ============================== COMMANDS ===================================
@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def roll(ctx, dice: str = commands.parameter(default="1d6", description=": must be NdN format")):
    """rolls dice in NdN format"""
    try:
        if ctx.message.guild:
            await ctx.message.delete()
        rolls, limit = map(int, dice.split('d'))
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

    except Exception:
        await ctx.send("Format has to be in NdN!", delete_after=2)
        return


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def flip(ctx):
    """flip a coin"""
    number = random.randint(1, 2)
    try:
        if ctx.message.guild:
            await ctx.message.delete()
        coin = 'Heads' if number == 1 else 'Tails'
        await ctx.send(coin, delete_after=10)

    except Exception:
        await ctx.send(f"Something went wrong", delete_after=2)
        return


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def teams(ctx, *args):
    """team randomizer"""
    if len(args) < 2:
        if ctx.message.guild:
            await ctx.message.delete()
        await ctx.send(f"requires at least 2 players", delete_after=2)
        return

    try:
        if ctx.message.guild:
            await ctx.message.delete()
        players = list(args)
        random.shuffle(players)
        team_a = ', '.join(players[:len(players)//2]).title()
        team_b = ', '.join(players[len(players)//2:]).title()

        embed = discord.Embed(
            colour=discord.Color.dark_teal(),
        )
        embed.add_field(name="Team 1", inline=True, value='\n'.join(team_a.split(', ')))
        embed.add_field(name="Team 2", inline=True, value='\n'.join(team_b.split(', ')))
        await ctx.send(embed=embed)

    except Exception:
        await ctx.send(f"Something went wrong", delete_after=2)
        return


@bot.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def gabe(ctx):
    """Gabe gambler"""
    try:
        rand_array = np.random.normal(int(5), int(10), int(100))
        rand_num = int(abs(rand_array[0]))
        if ctx.message.guild:
            await ctx.message.delete()
            await ctx.send(f"<@{ctx.author.id}> Ga{'a'*rand_num}be ({rand_num + 1})")
        else:
            await ctx.send(f"Ga{'a'*rand_num}be ({rand_num + 1})")

        # open json file
        with open("gabe_dict.json", "r") as f:
            gabe_dict = json.load(f)

        # if the ctx.author.id (refer now as author_id) is inside dictionary
        if (author_id := str(ctx.author.id)) in gabe_dict:
            if gabe_dict[author_id] < rand_num + 1:
                await ctx.send(f"**New high score!**\nPrevious was {gabe_dict[author_id]}")
                gabe_dict[author_id] = rand_num + 1
                with open("gabe_dict.json", "w") as f:
                    sorted_list = sorted(gabe_dict.items(), key=lambda x: x[1], reverse=True)
                    sorted_dict = dict(sorted_list)
                    json.dump(sorted_dict, f)
        else:
            gabe_dict[author_id] = rand_num + 1
            with open("gabe_dict.json", "w") as f:
                sorted_list = sorted(gabe_dict.items(), key=lambda x: x[1], reverse=True)
                sorted_dict = dict(sorted_list)
                json.dump(sorted_dict, f)
    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        return


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def glb(ctx):
    """Gabe leaderboard"""
    try:
        if ctx.message.guild:
            await ctx.message.delete()

        # open json file
        with open("gabe_dict.json", "r") as f:
            gabe_dict = json.load(f)

        gabe_keys = list(gabe_dict.keys())[0: 5]
        gabe_keys = '\n'.join(["<@" + e + ">" for e in gabe_keys])

        gabe_vals = list(gabe_dict.values())[0: 5]
        gabe_vals = '\n'.join(str(e) for e in gabe_vals)

        # create discord embed message
        embed = discord.Embed(
            colour=discord.Color.dark_teal(),
            title="Gaaaaabe Leaderboard",
        )
        embed.set_thumbnail(url="https://cdn.frankerfacez.com/emoticon/588022/2")
        embed.add_field(name="Rank", inline=True, value="1\n2\n3\n4\n5")
        embed.add_field(name="User", inline=True, value=gabe_keys)
        embed.add_field(name="Score", inline=True, value=gabe_vals)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        return


@bot.command()
@commands.cooldown(1, 1, commands.BucketType.user)
async def orders(ctx, *, arg):
    """Get orders"""
    try:
        if ctx.message.guild:
            await ctx.message.delete()
        converted_str = '_'.join(arg.split(' '))

        res = requests.get(f"https://api.warframe.market/v1/items/{converted_str}/orders")
        data = res.json()
        order_data = data['payload']['orders']

        # create discord embed message
        embed = discord.Embed(
            colour=discord.Color.dark_teal(),
            title=arg + " orders",
        )
        # embed.set_thumbnail(url=f"https://warframe.market/static/assets/{item['icon']}")
        embed.add_field(name="User", inline=True, value=order_data['user']['ingame_name'])
        embed.add_field(name="Price", inline=True, value=order_data['platinum'])
        embed.add_field(name="Quantity", inline=True, value=order_data['quantity'])
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        return


@bot.command()
async def test(ctx):
    if ctx.message.guild:
        await ctx.message.delete()
    await ctx.send(ctx.message.content, delete_after=2)


# Run bot
bot.run(os.getenv("token"))
