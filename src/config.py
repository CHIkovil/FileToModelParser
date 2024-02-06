import logging
from os import environ
from pathlib import Path

from dotenv import load_dotenv

LOGGER = logging.getLogger()

if not load_dotenv(Path("./.env")):
    LOGGER.error("Not found .env file")

UVICORN_SERVER_HOST = environ.get("UVICORN_SERVER_HOST")
UVICORN_SERVER_PORT = environ.get("UVICORN_SERVER_PORT")

