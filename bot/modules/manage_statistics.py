import datetime as dt
from pydantic import ValidationError
from pymongo.errors import OperationFailure

from ..utils import User, Statistic, TIME_FORMAT, PROPERTY_TRANSLATION
from ..mongodb import MongoDB


def get_statistics(chat_id: int, date: str) -> str:
    message = ""
    message += get_category_statistics("Messages", chat_id, date)
    message += get_category_statistics("Voices", chat_id, date)
    message += get_category_statistics("Videonotes", chat_id, date)
    return message


def get_category_statistics(category: str, chat_id: int, date: str) -> str:
    results = MongoDB.find_date_statistic(category, chat_id, date)

    initial_message = f"\n\n*Gli utenti con più {PROPERTY_TRANSLATION[category.lower()]} sono stati:*"
    message = ""
    for raw_res in results:
        try:
            stat = Statistic(chat_id=raw_res["chat_id"], user_id=raw_res["user_id"], date=raw_res["date"], count=raw_res["count"])
            if category in ["Videonotes", "Voices"]:
                count_format = format_seconds_count(stat.count)
                unit_count = "minuti"
            else:
                count_format = stat.count
                unit_count = "messaggi"
            user = MongoDB.find_user(stat.user_id)
            message += f"\n{user.full_name} con {count_format} {unit_count}"
        except ValidationError as exc:
            raise RuntimeError from exc

    if message == "":
        return message
    else:
        return initial_message + message


def format_seconds_count(count: int) -> str:
    hours = int(count / 3600)
    minutes = int(count / 60)
    seconds = count - (minutes * 60) - (hours * 3600)

    time_val = dt.time(hour=hours, minute=minutes, second=seconds)
    return time_val.strftime(TIME_FORMAT)


def set_statistic_counter(count: int, category: str, chat_id: int, user_id: int, user_full_name: str, date: str):
    try:
        user = User(_id=user_id, full_name=user_full_name)
        statistic = Statistic(chat_id=chat_id, user_id=user.id, date=date, count=count)

        MongoDB.update_date_statistic(category, user, statistic)
    except (ValidationError, OperationFailure) as exc:
        raise RuntimeError from exc
