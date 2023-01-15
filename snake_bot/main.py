# This example requires the 'members' and 'message_content' privileged intents to function.

import random
from textwrap import dedent
from typing import List
from uuid import uuid4

import discord
import openai
from decouple import config
from discord.ext import commands
from openai.openai_object import OpenAIObject
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from snake_bot.database.db import engine
from snake_bot.database.models import Conversation
from snake_bot.utils import MockOpenAIResponse

GUILD_ID = config("GUILD_ID")
DISCORD_TOKEN = config("DISCORD_TOKEN")
openai.organization = config("OPENAI_ORGANIZATION")
openai.api_key = config("OPENAPI_TOKEN")

DEFAULT_CONVERSATION = """
    User: Hi HAL (that's your name from now on)\n
    AI: Hello %s\n
    User: We're going to talk about %s (for code examples add markdown code blocks with language support)\n
    AI: Ok
"""

OPENAI_RESPONSE_ERROR = [MockOpenAIResponse("Some kind of error happen when trying to get your answer!")]

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


@bot.hybrid_command(description="Talk with HAL-9000 bot")
async def hal(ctx, question: str):
    original_question = question
    person_name = ctx.message.author.name
    person_id: str = str(ctx.message.author.id)
    topic: str = ctx.message.channel.name

    async with AsyncSession(engine) as session:
        conversations = await session.execute(
            select(Conversation).where(Conversation.topic == topic, Conversation.person == person_id)
        )

        context: List[str] = [
            f"User:{conversation.person_message}\nAI:{conversation.ai_response}"
            for conversation in conversations.scalars().all()
        ]
        if not context:
            context.append(dedent(DEFAULT_CONVERSATION % (person_name, " ".join(topic.split("_")))))
        context.append(f"User: {question}")
        question = "\n".join(context)

        # Make a call to OpenAI language model
        response: OpenAIObject = await openai.Completion.acreate(
            model="text-davinci-003",
            prompt=f"{question}\n$--$",
            max_tokens=256,
            temperature=0,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n$--$"],
        )
        ai_response: str = response.get("choices", OPENAI_RESPONSE_ERROR)[0].text

        # # Save conversation on database
        session.add(
            Conversation(
                topic=topic,
                person=person_id,
                person_message=question,
                ai_response=ai_response,
            )
        )
        await session.commit()

        # Response to discord
        await ctx.reply(original_question)
        await ctx.send(ai_response)


bot.run(DISCORD_TOKEN)
