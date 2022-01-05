from pydantic import BaseModel, Field


class Chat(BaseModel):
    id: int = Field(..., alias="_id")
    notification: bool
    messages: bool
    videonotes: bool
    voices: bool


class User(BaseModel):
    id: int = Field(..., alias="_id")
    full_name: str


class Statistic(BaseModel):
    chat_id: int
    user_id: int
    date: str
    count: int
