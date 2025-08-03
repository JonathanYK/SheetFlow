from typing import List
from pydantic import BaseModel, Field
from app.services.column import Column


class SheetSchema(BaseModel):
    columns: List[Column] = Field(..., description="List of columns for the sheet.")

