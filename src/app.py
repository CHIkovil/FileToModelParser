from logging import getLogger
from sys import exit
from src.Web.Server.web_server import WebServer

from config import (
    UVICORN_SERVER_HOST,
    UVICORN_SERVER_PORT,
)

LOGGER = getLogger()

if not UVICORN_SERVER_HOST \
        or not UVICORN_SERVER_PORT:
    LOGGER.error("None value env")
    exit(1)


def _setup_web_server() -> WebServer:
    return WebServer(host=UVICORN_SERVER_HOST,
                     port=int(UVICORN_SERVER_PORT))


if __name__ == "__main__":
    try:
        server = _setup_web_server()
        server.start()
    except Exception as error:
        LOGGER.error(error)


