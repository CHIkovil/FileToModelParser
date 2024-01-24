from cv2 import (imread as cv2_imread)

from pytesseract import image_to_string
from logging import getLogger
from pathlib import Path
from asyncio import (to_thread as aio_thread,
                     create_task as aio_task,
                     gather as aio_gather)

from re import compile as re_compile

LOGGER = getLogger()


class DynamicModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class ImgParserOperations:
    @staticmethod
    async def _parse_image_to_models(*, data: Path or str, language_code: str, models_description: dict):
        result = None

        try:

            if isinstance(data, Path):

                image = await aio_thread(cv2_imread, data)
                text = await aio_thread(image_to_string, image, config=f"-l {language_code}")

            elif isinstance(data, str) and not Path(data).exists():

                text = data

            tasks = [aio_task(ImgParserOperations._parse_text_to_model(text=text,
                                                                       model_description=obj))
                     for obj
                     in
                     models_description.items()]

            result = await aio_gather(*tasks)

        except Exception as error:
            LOGGER.error(error)
        finally:
            return result

    @staticmethod
    async def _parse_text_to_model(*, text: str, model_description: tuple) -> list or None:

        result = None

        try:

            field_regexs = list(map(lambda obj: obj[1][1], sorted(model_description[1].items())))

            regex = r'[\s\S]*'.join(field_regexs)

            pattern = re_compile(regex)

            match_obj = await aio_thread(pattern.search, text)

            if not match_obj:
                return

            groups = match_obj.groups()

            if len(groups) != len(field_regexs):
                return

            fields = {model_description[1][index][0]: value.strip() for (index, value) in enumerate(groups, start=1)}

            result = ImgParserOperations._create_model(model_name=model_description[0], fields=fields)

        except Exception as error:
            LOGGER.error(error)
        finally:
            return result

    @staticmethod
    def _create_model(*, model_name: str, fields: dict) -> DynamicModel:
        result = None

        try:
            result = type(model_name, (DynamicModel,), fields)

        except Exception as error:
            LOGGER.error(error)
        finally:
            return result
