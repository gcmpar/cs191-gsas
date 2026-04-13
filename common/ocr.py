"""
OCR utilities for scanning student Transcript of Records (TOR) PDFs.
Ported from __old/ocr_pdf.py.
"""

import re
import logging
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
import pytesseract

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _fix_grade(grade: str) -> str:
    """Fix grades that were extracted incorrectly by OCR."""
    grade = grade.replace(",", ".")  # Convert comma to dot for decimal consistency
    if re.fullmatch(r"\d{3}", grade):   # e.g. "175" → "1.75"
        return f"{grade[0]}.{grade[1:]}"
    elif re.fullmatch(r"\d{2}", grade): # e.g. "15" → "1.5"
        return f"{grade[0]}.{grade[1]}"
    return grade


_COURSE_PATTERN = re.compile(
    r"([A-Za-z]+(?:\s[A-Za-z]+)?\s*\d+(?:\.\d+)?)\s+"          # Course Code (e.g. "Eng 10", "Fil 40")
    r"((?:\b(?:[A-Za-z&\-,]{2,}|\b[A-Za-z]\b)\s*)+?)\s+"       # Description (multiple words)
    r"(\d+(?:[.,]\d{1,2})?|Inc|[A-F][+-]?)?\s*[|]?\s*"         # Grade (numerical first, e.g. "2.25", "A")
    r"(\d+|\(\d+\))?"                                            # Units (whole number or in parens)
)


def _is_probable_course_line(line: str) -> bool:
    line = line.strip()
    ends_with_unit = re.search(r"(\d+|\(\d+\))?", line)
    if not ends_with_unit:
        return False
    starts_with_course_like = re.match(
        r"([A-Za-z]+(?:\s[A-Za-z]+)?\s*\d+(?:\.\d+)?)\s+", line
    )
    return bool(starts_with_course_like)


def _preprocess_raw_text(raw_text: str) -> list[str]:
    """Clean raw OCR text and return only probable course lines."""
    cleaned_lines = []
    for line in raw_text.splitlines():
        line = re.sub(r'[|/\\@#*~]', '', line)           # strip symbols that sneak in
        line = re.sub(r"[^A-Za-z0-9\s.,()-]", " ", line) # keep alphanum + common punct
        line = re.sub(r'\bll\b', '11', line)              # fix 'll' → '11'
        line = re.sub(r'\bl\b', '1', line)                # fix 'l' → '1'
        line = re.sub(r"\s+", " ", line).strip()          # normalise spacing
        if _is_probable_course_line(line):
            cleaned_lines.append(line)
    return cleaned_lines


def _extract_structured_data(text: str, seen_keys: set) -> list[dict]:
    """Parse preprocessed OCR text into a list of course dicts."""
    structured_data = []
    for line in text.splitlines():
        line = line.strip()
        match = _COURSE_PATTERN.match(line)
        if match:
            course_code  = match.group(1).strip()
            description  = match.group(2).strip()
            grade        = _fix_grade(match.group(3).strip()) if match.group(3) else "N/A"
            units        = match.group(4).strip() if match.group(4) else "Unknown"

            key = (course_code.upper(), description.lower().strip())
            if key not in seen_keys:
                structured_data.append({
                    "course_code":  course_code,
                    "description":  description,
                    "grade":         grade,
                    "units":         units,
                })
                seen_keys.add(key)
            else:
                logger.debug("Duplicate course skipped: %s", key)
    return structured_data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_courses_from_pdf(pdf_path: str) -> list[dict]:
    """
    Run OCR on a TOR PDF and return a flat list of extracted course dicts.

    Each dict has keys: course_code, description, grade, units.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        List of course dicts (may be empty if nothing could be parsed).
    """
    seen_keys: set = set()
    all_courses: list[dict] = []

    try:
        pages = convert_from_path(pdf_path, dpi=300)
    except Exception as exc:
        logger.error("pdf2image failed to convert '%s': %s", pdf_path, exc)
        return []

    for page_number, page_image in enumerate(pages, start=1):
        try:
            # Image preprocessing for better OCR accuracy
            processed = page_image.convert('L')                   # grayscale
            processed = processed.filter(ImageFilter.MedianFilter())
            enhancer  = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(2)

            custom_config = r'--oem 3 --psm 6'  # LSTM-based, block-of-text mode
            raw_text      = pytesseract.image_to_string(processed, config=custom_config)
            clean_lines   = _preprocess_raw_text(raw_text)
            processed_text = "\n".join(clean_lines)

            page_courses = _extract_structured_data(processed_text, seen_keys)
            all_courses.extend(page_courses)

        except Exception as exc:
            logger.error("Error processing page %d of '%s': %s", page_number, pdf_path, exc)

    return all_courses
