# bot/logs/__init__.py

"""
Logs package initializer.

This package handles logging utilities for the Klavia bot system.
You can put shared log helpers, configurations, or setup here.
"""

import logging
import os

# Configure a base logger for your bot logs package
logger = logging.getLogger("klavia_bot.logs")
logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Example file handler setup — you can customize the file name and format
file_handler = logging.FileHandler(os.path.join(LOG_DIR, 'bot.log'))
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# You can also add console handler if you want logs in console during dev
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Expose logger for easy imports elsewhere
__all__ = ['logger']

