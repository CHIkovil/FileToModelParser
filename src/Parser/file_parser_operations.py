from cv2 import (imread as cv2_imread)

from pytesseract import image_to_string
from logging import getLogger
from asyncio import (to_thread as aio_thread,
                     create_task as aio_task,
                     gather as aio_gather,
                     Task as AioTask,
                     Lock as AioLock)

from re import compile as re_compile
from src.Error.parsing_error import ParsingError
from pypdf import PdfReader
from io import BytesIO
from pydantic import BaseModel, Extra
from typing import Optional
from enum import Enum
from numpy import (array as np_array,
                   frombuffer as np_frombuffer,
                   uint8)
from cv2 import (imdecode as cv2_imdecode,
                 IMREAD_ANYCOLOR)

LOGGER = getLogger()


class DataType(str, Enum):
    img = "img"
    pdf = "pdf"


class DynamicModel(BaseModel, extra=Extra.allow):
    pass


class ParserConvertModel(BaseModel):
    name: str
    result: Optional[DynamicModel]
    error: Optional[str]


class ParserResultModel(BaseModel):
    results: Optional[list[ParserConvertModel]]
    error: Optional[str]


class FileParserOperations:

    @staticmethod
    async def parse_file_to_models(*,
                                   data: bytes,
                                   data_type: DataType,
                                   language_code: str = 'rus',
                                   models_description: dict) -> (dict[DynamicModel or str], str or None):
        result = None
        error = None

        try:

            text, error = await FileParserOperations._get_text_from_data(data=data,
                                                                         data_type=data_type,
                                                                         language_code=language_code)

            if not error:

                convert_results = []
                lock = AioLock()

                async def on_callback(*,
                                      t: AioTask,
                                      results: list):
                    content = t.result()

                    async with lock:
                        results.append(content)

                tasks = []

                for obj in models_description.items():
                    task = aio_task(FileParserOperations._parse_text_to_model(text=text,
                                                                              model_description=obj))
                    task.add_done_callback((lambda t: aio_task(on_callback(t=t, results=convert_results))))
                    tasks.append(task)

                await aio_gather(*tasks)

                if len(convert_results) != 0:
                    result = convert_results
                else:
                    error = "Empty convert results"

                result = convert_results

        except (ParsingError, Exception) as err:
            LOGGER.error(err)
            error = err

        finally:
            return ParserResultModel(results=result,
                                     error=error)

    @staticmethod
    async def _parse_text_to_model(*,
                                   text: str,
                                   model_description: tuple) -> ParserConvertModel:

        result = None
        error = None

        try:
            field_results = {}
            lock = AioLock()

            async def on_callback(*,
                                  t: AioTask,
                                  results: dict):

                content = t.result()

                if isinstance(content, tuple):
                    async with lock:
                        results[content[0]] = content[1]

            tasks = []

            for obj in model_description[1].items():
                task = aio_task(FileParserOperations._search_pattern_in_text(text=text,
                                                                             field_obj=obj))

                task.add_done_callback((lambda t: aio_task(on_callback(t=t, results=field_results))))
                tasks.append(task)

            await aio_gather(*tasks)

            if len(field_results) != 0:
                result = FileParserOperations._create_model(fields=field_results)
            else:
                error = "Not create model with fields"

        except Exception as err:
            LOGGER.error(err)
            error = err

        finally:
            return ParserConvertModel(name=model_description[0],
                                      result=result,
                                      error=error)

    @staticmethod
    async def _get_text_from_data(*, data: bytes,
                                  data_type: DataType,
                                  language_code: str) -> (str, str):
        result = None
        error = None

        try:
            if data_type == DataType.img:
                tesseract_text = await FileParserOperations._get_text_from_image_data(data=data,
                                                                                      language_code=language_code)
                if tesseract_text:
                    result = tesseract_text
                else:
                    error = f"Tesseract not recognized {language_code} text from image"

            elif data_type == DataType.pdf:
                with BytesIO(data) as buffer:
                    reader = await aio_thread(PdfReader, buffer)

                    pdf_text = ''

                    for page in reader.pages:
                        for image in page.images:
                            tesseract_text = await FileParserOperations._get_text_from_image_data(data=image.data,
                                                                                                  language_code=language_code)
                            if tesseract_text:
                                pdf_text += tesseract_text
                            else:
                                error = f"Tesseract not recognized {language_code} text from images in pdf data"

                    if len(pdf_text) == 0:
                        error = "Pdf reader not extract text"
                    else:
                        result = pdf_text
            else:
                error = "Not correct data type for convert to text"

        except Exception as error:
            error = f"Unknown error when convert file data to text - {error}"

        finally:
            return result, error

    @staticmethod
    async def _search_pattern_in_text(*, text: str, field_obj: tuple) -> str or None:
        result = None

        try:
            pattern = re_compile(field_obj[1])

            match_obj = await aio_thread(pattern.search, text)

            if not match_obj:
                raise ParsingError(f'Not search match for field - {field_obj}')

            result = match_obj.group(1).strip()

        except ParsingError as error:
            LOGGER.warning(error)
        except Exception as error:
            LOGGER.error(error)
        finally:
            return field_obj[0], result

    @staticmethod
    async def _get_text_from_image_data(*,
                                        data: bytes,
                                        language_code: str) -> str or None:
        result = None

        try:
            array = np_array(np_frombuffer(data, dtype=uint8))

            image = await aio_thread(cv2_imdecode,array, IMREAD_ANYCOLOR)

            result = await aio_thread(image_to_string,
                                      image,
                                      config=f"-l {language_code}")
        except Exception as error:
            LOGGER.error(error)
        finally:
            return result

    @staticmethod
    def _create_model(*, fields: dict) -> DynamicModel:
        result = None

        try:
            result = DynamicModel(**fields)

        except Exception as error:
            LOGGER.error(error)
        finally:
            return result
