# src/__init__.py
import logging
import os

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(asctime)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Load the .env file
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOTENV_PATH = os.path.join(ROOT_DIR, ".env")
DOTENV_LOADED = load_dotenv(DOTENV_PATH)

if DOTENV_LOADED:
    logger.debug(f"Successfully loaded .env file from {DOTENV_PATH}")
else:
    logger.warning(f"Could not find .env file in the root directory {ROOT_DIR}")
