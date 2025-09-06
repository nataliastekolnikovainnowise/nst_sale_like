from odoo import models, fields, api


class NstOrder(models.Model):
    _name = "nst.order"
    _description = "NST Order"

    name = fields.Char(string="Order Reference")

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
    )

    order_line_ids = fields.One2many(
        "nst.order.line",
        "order_id",
        string="Order Lines",
    )

    amount_total = fields.Monetary(
        string="Total Amount",
        compute="_compute_amount_total",
        store=True,
        readonly=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # === Логика переключения статусов ===
    def action_confirm(self):
        for order in self:
            order.state = "confirmed"

    def action_set_to_draft(self):
        for order in self:
            order.state = "draft"

    # === Подсчёт общей суммы ===
    @api.depends("order_line_ids.subtotal")
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.order_line_ids.mapped("subtotal"))


class NstOrderLine(models.Model):
    _name = "nst.order.line"
    _description = "NST Order Line"

    order_id = fields.Many2one(
        "nst.order",
        string="Order",
        ondelete="cascade",
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
    )

    quantity = fields.Float(
        string="Quantity",
        default=1.0,
    )

    price_unit = fields.Monetary(
        string="Unit Price",
        required=True,
        default=0.0,
        currency_field="currency_id",
    )

    subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        readonly=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        related="order_id.currency_id",
        store=True,
        readonly=True,
    )

    # === Подсчёт суммы строки ===
    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
