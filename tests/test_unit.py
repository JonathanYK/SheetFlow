import pytest
from bidict import bidict

from app.services.cell_service import (
    update_cell_in_sheet,
    is_value_of_cell_type,
    get_cell_value_type,
    handle_lookup_values, cell_values, cell_lookup_dependencies,
)

def test_update_cell_in_sheet():
    sheet_id = "test_sheet"
    column, row, value = "A", "1", "42"
    update_cell_in_sheet(sheet_id, column, row, value)
    assert cell_values[sheet_id][(column, row)] == value


@pytest.mark.parametrize(
    "cell_type, value, expected",
    [
        ("boolean", "true", True),
        ("boolean", "false", True),
        ("boolean", "invalid", False),
        ("int", "123", True),
        ("int", "12.3", False),
        ("string", "text", True),
        ("double", "12.3", True),
        ("double", "invalid", False),
    ],
)
def test_is_value_of_cell_type(cell_type, value, expected):
    assert is_value_of_cell_type(cell_type, value) == expected


def test_get_cell_value_type():
    sheet_id = "test_sheet"
    column, row, value = "A", "1", "42"
    update_cell_in_sheet(sheet_id, column, row, value)

    # Assert the value type
    assert get_cell_value_type(sheet_id, column, row) == value


def test_handle_lookup_values():
    sheet_id = "test_sheet"
    column, row, value = "A", "1", "42"
    update_cell_in_sheet(sheet_id, column, row, value)
    cell_lookup_dependencies[sheet_id] = bidict({("B", "2"): ("A", "1")})

    updated_values = handle_lookup_values(sheet_id)
    assert updated_values[("B", "2")] == "42"