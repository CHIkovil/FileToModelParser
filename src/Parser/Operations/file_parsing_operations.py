from logging import getLogger
from asyncio import (create_task as aio_task,
                     gather as aio_gather,
                     Task as AioTask,
                     Lock as AioLock)
from src.Error.parsing_error import ParsingError
from src.Models.parsing_models import (ParsingModel,
                                       ParserConvertModel,
                                       ParserResultModel)

from src.Parser.Utils.file_parsing_utils import FileParsingUtils
import base64

LOGGER = getLogger()


class FileParserOperations(FileParsingUtils):

    @staticmethod
    async def parse_file_to_models(*,
                                   item: ParsingModel) -> ParserResultModel:
        result = None
        error = None

        try:
            data = base64.b64decode(item.file)
            text, error = await FileParserOperations._get_text_from_data(data=data,
                                                                         data_type=item.type,
                                                                         language_code=item.language_code)

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

                for obj in item.models_description.items():
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
