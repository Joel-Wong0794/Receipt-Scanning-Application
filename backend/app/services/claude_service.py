import base64
import json
import logging
import re
from io import BytesIO

from anthropic import Anthropic
from flask import current_app
from PIL import Image

logger = logging.getLogger(__name__)

STRUCTURE_PROMPT = """Parse this receipt text and return ONLY a JSON object with exactly these fields:
{
  "vendor_name": "string or null",
  "date": "YYYY-MM-DD or null",
  "currency": "USD",
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00,
  "line_items": [
    {
      "description": "string",
      "quantity": 1,
      "unit_price": null,
      "total_price": 0.00
    }
  ]
}
Rules:
- Use null for any field not found
- Never guess prices — use null if uncertain
- Return only the JSON object, no markdown, no explanation
- All monetary values must be numbers (not strings)
"""

VISION_PROMPT = """Extract all data from this receipt image and return ONLY a JSON object with exactly these fields:
{
  "vendor_name": "string or null",
  "date": "YYYY-MM-DD or null",
  "currency": "USD",
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00,
  "line_items": [
    {
      "description": "string",
      "quantity": 1,
      "unit_price": null,
      "total_price": 0.00
    }
  ]
}
Rules:
- Use null for any field not found
- Never guess prices — use null if uncertain
- Return only the JSON object, no markdown, no explanation
- All monetary values must be numbers (not strings)
"""


def _preprocess_image(image_bytes: bytes) -> tuple[bytes, str]:
    """Resize and convert image to JPEG, return (jpeg_bytes, media_type)."""
    img = Image.open(BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    max_height = 1600
    if img.height > max_height:
        ratio = max_height / img.height
        new_size = (int(img.width * ratio), max_height)
        img = img.resize(new_size, Image.LANCZOS)

    output = BytesIO()
    img.save(output, format="JPEG", quality=85)
    return output.getvalue(), "image/jpeg"


def _parse_json_response(text: str) -> dict:
    """Extract and parse JSON from Claude's response text."""
    text = text.strip()
    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def extract_with_vision(image_bytes: bytes) -> dict:
    """Send image directly to Claude Vision API and return structured receipt data."""
    client = Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])
    jpeg_bytes, media_type = _preprocess_image(image_bytes)
    b64 = base64.standard_b64encode(jpeg_bytes).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a receipt data extraction assistant. Return ONLY valid JSON. If a field is not found, use null. Never guess prices.",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                },
                {"type": "text", "text": VISION_PROMPT},
            ],
        }],
    )

    raw_text = response.content[0].text
    data = _parse_json_response(raw_text)
    data["_source"] = "claude_vision"
    return data


def extract_with_text(ocr_text: str) -> dict:
    """Send raw OCR text to Claude text API and return structured receipt data."""
    client = Anthropic(api_key=current_app.config["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a receipt data extraction assistant. Given raw OCR text from a receipt, return ONLY valid JSON. If a field is not found, use null. Never guess prices.",
        messages=[{
            "role": "user",
            "content": f"Receipt OCR text:\n\n{ocr_text}\n\n{STRUCTURE_PROMPT}",
        }],
    )

    raw_text = response.content[0].text
    data = _parse_json_response(raw_text)
    data["_source"] = "paddle_ocr+claude_text"
    return data
