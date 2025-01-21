from fastapi import APIRouter

from app.services.cell_schema import CellUpdateSchema
from app.services.cell_service import handle_cell_value_update, get_sheet_cells

cell_router = APIRouter()


@cell_router.post("/")
async def set_cell(sheet_id: str, cell_update: CellUpdateSchema):
    """
    Endpoint to update a cell in a sheet by sheet ID.

    Args:
        sheet_id (str): The ID of the sheet to update.
        cell_update (CellUpdateSchema): The details of the cell update, including row, column, value, and user_id.

    Returns:
        dict: A confirmation message indicating the cell has been updated.
    """
    return await handle_cell_value_update(sheet_id, cell_update)


@cell_router.get("/")
async def get_sheet(sheet_id: str):
    return await get_sheet_cells(sheet_id)