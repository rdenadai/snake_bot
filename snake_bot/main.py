# This example requires the 'members' and 'message_content' privileged intents to function.

import random
from textwrap import dedent
from uuid import uuid4

import discord
from decouple import config
from discord.ext import commands

GUILD_ID = config("GUILD_ID")
DISCORD_TOKEN = config("DISCORD_TOKEN")

description = """SnakeBot built by rdenadai."""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="?", description=description, intents=intents)


@bot.event
async def on_ready():
    print("-" * 30)
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("-" * 30)


@bot.event
async def setup_hook():
    # This copies the global commands over to your guild.
    bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))


@bot.hybrid_command(description="Roll N number of dices of N number of faces")
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split("d"))
    except Exception:
        await ctx.send("Format has to be in NdN!")
        return

    result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.hybrid_command(description="Random choose one of any number of items (separated by commas)")
async def choose(ctx, choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices.split(",")))


@bot.hybrid_command(description="Check when user joined the server")
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f"{member.name} joined {discord.utils.format_dt(member.joined_at)}")


@bot.hybrid_command(description="Generate random UUID4")
async def uuid(ctx, number: int = 1):
    await ctx.send("\n".join(str(uuid4()) for _ in range(number)))


@bot.hybrid_command(description="Print the Zen of Python")
async def this(ctx):
    await ctx.send(
        dedent(
            """
            Command:
            ```python
            import this
            ```
            Output:
            ```markdown
            Beautiful is better than ugly.
            Explicit is better than implicit.
            Simple is better than complex.
            Complex is better than complicated.
            Flat is better than nested.
            Sparse is better than dense.
            Readability counts.
            Special cases aren't special enough to break the rules.
            Although practicality beats purity.
            Errors should never pass silently.
            Unless explicitly silenced.
            In the face of ambiguity, refuse the temptation to guess.
            There should be one-- and preferably only one --obvious way to do it.
            Although that way may not be obvious at first unless you're Dutch.
            Now is better than never.
            Although never is often better than *right* now.
            If the implementation is hard to explain, it's a bad idea.
            If the implementation is easy to explain, it may be a good idea.
            Namespaces are one honking great idea -- let's do more of those!
            ```
            """
        )
    )


bot.run(DISCORD_TOKEN)
