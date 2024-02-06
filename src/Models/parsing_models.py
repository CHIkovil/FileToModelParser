from enum import Enum
from pydantic import BaseModel, Extra
from typing import Optional


class ExtendedEnum(Enum):
    @classmethod
    def set(cls):
        return set(map(lambda c: c.value, cls))


class DataType(str, ExtendedEnum):
    pdf = "pdf"


class ParsingModel(BaseModel):
    file: bytes
    type: DataType
    language_code: Optional[str] = None
    models_description: dict


class DynamicModel(BaseModel, extra=Extra.allow):
    pass


class ParserConvertModel(BaseModel):
    name: str
    result: Optional[DynamicModel]
    error: Optional[str]


class ParserResultModel(BaseModel):
    results: Optional[list[ParserConvertModel]]
    error: Optional[str]

    def __str__(self):
        return f'attrs: result - {list(map(lambda x: x.dict(), self.results))} \n error - {self.error} '
