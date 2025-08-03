from pydantic import Field, field_validator
from app.services.sheet_base_model import SheetBaseModel


class Column(SheetBaseModel):
    name: str = Field(..., min_length=1, description="The name of the column.")
    type: str = Field(..., description="The data type of the column. Accepted values: boolean, int, double, string.")

    # Custom field validator for the "type" field
    @field_validator("type")
    def validate_type(cls, value):
        if value not in cls.valid_types:
            raise ValueError(f"Invalid type '{value}'. Valid types are: {', '.join(cls.valid_types)}")
        return value

