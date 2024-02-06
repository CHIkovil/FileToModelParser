from enum import Enum
from src.Web.Api.base_api import BaseApi


class WebServerStoreApi(str, Enum):
    convert = "convert"

    def on_value(self) -> str:
        return f"{BaseApi.to_parser()}/{self._value_}"
