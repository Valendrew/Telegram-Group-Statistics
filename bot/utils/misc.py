from telegram import InlineKeyboardButton
import pytz

# All type of inline keyboard
MAIN_MENU_KEYBOARD = [
    [
        InlineKeyboardButton("Conteggio messaggi", callback_data="messages_management"),
        InlineKeyboardButton("Gestione notifiche", callback_data="notification_management"),
    ],
    [InlineKeyboardButton("Statistiche", callback_data="statistics")],
]
BACK_MENU_BUTTON = InlineKeyboardButton("Torna indietro", callback_data="back_menu")
BACK_STATISTIC_BUTTON = InlineKeyboardButton("Torna indietro", callback_data="statistics")
PREV_NEXT_BUTTONS = [
    InlineKeyboardButton("Date precedenti", callback_data="prev_statistics"),
    InlineKeyboardButton("Date successive", callback_data="next_statistics"),
]

# Translation between properties name and string in the button
PROPERTY_TRANSLATION = {"videonotes": "videomessaggi", "voices": "audiomessaggi", "messages": "messaggi", "notification": "notifiche"}

# Convert boolean into emoji, for inline button
BOOL_EMOJI_CONVERTER = {True: "✅", False: "❌"}

# Must be even and greater than 1
NUMBER_PAST_STATS_BUTTONS = 6

# Date settings
# Timezone
TIMEZONE = pytz.timezone("Europe/Rome")
DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%M:%S"

LIMIT_USER_STAT = 6
