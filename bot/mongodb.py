import pymongo
from pymongo.database import Database
from pymongo.cursor import Cursor
import os
from pydantic import parse_obj_as

from utils import Chat, User, Statistic, LIMIT_USER_STAT

class MongoDB:
    DATABASE: Database = None
    CHATS = "Chats"
    USERS = "Users"

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(os.environ.get("MONGO_URI"))
        MongoDB.DATABASE = client[os.environ.get("MONGO_DB", "BotGroupStats")]

    @staticmethod
    def add_user(user: User):
        result = MongoDB.DATABASE[MongoDB.USERS].update_one({"_id": user.id}, update={"$set": user.dict(by_alias=True)}, upsert=True)

    @staticmethod
    def add_chat(chat: Chat):
        result = MongoDB.DATABASE[MongoDB.CHATS].update_one({"_id": chat.id}, update={"$set": chat.dict(by_alias=True)}, upsert=True)

    @staticmethod
    def find_chat(chat_id: int) -> Chat:
        chat = parse_obj_as(Chat, MongoDB.DATABASE[MongoDB.CHATS].find_one({"_id": chat_id}))
        return chat

    @staticmethod
    def update_chat_property(chat_id: int, property: str, value: bool):
        MongoDB.DATABASE[MongoDB.CHATS].update_one({"_id": chat_id}, update={"$set": {property: value}})

    @staticmethod
    def find_chats_properties_enabled() -> Cursor:
        results = MongoDB.DATABASE[MongoDB.CHATS].find(
            {"$or": [{"notification": True}, {"messages": True}, {"videonotes": True}, {"voices": True}]}
        )
        return results

    @staticmethod
    def update_date_statistic(collection: str, user: User, stat: Statistic):
        # result = MongoDB.DATABASE[collection].find_one({"$and": [{"chat_id": chat_id}, {"date": date}]})
        result = MongoDB.DATABASE[collection].update_one(
            {"$and": [{"chat_id": stat.chat_id}, {"user_id": stat.user_id}, {"date": stat.date}]},
            update={"$inc": {"count": stat.count}},
            upsert=True,
        )
        if result.upserted_id is not None:
            MongoDB.add_user(user)

    @staticmethod
    def find_date_statistic(collection: str, chat_id: int, date: str) -> Cursor:
        results = MongoDB.DATABASE[collection].find(
            {"$and": [{"chat_id": chat_id}, {"date": date}]}, sort=[("count", pymongo.DESCENDING)], limit=LIMIT_USER_STAT
        )
        return results
