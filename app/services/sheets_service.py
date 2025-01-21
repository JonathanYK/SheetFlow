import uuid
from typing import Dict
from fastapi import HTTPException
from app.services.sheet_schema import SheetSchema

sheets: Dict[str, Dict[str, str]] = {}


async def handle_sheet_creation(sheet: SheetSchema) -> str:
    """Create a new sheet with a unique ID and store it in memory"""

    # unique id for new sheet
    sheet_id = str(uuid.uuid4())
    sheets[sheet_id] = {item["name"]: item["type"] for item in sheet.dict()["columns"]}
    return sheet_id


async def get_sheet_by_id(sheet_id: str) -> Dict[str, str]:
    """Retrieve a sheet by its ID"""
    if sheet_id not in sheets:
        raise HTTPException(status_code=404, detail=f"Sheet with id: {sheet_id} not found")
    return sheets[sheet_id]