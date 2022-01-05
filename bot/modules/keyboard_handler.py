from telegram import InlineKeyboardButton
from typing import List
import datetime

from . import chat_settings, formatting
from ..utils import (
    PROPERTY_TRANSLATION,
    BOOL_EMOJI_CONVERTER,
    MAIN_MENU_KEYBOARD,
    NUMBER_PAST_STATS_BUTTONS,
    TIMEZONE,
    DATE_FORMAT,
    PREV_NEXT_BUTTONS,
    BACK_STATISTIC_BUTTON,
)


def edit_keyboard_properties(
    property_value: bool, data_button: str, inline_keyboard: List[List[InlineKeyboardButton]]
) -> List[List[InlineKeyboardButton]]:
    """When a property button is pressed, that value is
    changed for the user who made the request
    A button is in the form of '[propertyName] [emoji]'"""
    for row_buttons in inline_keyboard:
        for button in row_buttons:
            description, _ = button.text.split(" ")
            if description.lower() == PROPERTY_TRANSLATION[data_button]:
                button.text = f"{description} {BOOL_EMOJI_CONVERTER[property_value]}"
                return inline_keyboard
    raise RuntimeError("The property isn't found")


def handle_change_keyboard(
    data_button: str, current_chat: int, inline_keyboard: List[List[InlineKeyboardButton]]
) -> List[List[InlineKeyboardButton]]:
    chat_config = chat_settings.get_chat_properties(current_chat)

    # Keyboard to show the properties of the messages
    if data_button in ["messages_management"]:
        return formatting.format_messages_button(chat_config)
    # Keyboard to show the properties of the notification
    elif data_button in ["notification_management", "notification"]:
        return formatting.format_notification_button(chat_config)
    # Keyboard to show the menu for the statistics (current day or calendar of past days)
    elif data_button in ["statistics"]:
        return formatting.format_statistics_button(chat_config)
    elif data_button in ["past_statistics", "next_statistics", "prev_statistics"]:
        current_day = datetime.datetime.now(tz=TIMEZONE)
        if data_button == "next_statistics":
            date_value = inline_keyboard[0][0].text
            date_keyboard = datetime.datetime.strptime(date_value, DATE_FORMAT)
            date_start = date_keyboard + datetime.timedelta(days=NUMBER_PAST_STATS_BUTTONS)
        elif data_button == "prev_statistics":
            date_value = inline_keyboard[int(NUMBER_PAST_STATS_BUTTONS / 2) - 1][1].text
            date_keyboard = datetime.datetime.strptime(date_value, DATE_FORMAT)
            date_start = date_keyboard + datetime.timedelta(days=-1)
        else:
            date_start = current_day
        if current_day >= date_start.astimezone(tz=TIMEZONE):
            dates_range = generate_dates(date_start)
            return generate_dates_buttons(dates_range)
        else:
            return inline_keyboard

    else:
        return MAIN_MENU_KEYBOARD


def generate_dates(date_start: datetime.datetime) -> List[str]:
    dates_ranges = []
    for i in range(NUMBER_PAST_STATS_BUTTONS):
        date_past = date_start - datetime.timedelta(days=i)
        dates_ranges.append(date_past.strftime(DATE_FORMAT))
    return dates_ranges


def generate_dates_buttons(dates_range: List[str]) -> List[List[InlineKeyboardButton]]:
    statistic_buttons = list()
    tmp_list = list()

    buttons_row = 2
    for i in range(len(dates_range)):
        if i % buttons_row == 0 and i > 0:
            statistic_buttons.append(tmp_list.copy())
            tmp_list.clear()
        tmp_list.append(InlineKeyboardButton(dates_range[i], callback_data=f"{dates_range[i]}-statistics"))
    statistic_buttons.append(tmp_list.copy())
    statistic_buttons.append(PREV_NEXT_BUTTONS)
    statistic_buttons.append([BACK_STATISTIC_BUTTON])

    return statistic_buttons
