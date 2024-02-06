from logging import getLogger
from fastapi import APIRouter

from fastapi.exceptions import HTTPException
from src.Web.Api.web_server_parsing_api import WebServerStoreApi
from src.Models.parsing_models import ParserResultModel, ParsingModel
from src.Parser.file_parser import FileToModelParser

LOGGER = getLogger()


class WebServerParsingHandler:
    ROUTER = APIRouter()

    @staticmethod
    @ROUTER.get(WebServerStoreApi.convert.on_value())
    async def convert_file_to_model(item: ParsingModel) -> ParserResultModel:
        try:

            parser = FileToModelParser(item=item)

            result = await parser.run()

            return result
        except HTTPException:
            raise
        except Exception as error:
            LOGGER.error(error)
            raise HTTPException(status_code=500)
