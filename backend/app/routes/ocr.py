import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from PIL import Image
from io import BytesIO

from app.services import ocr_service
from app.services.parser_service import extract_from_text

bp = Blueprint("ocr", __name__, url_prefix="/api/ocr")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "heic", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/extract", methods=["POST"])
def extract():
    """
    Accept a receipt image, run OCR (PaddleOCR → EasyOCR fallback),
    parse the text into structured data, and return it.
    Does NOT save to the database.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify({"error": "Empty file"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    image_bytes = file.read()

    # Save image to uploads folder
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    save_path = os.path.join(upload_folder, filename)

    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # Resize if too large
        max_height = 1600
        if img.height > max_height:
            ratio = max_height / img.height
            img = img.resize((int(img.width * ratio), max_height), Image.LANCZOS)
        img.save(save_path, format="JPEG", quality=85)
    except Exception as e:
        current_app.logger.warning(f"Image save failed: {e}")

    # Run OCR (PaddleOCR with EasyOCR fallback — all open source)
    raw_ocr_text, confidence = ocr_service.extract_text(image_bytes)

    if not raw_ocr_text:
        return jsonify({
            "error": "Could not read text from image",
            "image_filename": filename,
            "ocr_raw_text": "",
            "ocr_confidence": 0.0,
            "vendor_name": None,
            "date": None,
            "currency": "USD",
            "subtotal": None,
            "tax": None,
            "total": None,
            "line_items": [],
        }), 200  # 200 so frontend shows editable empty form

    # Parse OCR text into structured receipt data
    data = extract_from_text(raw_ocr_text)
    data["image_filename"] = filename
    data["ocr_raw_text"] = raw_ocr_text
    data["ocr_confidence"] = round(confidence, 3)

    return jsonify(data), 200
