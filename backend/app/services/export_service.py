import csv
import io
import json
from datetime import date

from app.models import Receipt


def _decimal_str(val) -> str:
    return str(val) if val is not None else ""


def receipts_to_csv(receipts: list[Receipt]) -> str:
    """Export list of receipts to standard CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "External ID", "Date", "Vendor", "Category",
                     "Subtotal", "Tax", "Total", "Currency", "Notes", "Created At"])
    for r in receipts:
        writer.writerow([
            r.id,
            r.external_id,
            r.date.isoformat() if r.date else "",
            r.vendor_name or "",
            r.category or "",
            _decimal_str(r.subtotal),
            _decimal_str(r.tax),
            _decimal_str(r.total),
            r.currency or "USD",
            r.notes or "",
            r.created_at.isoformat() if r.created_at else "",
        ])
    return output.getvalue()


def receipts_to_workday_csv(receipts: list[Receipt]) -> str:
    """Export receipts to Workday-compatible CSV with their expected field names."""
    output = io.StringIO()
    writer = csv.writer(output)
    # Workday expense import column names
    writer.writerow([
        "Transaction Date", "Supplier", "Expense Type", "Amount",
        "Currency", "Tax Amount", "Memo", "External Reference ID"
    ])
    for r in receipts:
        # Concatenate line item descriptions as memo
        memo = "; ".join(
            li.description for li in r.line_items if li.description
        ) if r.line_items else (r.notes or "")

        writer.writerow([
            r.date.isoformat() if r.date else "",
            r.vendor_name or "",
            r.category or "Other",
            _decimal_str(r.total),
            r.currency or "USD",
            _decimal_str(r.tax),
            memo,
            r.external_id,
        ])
    return output.getvalue()


def receipts_to_json(receipts: list[Receipt]) -> str:
    """Export receipts to JSON string."""
    def receipt_dict(r):
        return {
            "id": r.id,
            "external_id": r.external_id,
            "vendor_name": r.vendor_name,
            "date": r.date.isoformat() if r.date else None,
            "category": r.category,
            "subtotal": _decimal_str(r.subtotal) or None,
            "tax": _decimal_str(r.tax) or None,
            "total": _decimal_str(r.total) or None,
            "currency": r.currency,
            "notes": r.notes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": _decimal_str(li.quantity),
                    "unit_price": _decimal_str(li.unit_price) or None,
                    "total_price": _decimal_str(li.total_price) or None,
                }
                for li in r.line_items
            ],
        }

    return json.dumps([receipt_dict(r) for r in receipts], indent=2)
