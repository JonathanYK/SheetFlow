from pydantic import Field
from app.services.sheet_base_model import SheetBaseModel


class CellUpdateSchema(SheetBaseModel):
    column: str = Field(..., description="The column letter.")
    row: str = Field(..., description="The row number(string).")
    value: str = Field(..., min_length=1, description="The value to set in the cell (must not be empty).")

