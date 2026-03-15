import logging
from io import BytesIO

from flask import current_app
from PIL import Image

logger = logging.getLogger(__name__)

_paddle_ocr = None
_easy_ocr = None


def _get_paddle():
    global _paddle_ocr
    if _paddle_ocr is None:
        from paddleocr import PaddleOCR
        _paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    return _paddle_ocr


def _get_easy():
    global _easy_ocr
    if _easy_ocr is None:
        import easyocr
        _easy_ocr = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _easy_ocr


def _to_rgb_array(image_bytes: bytes):
    import numpy as np
    img = Image.open(BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    return np.array(img)


def extract_text(image_bytes: bytes) -> tuple[str, float]:
    """
    Try PaddleOCR first. If confidence < threshold or it fails,
    fall back to EasyOCR.
    Returns (raw_text, avg_confidence).
    """
    threshold = 0.70
    try:
        from flask import current_app
        threshold = current_app.config.get("OCR_CONFIDENCE_THRESHOLD", 0.70)
    except RuntimeError:
        pass

    # --- Primary: PaddleOCR ---
    try:
        import numpy as np
        ocr = _get_paddle()
        img_array = _to_rgb_array(image_bytes)
        result = ocr.ocr(img_array, cls=True)

        if result and result[0]:
            lines = []
            confidences = []
            for line in result[0]:
                text = line[1][0]
                conf = line[1][1]
                lines.append(text)
                confidences.append(conf)

            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            raw_text = "\n".join(lines)

            if avg_conf >= threshold:
                logger.info(f"PaddleOCR succeeded (confidence={avg_conf:.2f})")
                return raw_text, avg_conf

            logger.info(f"PaddleOCR confidence {avg_conf:.2f} < {threshold}, trying EasyOCR")
    except Exception as e:
        logger.warning(f"PaddleOCR failed: {e}, trying EasyOCR fallback")

    # --- Fallback: EasyOCR ---
    try:
        reader = _get_easy()
        img_array = _to_rgb_array(image_bytes)
        result = reader.readtext(img_array)

        if result:
            lines = []
            confidences = []
            for (_bbox, text, conf) in result:
                lines.append(text)
                confidences.append(conf)

            avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
            raw_text = "\n".join(lines)
            logger.info(f"EasyOCR succeeded (confidence={avg_conf:.2f})")
            return raw_text, avg_conf

    except Exception as e:
        logger.warning(f"EasyOCR also failed: {e}")

    return "", 0.0
