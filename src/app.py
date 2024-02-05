from src.Parser.file_to_model_parser import FileToModelParser
from src.Parser.file_parser_operations import DataType
from asyncio import run as aio_run
from aiofiles import open as aio_open
from pathlib import Path



if __name__ == "__main__":
    aio_run(on_example_script())

