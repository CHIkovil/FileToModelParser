from logging import getLogger
from src.Error.parsing_error import ParsingError

from asyncio import (to_thread as aio_thread)
from pytesseract import image_to_string
from re import compile as re_compile
from pypdf import PdfReader
from io import BytesIO
from numpy import (array as np_array,
                   frombuffer as np_frombuffer,
                   uint8)
from cv2 import (imdecode as cv2_imdecode,
                 IMREAD_ANYCOLOR)
from src.Models.parsing_models import (DataType,
                                       DynamicModel)

LOGGER = getLogger()


class FileParsingUtils:
    @staticmethod
    def _create_model(*, fields: dict) -> DynamicModel:
        result = None

        try:
            result = DynamicModel(**fields)

        except Exception as error:
            LOGGER.error(error)
        finally:
            return result

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
    async def _get_text_from_data(*, data: bytes,
                                  data_type: DataType,
                                  language_code: str or None) -> (str, str):
        result = None
        error = None

        try:
            if data_type == DataType.pdf:
                with BytesIO(data) as buffer:
                    reader = await aio_thread(PdfReader, buffer)

                    pdf_text = ''

                    for page in reader.pages:
                        for image in page.images:
                            tesseract_text = await FileParsingUtils._get_text_from_image_data(data=image.data,
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
    async def _get_text_from_image_data(*,
                                        data: bytes,
                                        language_code: str or None) -> str or None:
        result = None

        try:
            array = np_array(np_frombuffer(data, dtype=uint8))

            image = await aio_thread(cv2_imdecode, array, IMREAD_ANYCOLOR)

            result = await aio_thread(image_to_string,
                                      image,
                                      config=f"-l {language_code if language_code else 'rus'}")
        except Exception as error:
            LOGGER.error(error)
        finally:
            return result
