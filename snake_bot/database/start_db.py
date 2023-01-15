import asyncio

from sqlmodel import SQLModel

from snake_bot.database.db import engine
from snake_bot.database.models import Conversation


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
