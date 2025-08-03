from typing import Dict, Tuple, Any
from starlette.responses import JSONResponse

from app.exceptions.exceptions import InvalidCellValueError, CyclicLookupError
from app.services.cell_schema import CellUpdateSchema
from app.services.sheet_values_json_encoder import SheetValuesJsonEncoder
from app.services.sheets_service import sheets
from bidict import bidict
from typing import Optional

BOOLEAN = "boolean"
INT = "int"
STRING = "string"
DOUBLE = "double"

cell_values: Dict[str, Dict[Tuple[str, str], str]] = {}
cell_lookup_dependencies: Dict[str, bidict] = {}


def update_cell_in_sheet(sheet_id: str, column: str, row: str, value: str) -> None:

    print(f"Updating sheet {sheet_id}: row {row}, column {column}, value {value}")

    # Initialize the sheet if it doesn't exist
    if sheet_id not in cell_values:
        cell_values[sheet_id] = {}

    # Update the cell value
    cell_values[sheet_id][(column, row)] = value


def is_value_of_cell_type(cell_type, value) -> bool:
    """Validate if the value matches the expected cell type."""
    try:
        if cell_type == BOOLEAN:
            return value.lower() in {"true", "false"}
        if cell_type == INT:
            return value.isdigit()
        if cell_type == STRING:
            return isinstance(value, str)
        if cell_type == DOUBLE:
            float(value)
            return True
        return False
    except (ValueError, AttributeError):
        return False


def get_cell_value_type(sheet_id, lookup_column, lookup_row) -> str:
    """Retrieve the type of cell value."""
    return cell_values[sheet_id][(lookup_column, lookup_row)]


async def handle_cell_value_update(sheet_id: str, cell_update: CellUpdateSchema)-> Dict[str, Any]:
    """Handle the update of a cell value, including lookups."""

    # Handle lookup
    if cell_update.value.startswith("lookup("):
        await remove_lookup_value_if_exists(cell_update.column, cell_update.row, sheet_id)
        await handle_lookup_value(cell_update, sheet_id)

    else:
        # validate cell value type
        if not is_value_of_cell_type(sheets[sheet_id][cell_update.column], cell_update.value):
            raise InvalidCellValueError(cell_update.column, sheets[sheet_id][cell_update.column], cell_update.value)

        update_cell_in_sheet(
            sheet_id=sheet_id,
            column=cell_update.column,
            row=cell_update.row,
            value=cell_update.value,
        )

    return {"message": "Cell updated successfully.", "sheet_id": sheet_id, "cell_update": cell_update.model_dump()}


def check_cycle(lookup_column: str, lookup_row: str, cell_column, cell_row, sheet_id: str) -> Optional[tuple[str, str]]:
    """Check for cycles in lookup dependencies."""
    if lookup_column == cell_column and lookup_row == cell_row:
        raise CyclicLookupError(lookup_column, lookup_row)

    if sheet_id in cell_lookup_dependencies and (cell_column, cell_row) in cell_lookup_dependencies[sheet_id].inv:
        if (lookup_column, lookup_row) in cell_lookup_dependencies[sheet_id] or (lookup_column == cell_column and lookup_row == cell_row):
            raise CyclicLookupError(lookup_column, lookup_row)


async def remove_lookup_value_if_exists(cell_column: str, cell_row: str, sheet_id: str):
    if sheet_id in cell_values and (cell_column, cell_row) in cell_values[sheet_id]:
        del cell_values[sheet_id][(cell_column, cell_row)]


async def handle_lookup_value(cell_update: CellUpdateSchema, sheet_id: str) -> None:
    """Handle lookup values and maintain dependencies."""
    inside_brackets = cell_update.value[7:-1]
    lookup_column, lookup_row = inside_brackets.split(",")
    lookup_column = lookup_column.strip('“”')

    check_cycle(lookup_column, lookup_row, cell_update.column, cell_update.row, sheet_id)

    if sheet_id not in cell_lookup_dependencies:
        cell_lookup_dependencies[sheet_id] = bidict()

    if (cell_update.column, cell_update.row) in cell_lookup_dependencies[sheet_id]:
        del cell_lookup_dependencies[sheet_id][(cell_update.column, cell_update.row)]
    if (lookup_column, lookup_row) in cell_lookup_dependencies[sheet_id].inv:
        del cell_lookup_dependencies[sheet_id].inv[(lookup_column, lookup_row)]
    cell_lookup_dependencies[sheet_id][(cell_update.column, cell_update.row)] = (lookup_column, lookup_row)


def handle_lookup_values(sheet_id: str) -> Dict[Tuple[str, str], str]:
    """Resolve lookup values for all cells in a sheet."""
    sheet_cell_values = cell_values[sheet_id].copy()
    for key, value in list(cell_values[sheet_id].items()):
        if key in cell_lookup_dependencies[sheet_id].inv:
            prev_lookup_cell = cell_lookup_dependencies[sheet_id].inv[key]
            sheet_cell_values[cell_lookup_dependencies[sheet_id].inv[key]] = value
            while prev_lookup_cell and prev_lookup_cell in cell_lookup_dependencies[sheet_id].inv:
                sheet_cell_values[cell_lookup_dependencies[sheet_id].inv[prev_lookup_cell]] = value
                prev_lookup_cell = cell_lookup_dependencies[sheet_id].inv[prev_lookup_cell]
    return sheet_cell_values


async def get_sheet_cells(sheet_id: str) -> JSONResponse:
    """Get all cells of a sheet, resolving lookups."""

    if not cell_lookup_dependencies or not cell_lookup_dependencies[sheet_id]:
        cell_values_with_lookup = cell_values[sheet_id]
    else:
        cell_values_with_lookup = handle_lookup_values(sheet_id)
    return JSONResponse(content=SheetValuesJsonEncoder.encode(cell_values_with_lookup))

