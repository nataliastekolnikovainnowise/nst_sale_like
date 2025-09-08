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
        string="Status",
        default="draft",
    )
    order_line_ids = fields.One2many(
        "nst.order.line",
        "order_id",
        string="Order Lines",
    )
    
    # === Summary fields ===
    amount_total = fields.Float(
        string="Total Amount",
        compute="_compute_summary",
        store=True,
    )
    amount_avg = fields.Float(
        string="Average Amount",
        compute="_compute_summary",
        store=True,
    )
    amount_max = fields.Float(
        string="Max Amount",
        compute="_compute_summary",
        store=True,
    )
    discount_percent = fields.Float(
        string="Discount %",
        default=0.0,
        help="Manual discount percentage for the entire order"
    )
    
    @api.depends("order_line_ids.subtotal", "discount_percent")
    def _compute_summary(self):
        for order in self:
            subtotals = order.order_line_ids.mapped("subtotal")
            if subtotals:
                # Сумма строк без общей скидки
                subtotal_sum = sum(subtotals)
                
                # Применяем общую скидку к итоговой сумме
                if order.discount_percent:
                    order.amount_total = subtotal_sum * (1 - order.discount_percent / 100.0)
                else:
                    order.amount_total = subtotal_sum
                    
                order.amount_avg = subtotal_sum / len(subtotals)
                order.amount_max = max(subtotals)
            else:
                order.amount_total = 0.0
                order.amount_avg = 0.0
                order.amount_max = 0.0
    
    # === State actions ===
    def action_confirm(self):
        for order in self:
            order.state = "confirmed"
    
    def action_set_draft(self):
        for order in self:
            order.state = "draft"


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
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
        default=0.0,
    )
    discount = fields.Float(
        string="Discount (%)",
        default=0.0,
        help="Discount percentage for this line"
    )
    subtotal = fields.Float(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        readonly=True,
    )
    
    @api.depends("quantity", "price_unit", "discount")
    def _compute_subtotal(self):
        for line in self:
            # Subtotal = quantity * price_unit * (1 - discount/100)
            # Discount всегда считается от исходного значения
            price = line.quantity * line.price_unit
            if line.discount:
                price = price * (1 - line.discount / 100.0)
            line.subtotal = price
