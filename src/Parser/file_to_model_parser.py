from pathlib import Path
from src.Parser.file_parser_operations import FileParserOperations, DataType


class FileToModelParser(FileParserOperations):
    def __init__(self, *,
                 data: Path or str,
                 data_type: DataType,
                 language_code: str = 'rus',
                 models_description: dict
                 ):
        self._data = data
        self._data_type = data_type
        self._language_code = language_code
        self._models_description = models_description

    async def run(self):
        return await self.parse_file_to_models(data=self._data,
                                               data_type=self._data_type,
                                               language_code=self._language_code,
                                               models_description=self._models_description)
