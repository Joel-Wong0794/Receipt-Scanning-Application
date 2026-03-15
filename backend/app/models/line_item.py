from app.extensions import db


class LineItem(db.Model):
    __tablename__ = "line_items"

    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey("receipts.id"), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    quantity = db.Column(db.Numeric(10, 3), default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=True)
    total_price = db.Column(db.Numeric(10, 2), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<LineItem {self.description} {self.total_price}>"
