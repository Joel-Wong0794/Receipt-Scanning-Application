from marshmallow import Schema, fields


class LineItemSchema(Schema):
    id = fields.Int(dump_only=True)
    receipt_id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    quantity = fields.Decimal(as_string=True, load_default="1")
    unit_price = fields.Decimal(as_string=True, allow_none=True, load_default=None)
    total_price = fields.Decimal(as_string=True, allow_none=True, load_default=None)
    sort_order = fields.Int(load_default=0)
