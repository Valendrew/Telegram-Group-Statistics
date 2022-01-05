from telegram.ext import Updater
import os
import logging
from logging.handlers import TimedRotatingFileHandler

from .mongodb import MongoDB

# logging_handler = [TimedRotatingFileHandler("log.txt", when="D", interval=14, backupCount=6), logging.StreamHandler()]
logging_handler = [logging.StreamHandler()]
logging.basicConfig(
    level=logging.WARNING,
    handlers=logging_handler,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher

MongoDB.initialize()
