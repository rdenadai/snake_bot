from typing import Optional

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic: str
    person: str
    person_message: str
    ai_response: str
