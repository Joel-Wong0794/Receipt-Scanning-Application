import logging
from app.models import Receipt

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from flask import current_app
        import gspread
        from google.oauth2.service_account import Credentials

        creds_file = current_app.config.get("GOOGLE_SHEETS_CREDENTIALS_FILE", "")
        if not creds_file:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS_FILE not configured")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
        _client = gspread.authorize(creds)
    return _client


def _get_sheet():
    from flask import current_app
    sheet_id = current_app.config.get("GOOGLE_SHEET_ID", "")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID not configured")
    gc = _get_client()
    spreadsheet = gc.open_by_key(sheet_id)
    try:
        worksheet = spreadsheet.worksheet("Expenses")
    except Exception:
        worksheet = spreadsheet.add_worksheet(title="Expenses", rows=1000, cols=10)
        worksheet.append_row([
            "Date", "Vendor", "Category", "Subtotal", "Tax",
            "Total", "Currency", "Notes", "Receipt ID", "External ID"
        ])
    return worksheet


def sync_receipt(receipt: Receipt) -> bool:
    """
    Append receipt as a new row to the configured Google Sheet.
    Returns True on success, False on failure (caller should not raise).
    """
    try:
        ws = _get_sheet()
        row = [
            receipt.date.isoformat() if receipt.date else "",
            receipt.vendor_name or "",
            receipt.category or "",
            str(receipt.subtotal) if receipt.subtotal is not None else "",
            str(receipt.tax) if receipt.tax is not None else "",
            str(receipt.total) if receipt.total is not None else "",
            receipt.currency or "USD",
            receipt.notes or "",
            receipt.id,
            receipt.external_id,
        ]
        ws.append_row(row)
        return True
    except Exception as e:
        logger.warning(f"Google Sheets sync failed for receipt {receipt.id}: {e}")
        return False
