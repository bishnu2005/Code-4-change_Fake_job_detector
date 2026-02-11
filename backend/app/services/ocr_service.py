"""
OCR service: extract text from uploaded images using Tesseract.
"""
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import io
import logging

logger = logging.getLogger(__name__)

# Lazy imports for optional dependencies
_tesseract_available = None


def _check_tesseract():
    """Check if pytesseract and PIL are available."""
    global _tesseract_available
    if _tesseract_available is not None:
        return _tesseract_available
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        _tesseract_available = True
    except ImportError:
        _tesseract_available = False
        logger.warning("pytesseract or Pillow not installed. OCR will be unavailable.")
    return _tesseract_available


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from an image using Tesseract OCR.
    Returns extracted text string, or raises RuntimeError if OCR is unavailable.
    """
    if not _check_tesseract():
        raise RuntimeError(
            "OCR is not available. Install pytesseract and Pillow, "
            "and ensure Tesseract binary is on your system PATH."
        )

    import pytesseract
    from PIL import Image

    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise RuntimeError(f"OCR extraction failed: {e}")
