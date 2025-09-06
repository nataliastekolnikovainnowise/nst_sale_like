from odoo import models, fields, api

class NstOrder(models.Model):
    _name = "nst.order"
    _description = "NST Order"

    name = fields.Char(string="Order Reference")

    customer_id = fields.Many2one(
        'res.partner',
        string="Customer",
        required=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft')

    order_line_ids = fields.One2many(
        'nst.order.line',
        'order_id',
        string="Order Lines"
    )

    amount_total = fields.Float(
        string="Total Amount",
        compute="_compute_amount_total",
        store=True
    )

    @api.depends('order_line_ids.subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(line.subtotal for line in order.order_line_ids)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'


class NstOrderLine(models.Model):
    _name = "nst.order.line"
    _description = "NST Order Line"

    order_id = fields.Many2one(
        'nst.order',
        string="Order",
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )

    price_unit = fields.Float(string="Unit Price")

    quantity = fields.Float(string="Quantity", default=1.0)

    discount = fields.Float(string="Discount (%)", default=0.0)

    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True
    )

    @api.depends('price_unit', 'quantity', 'discount')
    def _compute_subtotal(self):
        for line in self:
            price = line.price_unit * line.quantity
            discount_amount = price * (line.discount / 100.0)
            line.subtotal = price - discount_amount
