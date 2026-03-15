import io
from unittest.mock import patch


def _fake_image_bytes():
    """Create a minimal valid JPEG for testing."""
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(buf, format="JPEG")
    return buf.getvalue()


MOCK_OCR_TEXT = (
    "Starbucks\n"
    "123 Main St\n"
    "03/15/2026\n"
    "Latte         4.50\n"
    "Muffin        2.75\n"
    "Subtotal      7.25\n"
    "Tax           0.65\n"
    "Total         7.90\n"
)


@patch("app.services.ocr_service.extract_text", return_value=(MOCK_OCR_TEXT, 0.92))
def test_extract_parses_receipt(mock_ocr, client):
    data = {"image": (io.BytesIO(_fake_image_bytes()), "receipt.jpg")}
    resp = client.post("/api/ocr/extract", content_type="multipart/form-data", data=data)
    assert resp.status_code == 200
    result = resp.get_json()
    assert result["vendor_name"] == "Starbucks"
    assert result["date"] == "2026-03-15"
    assert result["total"] == 7.90
    assert result["tax"] == 0.65
    assert len(result["line_items"]) >= 1


@patch("app.services.ocr_service.extract_text", return_value=("", 0.0))
def test_extract_empty_ocr_returns_empty_form(mock_ocr, client):
    data = {"image": (io.BytesIO(_fake_image_bytes()), "receipt.jpg")}
    resp = client.post("/api/ocr/extract", content_type="multipart/form-data", data=data)
    assert resp.status_code == 200
    result = resp.get_json()
    assert result["vendor_name"] is None
    assert result["line_items"] == []


def test_extract_no_file(client):
    resp = client.post("/api/ocr/extract")
    assert resp.status_code == 400


def test_extract_invalid_extension(client):
    data = {"image": (io.BytesIO(b"fake"), "file.txt")}
    resp = client.post("/api/ocr/extract", content_type="multipart/form-data", data=data)
    assert resp.status_code == 400
