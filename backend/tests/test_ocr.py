import json
from unittest.mock import patch, MagicMock
import io


MOCK_EXTRACTED = {
    "vendor_name": "Mock Store",
    "date": "2026-03-15",
    "currency": "USD",
    "subtotal": 9.00,
    "tax": 1.00,
    "total": 10.00,
    "line_items": [{"description": "Mock Item", "quantity": 1, "unit_price": 9.00, "total_price": 9.00}],
    "_source": "paddle_ocr+claude_text",
}


def _fake_image_bytes():
    """Create a minimal valid JPEG bytes for testing."""
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    img.save(buf, format="JPEG")
    return buf.getvalue()


@patch("app.services.ocr_service.extract_text", return_value=("Store\nTotal 10.00", 0.95))
@patch("app.services.claude_service.extract_with_text", return_value=MOCK_EXTRACTED)
def test_extract_uses_paddle_when_confident(mock_claude, mock_ocr, client):
    data = {"image": (io.BytesIO(_fake_image_bytes()), "receipt.jpg")}
    resp = client.post("/api/ocr/extract", content_type="multipart/form-data", data=data)
    assert resp.status_code == 200
    result = resp.get_json()
    assert result["vendor_name"] == "Mock Store"
    assert result["total"] == 10.00
    mock_claude.assert_called_once()


@patch("app.services.ocr_service.extract_text", return_value=("", 0.30))
@patch("app.services.claude_service.extract_with_vision", return_value={**MOCK_EXTRACTED, "_source": "claude_vision"})
def test_extract_falls_back_to_vision_on_low_confidence(mock_vision, mock_ocr, client):
    data = {"image": (io.BytesIO(_fake_image_bytes()), "receipt.jpg")}
    resp = client.post("/api/ocr/extract", content_type="multipart/form-data", data=data)
    assert resp.status_code == 200
    result = resp.get_json()
    mock_vision.assert_called_once()


def test_extract_no_file(client):
    resp = client.post("/api/ocr/extract")
    assert resp.status_code == 400


def test_extract_invalid_extension(client):
    data = {"image": (io.BytesIO(b"fake"), "file.txt")}
    resp = client.post("/api/ocr/extract", content_type="multipart/form-data", data=data)
    assert resp.status_code == 400
