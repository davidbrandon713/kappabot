import os
import json
import requests
import traceback
import discord
from discord.ext import commands
import random
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()


# Initializing bot and intents
description = 'A bot used for practicing Python'
allowed_channels = os.getenv("ALLOWED_CHANNELS").split(', ')
allowed_guilds = os.getenv("ALLOWED_GUILDS").split(', ')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT_ID"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID"),
)
gabe_file = "gabe_dict.json"


# Prefix '-' in servers, no prefix in DMs
def command_prefix(bot, message):
    if message.guild is None:
        return ''
    else:
        return '-'


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
    # if a bot wrote the message, ignore
    if message.author == bot.user:
        return
    if str(message.channel.id) in allowed_channels or str(message.guild.id) in allowed_guilds:
        try:
            # determine if message is command or not
            ctx = await bot.get_context(message)
            if not ctx.command or not ctx.valid:
                return
            # message is command, process the command and log to console
            await bot.process_commands(message)
            print(f"{message.author} said '{message.content}' in #{message.channel} ({message.guild})")
        except Exception:
            pass


# ============ Error handler ==============
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
        await ctx.send(coin)

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

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        await on_command_error(ctx, e)
        return


@bot.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def gabe(ctx):
    """Gabe gambler"""

    def sort_and_save():
        with open(gabe_file, "w") as w:
            sorted_list = sorted(gabe_dict.items(), key=lambda x: x[1], reverse=True)
            sorted_dict = dict(sorted_list)
            json.dump(sorted_dict, w)

    try:
        author_id = str(ctx.author.id)
        rand_array = np.random.normal(int(5), int(10), int(100))
        rand_num = int(abs(rand_array[0]))
        displayed_num = rand_num + 1
        record = 0

        if ctx.message.guild:
            await ctx.message.delete()
            await ctx.send(f"<@{ctx.author.id}> Ga{'a'*rand_num}be ({displayed_num})")
        else:
            await ctx.send(f"Ga{'a'*rand_num}be ({displayed_num})")

        # open json file
        with open(gabe_file, "r") as r:
            gabe_dict = json.load(r)

        # check all values in case of sorting issue
        for value in gabe_dict.values():
            if value > record:
                record = value

        # if you got a new world record
        if displayed_num > record:
            await ctx.send(f"<:WTFFFFF:1284584326654066791>")
            await ctx.send(f"**New world record! ({displayed_num})**\nPrevious was {record}")
            gabe_dict[author_id] = displayed_num
            sort_and_save()
            return

        # if you got a new high score
        if author_id in gabe_dict and displayed_num > gabe_dict[author_id]:
            await ctx.send(f"**New high score! ({displayed_num})**\nPrevious was {gabe_dict[author_id]}")
            gabe_dict[author_id] = displayed_num
            sort_and_save()
            return

        # if it's your first score
        if author_id not in gabe_dict:
            gabe_dict[author_id] = displayed_num
            sort_and_save()
            return

        # 2024-09-14
        # {"176502309965135874": 21, "417463311961948162": 19, "107317852612075520": 11, "228919057368350721": 10, "302681717225947139": 8}

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        await on_command_error(ctx, e)
        return


@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def glb(ctx, count: str = commands.parameter(default=5, description=": 'all' for all scores")):
    """Gabe leaderboard"""
    if count == "all":
        count = 50

    try:
        author_id = str(ctx.author.id)
        ranks_list = list(str(i) for i in range(1, count))

        # open json file
        with open(gabe_file, "r") as r:
            gabe_dict_unsorted = json.load(r)
            # sort for good measure
            sorted_list = sorted(gabe_dict_unsorted.items(), key=lambda x: x[1], reverse=True)
            gabe_dict = dict(sorted_list)

        gabe_keys_list = list(gabe_dict.keys())[0: int(count)]
        gabe_keys = '\n'.join(["<@" + e + ">" for e in gabe_keys_list])

        gabe_vals_list = list(gabe_dict.values())[0: int(count)]
        gabe_vals = '\n'.join(str(v) for v in gabe_vals_list)

        ranks = '\n'.join(ranks_list[0:len(gabe_keys_list)])

        # if you're not in the top 5
        if author_id not in gabe_keys and author_id in gabe_dict:
            # find your position in leaderboard and display below top 5
            temp = list(gabe_dict.items())
            rank = [idx for idx, key in enumerate(temp) if key[0] == author_id][0]
            ranks += f"\n...\n{str(rank + 1)}"
            gabe_keys += f"\n...\n<@{author_id}>"
            gabe_vals += f"\n...\n{gabe_dict[author_id]}"

        # create discord embed message
        embed = discord.Embed(
            colour=discord.Color.dark_teal(),
            title="Gaaaaabe Leaderboard",
        )
        embed.set_thumbnail(url="https://cdn.frankerfacez.com/emoticon/588022/2")
        embed.add_field(name="Rank", inline=True, value=ranks)
        embed.add_field(name="User", inline=True, value=gabe_keys)
        embed.add_field(name="Score", inline=True, value=gabe_vals)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        await on_command_error(ctx, e)
        return


# Random cat image

@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def cat(ctx, d: str = commands.parameter(default=0, description=": for a description")):
    """Get a random image of a cat, `-cat d` for an image with a description."""
    image_desc = 0
    if d == "d":
        image_desc = 1
    try:
        api_key = os.getenv("CAT_API_KEY")
        res = requests.get(f"https://api.thecatapi.com/v1/images/search?api_key={api_key}&has_breeds={image_desc}")
        data = res.json()
        breeds = data[0]['breeds']

        await ctx.send(data[0]['url'])
        if image_desc:
            await ctx.send(f"**{breeds[0]['name']}**: {breeds[0]['description']}")

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        await on_command_error(ctx, e)
        return


# WFM
@bot.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def orders(ctx, *, arg):
    """Get orders"""
    try:
        if ctx.message.guild:
            await ctx.message.delete()
        converted_str = '_'.join(arg.split(' '))

        res = requests.get(f"https://api.warframe.market/v1/items/{converted_str}/orders?include=item")
        data = res.json()
        order_data = data['payload']['orders']
        sorted_data = list(sorted(order_data, key=lambda x: x['platinum']))
        filtered_data = list(
            filter(lambda x: x['order_type'] == 'sell' and x['user']['status'] == 'ingame', sorted_data)
        )

        displayed_users = '\n'.join(order['user']['ingame_name'] for order in filtered_data[0:8])
        displayed_prices = '\n'.join(str(order['platinum']) for order in filtered_data[0:8])
        displayed_quantity = '\n'.join(str(order['quantity']) for order in filtered_data[0:8])

        print(displayed_users)

        # create discord embed message
        embed = discord.Embed(
            colour=discord.Color.dark_teal(),
            title=arg.title() + " Orders",
        )
        embed.set_thumbnail(
            url=f"https://warframe.market/static/assets/{data['include']['item']['items_in_set'][0]['thumb']}"
        )
        embed.add_field(name="User", inline=True, value=displayed_users)
        embed.add_field(name="Price", inline=True, value=displayed_prices)
        embed.add_field(name="Quantity", inline=True, value=displayed_quantity)
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Something went wrong", delete_after=2)
        print(e)
        await on_command_error(ctx, e)
        return


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def c(ctx, *args):
    """ChatGPT response"""
    prompt = ' '.join(args)
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.7,
    )
    try:
        response = completion.choices[0].message.content
        await ctx.send(response)

    except Exception as e:
        finish_reason = completion.choices[0].finish_reason
        await ctx.send(f"Something went wrong", delete_after=2)
        print(finish_reason)
        print(e)
        await on_command_error(ctx, e)
        return


@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def shaun(ctx):
    await ctx.send(f"https://media.discordapp.net/attachments/1257847889489825814/1286775167799918655/8xn0pq.gif?ex=66"
                   f"f316c3&is=66f1c543&hm=b43127a065c6e80892b833520b8296b8699f655d72e862a326e5abdc4b9f910d&")


@bot.command()
async def test(ctx):
    if ctx.message.guild:
        await ctx.message.delete()
    await ctx.send("Test", delete_after=2)


@bot.command()
async def say(ctx, *args):
    message = " ".join(args)
    admin_ids = os.getenv("ADMIN_IDS").split(', ')
    if ctx.message.guild:
        await ctx.message.delete()
    if str(ctx.author.id) not in admin_ids:
        return
    await ctx.send(message)


@bot.command()
async def shutdown(ctx):
    await ctx.send("gg")
    exit()

# Run bot
bot.run(os.getenv("token"))
