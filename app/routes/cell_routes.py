from fastapi import APIRouter, Header, HTTPException
from app.services.cell_schema import CellUpdateSchema
from app.services.cell_service import handle_cell_value_update, get_sheet_cells, is_value_of_cell_type, cell_values
from app.services.sheets_service import sheets
import app.exceptions.exceptions as exceptions

cell_router = APIRouter()


@cell_router.post("/")
async def set_cell(
        sheet_id: str = Header(None),
        cell_update: CellUpdateSchema = None):
    """
    Endpoint to update a cell in a sheet by sheet ID.
    Args:
        sheet_id (str): The ID of the sheet to update.
        cell_update (CellUpdateSchema): The details of the cell update, including row, column, value, and user_id.
    Returns:
        dict: A confirmation message indicating the cell has been updated.
    """
    if not sheet_id:
        raise HTTPException(status_code=404, detail="Sheet ID is required and cannot be empty.")
    if sheet_id not in sheets:
        raise HTTPException(status_code=404, detail=f"Sheet ID: {sheet_id} does not exist.")
    if cell_update.column not in sheets[sheet_id]:
        raise HTTPException(status_code=400, detail=f"Column '{cell_update.column}' does not exist in sheet '{sheet_id}'.")
    if not cell_update.value.startswith("lookup(") and not is_value_of_cell_type(sheets[sheet_id][cell_update.column], cell_update.value):
        raise HTTPException(status_code=422, detail=(
            f"Invalid value for column '{cell_update.column}'. Expected type: '{sheets[sheet_id][cell_update.column]}', but received: '{cell_update.value}'."
        ))
    try:
        await handle_cell_value_update(sheet_id, cell_update)
    except exceptions.CyclicLookupError as cyclic_lookup_error:
        raise HTTPException(status_code=504, detail=str(cyclic_lookup_error))


@cell_router.get("/")
async def get_cells_of_specific_sheet(sheet_id: str = Header(None)):
    if sheet_id not in sheets:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Sheet with id: '{sheet_id}' not found."
            )
        )

    if not cell_values:
        raise HTTPException(
            status_code=204,
            detail=f"No cell values found for sheet with ID '{sheet_id}'."
        )

    return await get_sheet_cells(sheet_id)

