from pydantic import parse_obj_as, ValidationError
from pymongo.errors import DuplicateKeyError, OperationFailure

from ..mongodb import MongoDB
from ..utils import Chat


def create_new_chat(chat_id: int) -> Chat:
    """A new chat entry in the database is created
    from the given id. All the properties all enabled by default"""
    chat = Chat(_id=chat_id, notification=True, messages=True, videonotes=True, voices=True)
    try:
        MongoDB.add_chat(chat)
        return chat.dict(exclude={"id"})
    except DuplicateKeyError as exc:
        raise RuntimeError from exc


def get_chat_properties(chat_id: int) -> Chat:
    """A chat is searched in the database and then returned"""
    try:
        chat = MongoDB.find_chat(chat_id)
        return chat
    except ValidationError as exc:
        raise RuntimeError from exc


def change_chat_properties(chat_id: int, property: str) -> bool:
    """The chat is returned from the database,
    then the value of the property requested for the change
    (a simple not operation is performed) is set into the database"""
    try:
        chat = MongoDB.find_chat(chat_id)
        value = not getattr(chat, property)
        MongoDB.update_chat_property(chat.id, property, value)
        return value
    except (ValidationError, AttributeError, DuplicateKeyError) as exc:
        raise RuntimeError from exc


def get_all_chats_enabled_properties() -> dict:
    """Find users where at least one property is enabled.
    An iteration through all users is performed to filter
    only the properties enabled for each user"""
    try:
        results = MongoDB.find_chats_properties_enabled()
    except (TypeError, OperationFailure) as exc:
        raise RuntimeError from exc

    enabled_properties = dict()
    for raw_chat in results:
        try:
            chat = parse_obj_as(Chat, raw_chat)
            chat_dict = chat.dict(exclude={"_id"})
            enabled_properties[chat.id] = {p: v for p, v in chat_dict.items() if v == True}
        except ValidationError as exc:
            raise RuntimeError from exc

    return enabled_properties
