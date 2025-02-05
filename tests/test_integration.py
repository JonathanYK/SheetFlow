import json

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def create_sheet(client, file_name):
    with open(file_name, 'r') as columns_data:
        sheet_creation_response = client.post(
            "/sheets",
            json=json.load(columns_data)
        )
    assert sheet_creation_response.status_code == 200
    return sheet_creation_response


def test_create_sheet_and_update_cell_integration(client):
    sheet_creation_response = create_sheet(client, 'columns_data_a.json')

    sheet_id = sheet_creation_response.json()
    create_cell(client, sheet_id, "D", "100", "500")


def test_create_sheet_and_update_cell_lookup_integration(client):
    sheet_creation_response = create_sheet(client, 'columns_data_b.json')
    sheet_id = sheet_creation_response.json()

    create_cell(client, sheet_id, "A", "10", "hello")
    create_cell(client, sheet_id, "B", "11", "true")
    create_cell(client, sheet_id, "C", "1", "lookup(“A”,10)")

    get_cells_response = get_all_cells(client, sheet_id)
    assert get_cells_response.status_code == 200
    assert (get_cells_response.json() ==
            {
                "('A', '10')": "hello",
                "('B', '11')": "true",
                "('C', '1')": "hello"
            })


def test_create_sheet_and_update_cell_lookup_cycle_integration(client):
    sheet_creation_response = create_sheet(client, 'columns_data_b.json')
    sheet_id = sheet_creation_response.json()

    create_cell(client, sheet_id, "C", "1", "lookup(“A”,1)")

    create_cell(client, sheet_id, "A", "1", "lookup(“B”,1)")

    cell_creation_lookup_c1_lookup_cycle_response = client.post(
        url="/cells/",
        headers={"sheet-id": sheet_id},
        json={
            "column": "B",
            "row": "1",
            "value": "lookup(“C”,1)"
        }
    )
    assert cell_creation_lookup_c1_lookup_cycle_response.status_code == 504
    assert cell_creation_lookup_c1_lookup_cycle_response.json()[
               "detail"] == 'Lookup (C, 1) creates a cycle, which is not allowed.'


def create_cell(client, sheet_id: str, column: str, row: str, value: str):
    cell_creation_c1_lookup_response = client.post(
        url="/cells/",
        headers={"sheet-id": sheet_id},
        json={
            "column": f"{column}",
            "row": f"{row}",
            "value": f"{value}"
        }
    )
    assert cell_creation_c1_lookup_response.status_code == 200
    return cell_creation_c1_lookup_response.json()


def get_all_cells(client, sheet_id: str):
    return client.get(
        url="/cells/",
        headers={"sheet-id": sheet_id}
    )


def test_create_sheet_reassign_lookup_integration(client):
    """
    Test edge cases in lookup behavior
    1. lookup values not part of cell_values
    2. validate lookup chain returns all chain values
    3. concat the chain, validate lookup chain without values not returned in cell_values
    4. set the latest lookup value pointer to actual value, ensure the concat chain is set to latest lookup value
    """

    sheet_creation_response = create_sheet(client, 'columns_data_b.json')
    sheet_id = sheet_creation_response.json()

    # create initial cells with lookup chains
    create_cell(client, sheet_id, "A", "100", "100")
    create_cell(client, sheet_id, "A", "1", "lookup(A,2)")
    create_cell(client, sheet_id, "A", "2", "lookup(A,3)")

    all_cells = get_all_cells(client, sheet_id)
    assert all_cells.status_code == 200
    assert all_cells.json() == {"('A', '100')": '100'}

    # add resolvable lookup chain
    create_cell(client, sheet_id, "A", "3", "3")
    all_cells = get_all_cells(client, sheet_id)
    assert all_cells.status_code == 200
    assert all_cells.json() == {"('A', '1')": '3', "('A', '100')": '100', "('A', '2')": '3', "('A', '3')": '3'}

    # add lookup that concat the chain and removes previous chain values
    create_cell(client, sheet_id, "A", "3", "lookup(A,4)")
    all_cells = get_all_cells(client, sheet_id)
    assert all_cells.status_code == 200
    assert all_cells.json() == {"('A', '100')": '100'}

    # resolve the lookup chain by setting the final value
    create_cell(client, sheet_id, "A", "4", "4")
    all_cells = get_all_cells(client, sheet_id)
    assert all_cells.status_code == 200
    assert all_cells.json() == {"('A', '1')": '4', "('A', '100')": '100', "('A', '2')": '4', "('A', '3')": '4', "('A', '4')": '4'}
