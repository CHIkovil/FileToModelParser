from enum import Enum


class BaseApi(str, Enum):
    base_api = "api"
    parser = "parser"

    @staticmethod
    def to_base() -> str:
        return f"/{BaseApi.base_api.value}"

    @staticmethod
    def to_parser() -> str:
        return f"/{BaseApi.base_api.value}/{BaseApi.parser.value}"
