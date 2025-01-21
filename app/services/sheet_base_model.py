from typing import ClassVar
from pydantic import BaseModel


class SheetBaseModel(BaseModel):
    valid_types: ClassVar[set] = {"string", "double", "int", "boolean"}

