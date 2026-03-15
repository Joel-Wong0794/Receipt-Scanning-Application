import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.services import ocr_service, claude_service

bp = Blueprint("ocr", __name__, url_prefix="/api/ocr")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "heic", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/extract", methods=["POST"])
def extract():
    """
    Accept a receipt image, run OCR + Claude structuring, return extracted data.
    Does NOT save to the database — caller reviews then POSTs to /api/receipts.
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify({"error": "Empty file"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    image_bytes = file.read()

    # Save upload
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    filename = f"{uuid.uuid4()}.jpg"
    save_path = os.path.join(upload_folder, filename)

    # Step 1: Try PaddleOCR
    raw_ocr_text, confidence = ocr_service.extract_text(image_bytes)
    threshold = current_app.config["OCR_CONFIDENCE_THRESHOLD"]

    try:
        if raw_ocr_text and confidence >= threshold:
            # Step 2a: OCR succeeded — structure with Claude text API
            data = claude_service.extract_with_text(raw_ocr_text)
        else:
            # Step 2b: Low confidence or OCR failed — fall back to Claude Vision
            current_app.logger.info(
                f"OCR confidence {confidence:.2f} < {threshold}, using Claude Vision"
            )
            data = claude_service.extract_with_vision(image_bytes)

        # Persist image file
        with open(save_path, "wb") as f:
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(image_bytes))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(save_path, format="JPEG", quality=85)

        data["image_filename"] = filename
        data["ocr_raw_text"] = raw_ocr_text
        data["ocr_confidence"] = round(confidence, 3)
        return jsonify(data), 200

    except Exception as e:
        current_app.logger.error(f"Extraction failed: {e}")
        return jsonify({
            "error": "Extraction failed",
            "detail": str(e),
            "image_filename": filename,
            "ocr_raw_text": raw_ocr_text,
            "ocr_confidence": round(confidence, 3),
            # Return empty skeleton so frontend can still show editable form
            "vendor_name": None,
            "date": None,
            "currency": "USD",
            "subtotal": None,
            "tax": None,
            "total": None,
            "line_items": [],
        }), 200  # 200 so frontend doesn't error out — partial result
