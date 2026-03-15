"""
Open-source receipt parser.
Extracts structured data from raw OCR text using regex and heuristics.
No external API calls — runs entirely locally.
"""

import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Prices: optional $ then digits with 2 decimal places
PRICE_RE = re.compile(r"\$?\s*(\d{1,6}[.,]\d{2})\b")

# Date formats commonly found on receipts
DATE_PATTERNS = [
    (re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b"), "mdy"),   # 03/15/2026
    (re.compile(r"\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b"), "ymd"),      # 2026-03-15
    (re.compile(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+"
        r"(\d{1,2})[,\s]+(\d{4})\b", re.IGNORECASE
    ), "mname"),  # March 15, 2026
]

MONTH_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# Keywords that signal total / tax / subtotal lines
TOTAL_KW    = re.compile(r"\b(total|amount due|balance due|grand total)\b", re.IGNORECASE)
TAX_KW      = re.compile(r"\b(tax|gst|hst|vat|sales tax)\b", re.IGNORECASE)
SUBTOTAL_KW = re.compile(r"\b(subtotal|sub-total|sub total)\b", re.IGNORECASE)

# Lines that are clearly NOT item descriptions (skip them)
SKIP_LINE_RE = re.compile(
    r"\b(total|subtotal|tax|change|cash|credit|debit|visa|mastercard|"
    r"thank you|welcome|receipt|invoice|order|cashier|server|table|"
    r"approved|authorization|auth|terminal|ref\b|trans\b|"
    r"phone|address|www\.|http)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_price(text: str) -> float | None:
    """Extract the rightmost price from a line of text."""
    matches = PRICE_RE.findall(text)
    if not matches:
        return None
    raw = matches[-1].replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _parse_date(text: str) -> str | None:
    """Return ISO date string (YYYY-MM-DD) or None."""
    for pattern, fmt in DATE_PATTERNS:
        m = pattern.search(text)
        if not m:
            continue
        try:
            if fmt == "mdy":
                month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
                if year < 100:
                    year += 2000
            elif fmt == "ymd":
                year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
            elif fmt == "mname":
                month = MONTH_ABBR[m.group(1)[:3].lower()]
                day = int(m.group(2))
                year = int(m.group(3))
            else:
                continue
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except (ValueError, KeyError):
            continue
    return None


def _looks_like_item_line(line: str) -> bool:
    """Return True if the line plausibly represents a purchased item."""
    if len(line.strip()) < 3:
        return False
    if SKIP_LINE_RE.search(line):
        return False
    if PRICE_RE.search(line):
        return True
    # Lines with only digits/prices and no description text are not items
    if re.match(r"^\s*[\d.,\s$]+\s*$", line):
        return False
    return False


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_from_text(ocr_text: str) -> dict:
    """
    Parse raw OCR text into a structured receipt dict.

    Returns a dict matching the schema expected by the frontend:
    {
        vendor_name, date, currency, subtotal, tax, total,
        line_items: [{description, quantity, unit_price, total_price}]
    }
    """
    lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]

    vendor_name = None
    date_str = None
    subtotal = None
    tax = None
    total = None
    line_items = []

    # --- Pass 1: scan every line for totals, date, and items ---
    for line in lines:
        # Date
        if date_str is None:
            d = _parse_date(line)
            if d:
                date_str = d

        price = _parse_price(line)
        if price is None:
            continue

        if TOTAL_KW.search(line) and not TAX_KW.search(line):
            # Keep the LARGEST "total" value found (avoid partial-total lines)
            if total is None or price > total:
                total = price

        elif TAX_KW.search(line):
            tax = price

        elif SUBTOTAL_KW.search(line):
            subtotal = price

        elif _looks_like_item_line(line):
            # Strip the price from the end to get description
            desc = PRICE_RE.sub("", line).strip(" -|:").strip()
            if desc:
                line_items.append({
                    "description": desc,
                    "quantity": 1,
                    "unit_price": None,
                    "total_price": price,
                })

    # --- Pass 2: vendor name heuristic ---
    # The vendor is usually in the first 1-4 non-empty lines that have no price
    # and aren't obviously a date/address.
    ADDRESS_RE = re.compile(r"\d{3,}|\bst\b|\bave\b|\brd\b|\bblvd\b|\bdr\b", re.IGNORECASE)
    for line in lines[:6]:
        if PRICE_RE.search(line):
            continue
        if _parse_date(line):
            continue
        if ADDRESS_RE.search(line):
            continue
        if len(line) >= 3:
            vendor_name = line
            break

    # --- Derive subtotal if missing ---
    if subtotal is None and line_items:
        calc = sum(it["total_price"] or 0 for it in line_items)
        if calc > 0:
            subtotal = round(calc, 2)

    # --- Sanity: if total is None but subtotal+tax exist, derive it ---
    if total is None and subtotal is not None:
        total = round((subtotal or 0) + (tax or 0), 2)

    return {
        "vendor_name": vendor_name,
        "date": date_str,
        "currency": "USD",
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "line_items": line_items,
        "_source": "paddle_ocr+easyocr+regex_parser",
    }
