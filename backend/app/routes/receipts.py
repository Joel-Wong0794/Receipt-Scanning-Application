import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify, send_file, current_app
from marshmallow import ValidationError

from app.extensions import db
from app.models import Receipt, LineItem
from app.schemas import ReceiptSchema
from app.services import export_service, google_sheets_service

bp = Blueprint("receipts", __name__, url_prefix="/api/receipts")

receipt_schema = ReceiptSchema()
receipts_schema = ReceiptSchema(many=True)


def _apply_line_items(receipt: Receipt, items_data: list):
    """Replace all line items on a receipt."""
    for li in list(receipt.line_items):
        db.session.delete(li)
    for i, item in enumerate(items_data):
        li = LineItem(
            receipt_id=receipt.id,
            description=item.get("description", ""),
            quantity=item.get("quantity", 1),
            unit_price=item.get("unit_price"),
            total_price=item.get("total_price"),
            sort_order=i,
        )
        db.session.add(li)


@bp.route("", methods=["POST"])
def create_receipt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    line_items_data = data.pop("line_items", [])

    receipt = Receipt(
        vendor_name=data.get("vendor_name"),
        date=datetime.strptime(data["date"], "%Y-%m-%d").date() if data.get("date") else None,
        subtotal=data.get("subtotal"),
        tax=data.get("tax"),
        total=data.get("total"),
        currency=data.get("currency", "USD"),
        category=data.get("category"),
        image_path=data.get("image_filename"),
        raw_text=data.get("raw_text"),
        ocr_raw_text=data.get("ocr_raw_text"),
        notes=data.get("notes"),
    )
    db.session.add(receipt)
    db.session.flush()  # get receipt.id before adding line items

    for i, item in enumerate(line_items_data):
        li = LineItem(
            receipt_id=receipt.id,
            description=item.get("description", ""),
            quantity=item.get("quantity", 1),
            unit_price=item.get("unit_price"),
            total_price=item.get("total_price"),
            sort_order=i,
        )
        db.session.add(li)

    db.session.commit()

    # Sync to Google Sheets (best-effort)
    synced = False
    try:
        if current_app.config.get("GOOGLE_SHEET_ID"):
            synced = google_sheets_service.sync_receipt(receipt)
            if synced:
                receipt.sheets_synced = True
                db.session.commit()
    except Exception as e:
        current_app.logger.warning(f"Sheets sync error: {e}")

    return jsonify(receipt_schema.dump(receipt)), 201


@bp.route("", methods=["GET"])
def list_receipts():
    query = Receipt.query.order_by(Receipt.created_at.desc())

    vendor = request.args.get("vendor")
    if vendor:
        query = query.filter(Receipt.vendor_name.ilike(f"%{vendor}%"))

    category = request.args.get("category")
    if category:
        query = query.filter(Receipt.category == category)

    date_from = request.args.get("date_from")
    if date_from:
        query = query.filter(Receipt.date >= date_from)

    date_to = request.args.get("date_to")
    if date_to:
        query = query.filter(Receipt.date <= date_to)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "receipts": receipts_schema.dump(paginated.items),
        "total": paginated.total,
        "page": page,
        "per_page": per_page,
        "pages": paginated.pages,
    }), 200


@bp.route("/export", methods=["GET"])
def export_receipts():
    fmt = request.args.get("format", "csv")
    receipts = Receipt.query.order_by(Receipt.date.desc()).all()

    if fmt == "workday_csv":
        content = export_service.receipts_to_workday_csv(receipts)
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="receipts_workday.csv",
        )
    elif fmt == "json":
        content = export_service.receipts_to_json(receipts)
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="application/json",
            as_attachment=True,
            download_name="receipts.json",
        )
    else:  # default csv
        content = export_service.receipts_to_csv(receipts)
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name="receipts.csv",
        )


@bp.route("/<int:receipt_id>", methods=["GET"])
def get_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    return jsonify(receipt_schema.dump(receipt)), 200


@bp.route("/<int:receipt_id>", methods=["PUT"])
def update_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    line_items_data = data.pop("line_items", None)

    if "vendor_name" in data:
        receipt.vendor_name = data["vendor_name"]
    if "date" in data:
        receipt.date = datetime.strptime(data["date"], "%Y-%m-%d").date() if data["date"] else None
    if "subtotal" in data:
        receipt.subtotal = data["subtotal"]
    if "tax" in data:
        receipt.tax = data["tax"]
    if "total" in data:
        receipt.total = data["total"]
    if "currency" in data:
        receipt.currency = data["currency"]
    if "category" in data:
        receipt.category = data["category"]
    if "notes" in data:
        receipt.notes = data["notes"]

    if line_items_data is not None:
        _apply_line_items(receipt, line_items_data)

    db.session.commit()
    return jsonify(receipt_schema.dump(receipt)), 200


@bp.route("/<int:receipt_id>", methods=["DELETE"])
def delete_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    db.session.delete(receipt)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@bp.route("/<int:receipt_id>/export", methods=["GET"])
def export_single_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    fmt = request.args.get("format", "csv")

    if fmt == "workday_csv":
        content = export_service.receipts_to_workday_csv([receipt])
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"receipt_{receipt_id}_workday.csv",
        )
    elif fmt == "json":
        content = export_service.receipts_to_json([receipt])
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="application/json",
            as_attachment=True,
            download_name=f"receipt_{receipt_id}.json",
        )
    else:
        content = export_service.receipts_to_csv([receipt])
        return send_file(
            io.BytesIO(content.encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"receipt_{receipt_id}.csv",
        )


@bp.route("/<int:receipt_id>/sync-sheets", methods=["POST"])
def sync_sheets(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    synced = google_sheets_service.sync_receipt(receipt)
    if synced:
        receipt.sheets_synced = True
        db.session.commit()
        return jsonify({"message": "Synced to Google Sheets"}), 200
    return jsonify({"error": "Google Sheets sync failed"}), 500
