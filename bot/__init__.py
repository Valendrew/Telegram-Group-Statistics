import logging
import os
from logging.handlers import TimedRotatingFileHandler
from .mongodb import MongoDB

# logging_handler = [TimedRotatingFileHandler("log.txt", when="D", interval=14, backupCount=6), logging.StreamHandler()]
logging_handler = [logging.StreamHandler()]

logging.basicConfig(
    level=logging.INFO,
    handlers=logging_handler,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)
TOKEN = os.environ.get("BOT_TOKEN")
MongoDB.initialize()