import datetime as dt
from telegram.ext import CommandHandler, Filters, CallbackQueryHandler, CallbackContext, JobQueue, MessageHandler
from telegram import ParseMode, InlineKeyboardMarkup, Update, TelegramError

from . import updater, dispatcher, LOGGER
from .modules import chat_settings, formatting, manage_stats, keyboard_handler
from .utils import MAIN_MENU_KEYBOARD, TIMEZONE, DATE_FORMAT


# Filtri per Handler
filters_callback = {"messages": Filters.chat(), "videonotes": Filters.chat(), "voices": Filters.chat()}


def statistic_message(chat_id: int, date: str):
    message = manage_stats.get_statistics(chat_id, date)
    if message == "":
        return f"Nessuna statistica disponibile il *{date}*"
    else:
        return f"Ecco le statistiche del *{date}*" + message


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    chat_id = update.message.chat_id
    chat = chat_settings.create_new_chat(chat_id)
    for property, value in chat.items():
        change_single_property(chat_id, property, value, context.job_queue)


def settings(update: Update, context: CallbackContext):
    update.message.reply_text("Impostazioni per le statistiche del gruppo", reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))
    LOGGER.info(formatting.format_info_log(update.message.text, update.message.chat_id, update.effective_chat.full_name))


def help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Ottieni statistiche riguardo al tuo gruppo")
    LOGGER.info(formatting.format_info_log(update.message.text, update.message.chat_id, update.effective_chat.full_name))


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    # LOGGER.warning('Update "%s" caused error "%s"', update, context.error)
    raise RuntimeError from context.error


def callback_inline_keyboard(update: Update, context: CallbackContext):
    chat_id = update.callback_query.message.chat_id
    button_pressed = update.callback_query
    button_data = button_pressed.data
    inline_keyboard = button_pressed.message.reply_markup.inline_keyboard

    # Button for property changes
    if button_data in ["videonotes", "voices", "messages", "notification"]:
        # The new value of the property is returned by the function
        property_value = chat_settings.change_chat_properties(chat_id, button_data)
        # The keyboard's property button in changed to reflect the update
        inline_keyboard = keyboard_handler.edit_keyboard_properties(property_value, button_data, inline_keyboard)
        change_single_property(chat_id, button_data, property_value, context.job_queue)
    # The statistics of the current day are sent to the chat
    elif button_data == "today_statistics":
        stats = statistic_message(chat_id, dt.datetime.now(tz=TIMEZONE).strftime(DATE_FORMAT))
        button_pressed.message.reply_markdown_v2(stats)
    # The statistics of a past day are sent to the chat
    elif button_pressed.data.endswith("-statistics"):
        stats = statistic_message(chat_id, button_pressed.data.split("-")[0])
        button_pressed.message.reply_markdown_v2(stats)
    # Other type of button is pressed
    else:
        inline_keyboard = keyboard_handler.handle_change_keyboard(button_data, chat_id, inline_keyboard)

    button_pressed.answer()
    try:
        button_pressed.edit_message_reply_markup(InlineKeyboardMarkup(inline_keyboard))
    except TelegramError as exc:
        LOGGER.info(exc.message)

    LOGGER.info(f"Button {button_pressed.data} pressed by {chat_id} | {update.effective_user.full_name}")


def callback_counter_messages(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_full_name = update.message.from_user.full_name
    tz_date = (update.message.date.astimezone(tz=TIMEZONE)).strftime(DATE_FORMAT)

    if update.message.text:
        category = "Messages"
        count = 1
    elif update.message.voice:
        category = "Voices"
        count = update.message.voice.duration
    elif update.message.video_note:
        category = "Videonotes"
        count = update.message.video_note.duration

    try:
        manage_stats.set_statistic_counter(count, category, chat_id, user_id, user_full_name, tz_date)
    except NameError as exc:
        raise RuntimeError from exc


def callback_notification(context: CallbackContext):
    chat_id = context.job.context

    today_datetime = dt.datetime.now(tz=TIMEZONE)
    date_to_request = (today_datetime - dt.timedelta(days=1)).strftime(DATE_FORMAT)

    chat_statistics = statistic_message(chat_id, date_to_request)
    context.bot.send_message(chat_id=chat_id, parse_mode=ParseMode.MARKDOWN_V2, text=chat_statistics, disable_notification=True)

    LOGGER.info(f"Sent notification to {chat_id}")


def enable_user_properties(job: JobQueue):
    """All chats with properties enabled are retrieved from the database,
    then the job queue and the filters list are updated in order to be triggered"""
    enabled_properties = chat_settings.get_all_chats_enabled_properties()
    for chat_id, props in enabled_properties.items():
        for prop, value in props.items():
            change_single_property(chat_id, prop, value, job)


def change_single_property(chat_id: int, prop: str, value: bool, job_queue: JobQueue):
    """For the notification, it's added to the job queue if it doesn't exist and the
    property is enabled, otherwise it's enabled/disabled based on the property value.
    For the counting of the messages, they are added to the filter list if the property is
    enabled, otherwise it's removed (only if it's present in the list)"""
    if prop == "notification":
        jobs_name = job_queue.get_jobs_by_name(f"{chat_id}_notification")

        # The job queue doesn't contain any job for the notification to the chat
        if len(jobs_name) == 0 and value:
            midnight = dt.time(hour=00, minute=00, tzinfo=TIMEZONE)
            job_queue.run_daily(callback_notification, midnight, context=chat_id, name=f"{chat_id}_notification")
            LOGGER.info(f"Added notification for {chat_id}")
        else:
            for jobs_entry in jobs_name:
                jobs_entry.enabled = value
                LOGGER.info(f"Edited notification for {chat_id} to {value}")
    else:
        if value and (chat_id not in filters_callback[prop].chat_ids):
            filters_callback[prop].add_chat_ids(chat_id)
            LOGGER.info(f"Added {prop} for {chat_id}")
        elif not value and (chat_id in filters_callback[prop].chat_ids):
            filters_callback[prop].remove_chat_ids(chat_id)
            LOGGER.info(f"Removed {prop} for {chat_id}")


def main():
    job_queue = updater.job_queue
    enable_user_properties(job_queue)

    # Filters
    text_filter = filters_callback["messages"] & (Filters.update.message & (Filters.text & ~(Filters.command)))
    voice_filter = filters_callback["voices"] & Filters.voice
    videonote_filter = filters_callback["videonotes"] & Filters.video_note

    # Handlers
    start_handler = CommandHandler("start", start)
    start_settings_handler = CommandHandler("start", settings)
    settings_handler = CommandHandler("settings", settings)
    help_handler = CommandHandler("help", help)
    keyboard_handler = CallbackQueryHandler(callback_inline_keyboard)
    message_handler = MessageHandler((text_filter | voice_filter | videonote_filter), callback_counter_messages)

    dispatcher.add_handler(start_handler, group=-1)
    dispatcher.add_handler(start_settings_handler, group=0)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(keyboard_handler)
    dispatcher.add_handler(message_handler)

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Bot has started")
    main()
