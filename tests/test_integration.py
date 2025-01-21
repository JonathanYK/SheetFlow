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
    cell_creation_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "D",
            "row": "100",
            "value": "500"
        }
    )
    assert cell_creation_response.status_code == 200
    assert cell_creation_response.json()["message"] == "Cell updated successfully."


def test_create_sheet_and_update_cell_lookup_integration(client):
    sheet_creation_response = create_sheet(client, 'columns_data_b.json')
    sheet_id = sheet_creation_response.json()
    cell_creation_a10_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "A",
            "row": "10",
            "value": "hello"
        }
    )
    assert cell_creation_a10_response.status_code == 200

    cell_creation_b11_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "B",
            "row": "11",
            "value": "true"
        }
    )
    assert cell_creation_b11_response.status_code == 200

    cell_creation_lookup_c1_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "C",
            "row": "1",
            "value": "lookup(A,10)"
        }
    )
    assert cell_creation_lookup_c1_response.status_code == 200

    get_cells_response = client.get(
        f"/cells/?sheet_id={sheet_id}"
    )
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
    cell_creation_c1_lookup_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "C",
            "row": "1",
            "value": "lookup(“A”,1)"
        }
    )
    assert cell_creation_c1_lookup_response.status_code == 200

    cell_creation_b1_lookup_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "A",
            "row": "1",
            "value": "lookup(“B”,1)"
        }
    )
    assert cell_creation_b1_lookup_response.status_code == 200

    cell_creation_lookup_c1_lookup_cycle_response = client.post(
        f"/cells/?sheet_id={sheet_id}",
        json={
            "sheet_id": sheet_id,
            "column": "B",
            "row": "1",
            "value": "lookup(C,1)"
        }
    )
    assert cell_creation_lookup_c1_lookup_cycle_response.status_code == 500
    assert cell_creation_lookup_c1_lookup_cycle_response.json()["detail"] == 'Lookup ( C, 1 ) creates cycle, that are not allowed.'

