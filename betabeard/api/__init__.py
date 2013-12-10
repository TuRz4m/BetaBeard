import logging
import logging.handlers

logging.getLogger(__name__).addHandler(logging.handlers.RotatingFileHandler("logs/APIUtils.log", maxBytes=8192))
logging.getLogger(__name__).setLevel(logging.DEBUG)