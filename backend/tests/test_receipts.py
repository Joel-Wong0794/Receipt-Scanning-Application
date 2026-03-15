import json
from datetime import date


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


def test_create_receipt(client):
    payload = {
        "vendor_name": "Test Store",
        "date": "2026-03-15",
        "subtotal": "10.00",
        "tax": "1.00",
        "total": "11.00",
        "currency": "USD",
        "category": "Office Supplies",
        "notes": "Test receipt",
        "line_items": [
            {"description": "Item A", "quantity": "1", "unit_price": "5.00", "total_price": "5.00"},
            {"description": "Item B", "quantity": "1", "unit_price": "5.00", "total_price": "5.00"},
        ],
    }
    resp = client.post("/api/receipts", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["vendor_name"] == "Test Store"
    assert data["total"] == "11.00"
    assert len(data["line_items"]) == 2
    assert "external_id" in data
    return data["id"]


def test_list_receipts(client):
    resp = client.get("/api/receipts")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "receipts" in data
    assert "total" in data


def test_get_receipt(client):
    # Create one first
    payload = {"vendor_name": "Get Test", "total": "5.00"}
    create_resp = client.post("/api/receipts", json=payload)
    receipt_id = create_resp.get_json()["id"]

    resp = client.get(f"/api/receipts/{receipt_id}")
    assert resp.status_code == 200
    assert resp.get_json()["vendor_name"] == "Get Test"


def test_update_receipt(client):
    payload = {"vendor_name": "Update Test", "total": "5.00"}
    create_resp = client.post("/api/receipts", json=payload)
    receipt_id = create_resp.get_json()["id"]

    resp = client.put(f"/api/receipts/{receipt_id}", json={"vendor_name": "Updated Store"})
    assert resp.status_code == 200
    assert resp.get_json()["vendor_name"] == "Updated Store"


def test_delete_receipt(client):
    payload = {"vendor_name": "Delete Test", "total": "1.00"}
    create_resp = client.post("/api/receipts", json=payload)
    receipt_id = create_resp.get_json()["id"]

    resp = client.delete(f"/api/receipts/{receipt_id}")
    assert resp.status_code == 200

    get_resp = client.get(f"/api/receipts/{receipt_id}")
    assert get_resp.status_code == 404


def test_export_csv(client):
    resp = client.get("/api/receipts/export?format=csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.content_type


def test_export_workday_csv(client):
    resp = client.get("/api/receipts/export?format=workday_csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.content_type
    content = resp.data.decode("utf-8")
    assert "Transaction Date" in content
    assert "Supplier" in content
    assert "External Reference ID" in content


def test_export_json(client):
    resp = client.get("/api/receipts/export?format=json")
    assert resp.status_code == 200
    assert "application/json" in resp.content_type


def test_filter_by_vendor(client):
    client.post("/api/receipts", json={"vendor_name": "Starbucks", "total": "5.00"})
    client.post("/api/receipts", json={"vendor_name": "McDonald's", "total": "8.00"})

    resp = client.get("/api/receipts?vendor=starbucks")
    assert resp.status_code == 200
    data = resp.get_json()
    for r in data["receipts"]:
        assert "starbucks" in r["vendor_name"].lower()
