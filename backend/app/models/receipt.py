import uuid
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class Receipt(db.Model):
    __tablename__ = "receipts"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(36), unique=True, nullable=False,
                            default=lambda: str(uuid.uuid4()))
    vendor_name = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=True)
    tax = db.Column(db.Numeric(10, 2), nullable=True)
    total = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), default="USD")
    category = db.Column(db.String(100), nullable=True)  # Expense type for Workday
    image_path = db.Column(db.String(512), nullable=True)
    raw_text = db.Column(db.Text, nullable=True)       # Claude structured response
    ocr_raw_text = db.Column(db.Text, nullable=True)   # PaddleOCR raw output
    notes = db.Column(db.Text, nullable=True)
    sheets_synced = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    line_items = db.relationship("LineItem", backref="receipt",
                                 cascade="all, delete-orphan", lazy=True,
                                 order_by="LineItem.sort_order")

    def __repr__(self):
        return f"<Receipt {self.id} {self.vendor_name} {self.total}>"
