from src.Parser.Operations.file_parsing_operations import FileParserOperations
from src.Models.parsing_models import ParsingModel


class FileToModelParser(FileParserOperations):
    def __init__(self, *,
                 item: ParsingModel
                 ):
        self._item = item

    async def run(self):
        return await self.parse_file_to_models(item=self._item)
