from marshmallow import Schema, fields
from .line_item_schema import LineItemSchema


class ReceiptSchema(Schema):
    id = fields.Int(dump_only=True)
    external_id = fields.Str(dump_only=True)
    vendor_name = fields.Str(allow_none=True, load_default=None)
    date = fields.Date(allow_none=True, load_default=None)
    subtotal = fields.Decimal(as_string=True, allow_none=True, load_default=None)
    tax = fields.Decimal(as_string=True, allow_none=True, load_default=None)
    total = fields.Decimal(as_string=True, allow_none=True, load_default=None)
    currency = fields.Str(load_default="USD")
    category = fields.Str(allow_none=True, load_default=None)
    image_path = fields.Str(dump_only=True, allow_none=True)
    notes = fields.Str(allow_none=True, load_default=None)
    sheets_synced = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    line_items = fields.List(fields.Nested(LineItemSchema), load_default=[])
