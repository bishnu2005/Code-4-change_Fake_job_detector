"""
OCR Risk Module: extract text from images, assess signal strength,
and reuse calibrated ML for scoring.

Signal strength:
  0.0 → no text extracted (absent signal)
  0.5 → weak extraction (text < OCR_MIN_TEXT_LENGTH)
  1.0 → strong extraction
"""
import io
import logging

from app.config import OCR_MIN_TEXT_LENGTH

logger = logging.getLogger(__name__)

_tesseract_available = None


def _check_tesseract():
    global _tesseract_available
    if _tesseract_available is not None:
        return _tesseract_available
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        _tesseract_available = True
    except ImportError:
        _tesseract_available = False
        logger.warning("pytesseract or Pillow not installed. OCR unavailable.")
    return _tesseract_available


def analyze_ocr_risk(image_bytes: bytes) -> dict:
    """
    Extract text from image and assess OCR signal quality.

    Returns:
        {
            "ocr_risk_score": float (0-100),
            "extracted_text": str,
            "ocr_text_length": int,
            "ocr_signal_strength": float (0.0 | 0.5 | 1.0),
        }
    """
    result = {
        "ocr_risk_score": 0.0,
        "extracted_text": "",
        "ocr_text_length": 0,
        "ocr_signal_strength": 0.0,
    }

    if not _check_tesseract():
        raise RuntimeError(
            "OCR is not available. Install pytesseract and Pillow, "
            "and ensure Tesseract binary is on your system PATH."
        )

    import pytesseract
    from PIL import Image

    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image).strip()
        result["extracted_text"] = text
        result["ocr_text_length"] = len(text)

        # Determine signal strength (discrete levels)
        if not text or len(text) == 0:
            result["ocr_signal_strength"] = 0.0  # absent
        elif len(text) < OCR_MIN_TEXT_LENGTH:
            result["ocr_signal_strength"] = 0.5  # weak
        else:
            result["ocr_signal_strength"] = 1.0  # strong

        # Get ML risk score if we have text
        if text.strip() and result["ocr_signal_strength"] > 0:
            try:
                from app.services.text_risk import analyze_text_risk
                text_result = analyze_text_risk(text)
                result["ocr_risk_score"] = text_result.get("text_risk_score", 0.0)
            except Exception as e:
                logger.warning(f"OCR ML scoring failed: {e}")

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise RuntimeError(f"OCR extraction failed: {e}")

    return result
