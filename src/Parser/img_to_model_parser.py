from pytesseract import image_to_string
from pathlib import Path
from src.Parser.img_parser_operations import ImgParserOperations


class ImageToModelParser(ImgParserOperations):
    def __init__(self, *,
                 data: Path or str,
                 language_code: str = 'rus',
                 models_description: dict
                 ):
        self._data = data
        self._language_code = language_code
        self._models_description = models_description

    async def run(self):
        return await self._parse_image_to_models(data=self._data,
                                                 language_code=self._language_code,
                                                 models_description=self._models_description)
