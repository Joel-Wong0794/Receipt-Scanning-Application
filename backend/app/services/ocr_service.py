import logging
from io import BytesIO

from flask import current_app
from PIL import Image

logger = logging.getLogger(__name__)

# Lazy-load PaddleOCR to avoid slow startup if not needed
_paddle_ocr = None


def _get_ocr():
    global _paddle_ocr
    if _paddle_ocr is None:
        from paddleocr import PaddleOCR
        _paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _paddle_ocr


def extract_text(image_bytes: bytes) -> tuple[str, float]:
    """
    Run PaddleOCR on image bytes.
    Returns (raw_text, avg_confidence).
    If PaddleOCR is unavailable, returns ("", 0.0) to trigger Vision fallback.
    """
    try:
        ocr = _get_ocr()
        import numpy as np

        img = Image.open(BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img_array = np.array(img)

        result = ocr.ocr(img_array, cls=True)

        if not result or not result[0]:
            return "", 0.0

        lines = []
        confidences = []
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            lines.append(text)
            confidences.append(confidence)

        raw_text = "\n".join(lines)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return raw_text, avg_confidence

    except Exception as e:
        logger.warning(f"PaddleOCR failed: {e}. Will fall back to Claude Vision.")
        return "", 0.0
