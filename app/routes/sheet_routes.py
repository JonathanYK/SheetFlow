from fastapi import APIRouter

from app.services.sheet_schema import SheetSchema
from app.services.sheets_service import handle_sheet_creation, get_sheet_by_id

sheet_router = APIRouter()


@sheet_router.get("/")
async def query_sheet_by_id(sheet_id: str = None) -> SheetSchema:
    """
    Endpoint to retrieve a sheet by its ID.

    Args:
       sheet_id (str, optional): The ID of the sheet to be retrieved. Defaults to None.

    Returns:
       Sheet: The sheet corresponding to the provided ID, or None if not found.
    """
    return await get_sheet_by_id(sheet_id)


@sheet_router.post("/")
async def create_sheet(sheet: SheetSchema) -> str:
    """
    Endpoint to create a new sheet with the specified schema.
    Args:
        sheet (SheetSchema): The schema for the new sheet.
    Returns:
        str: The ID of the newly created sheet.
    """
    return await handle_sheet_creation(sheet)

