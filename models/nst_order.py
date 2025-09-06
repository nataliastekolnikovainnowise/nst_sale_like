from odoo import api, fields, models


class NstOrder(models.Model):
    _name = "nst.order"
    _description = "NST Order"

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        default="New"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
        string="Status",
        default="draft",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    order_line_ids = fields.One2many(
        "nst.order.line",
        "order_id",
        string="Order Lines",
    )


class NstOrderLine(models.Model):
    _name = "nst.order.line"
    _description = "NST Order Line"

    order_id = fields.Many2one(
        "nst.order",
        string="Order",
        required=True,
        ondelete="cascade",
    )
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Monetary(string="Unit Price", required=True, default=0.0)
    extra_cost = fields.Monetary(string="Extra Cost", default=0.0)

    base_subtotal = fields.Monetary(
        string="Base Subtotal",
        compute="_compute_base_subtotal",
        store=True,
        readonly=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="order_id.currency_id",
        store=True,
        readonly=True,
    )

    @api.depends("quantity", "price_unit", "extra_cost")
    def _compute_base_subtotal(self):
        """Compute base subtotal = quantity * unit price + extra cost."""
        for line in self:
            line.base_subtotal = (line.quantity * line.price_unit) + line.extra_cost
