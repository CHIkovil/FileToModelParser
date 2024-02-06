from src.Support.base_singleton import BaseSingleton
from uvicorn import (Config as UvConfig, Server as UvServer)
from fastapi import FastAPI
from src.Web.Handlers.web_server_parsing_handler import WebServerParsingHandler


class WebServer(BaseSingleton,
                WebServerParsingHandler):
    def __init__(self, *, host: str,
                 port: int):
        self._host = host
        self._port = port
        self._app = FastAPI()
        self._setup()

    def _setup(self):
        for cls in self.__class__.__mro__:
            if cls.__name__.endswith("Handler"):
                self._app.include_router(cls.ROUTER)

        self._server = UvServer(config=UvConfig(self._app,
                                                host=self._host,
                                                port=self._port,
                                                reload=False,
                                                log_level="debug"))

    def start(self):
        self._server.run()
