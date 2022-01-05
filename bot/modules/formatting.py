from telegram import InlineKeyboardButton
from typing import List

from ..utils import BOOL_EMOJI_CONVERTER, BACK_MENU_BUTTON, Chat


def format_info_log(text: str, chat_id: int, full_name: str) -> str:
    return f"{text} from {chat_id} | {full_name}"


def format_messages_button(chat_config: Chat) -> List[List[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton(f"Videomessaggi {BOOL_EMOJI_CONVERTER[chat_config.videonotes]}", callback_data="videonotes"),
            InlineKeyboardButton(f"Audiomessaggi {BOOL_EMOJI_CONVERTER[chat_config.voices]}", callback_data="voices"),
        ],
        [
            InlineKeyboardButton(f"Messaggi {BOOL_EMOJI_CONVERTER[chat_config.messages]}", callback_data="messages"),
            BACK_MENU_BUTTON,
        ],
    ]


def format_notification_button(chat_config: Chat) -> List[List[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton(f"Notifiche {BOOL_EMOJI_CONVERTER[chat_config.notification]}", callback_data="notification"),
            BACK_MENU_BUTTON,
        ]
    ]


def format_statistics_button(chat_config: Chat) -> List[List[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton("Statistiche di oggi", callback_data="today_statistics"),
            InlineKeyboardButton("Statistiche passate", callback_data="past_statistics"),
        ],
        [BACK_MENU_BUTTON],
    ]
