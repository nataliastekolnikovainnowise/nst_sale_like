from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
        help="Manual discount percentage for the entire order (0-100)"
    )
    
    @api.depends("order_line_ids.quantity", "order_line_ids.price_unit", "order_line_ids.discount", "discount_percent")
    def _compute_summary(self):
        for order in self:
            subtotals = order.order_line_ids.mapped("subtotal")
            if subtotals:
                # Сумма строк без общей скидки
                subtotal_sum = sum(subtotals)
                
                # Применяем общую скидку к итоговой сумме
                if order.discount_percent:
                    final_total = subtotal_sum * (1 - order.discount_percent / 100.0)
                    final_avg = (subtotal_sum / len(subtotals)) * (1 - order.discount_percent / 100.0)
                    final_max = max(subtotals) * (1 - order.discount_percent / 100.0)
                else:
                    final_total = subtotal_sum
                    final_avg = subtotal_sum / len(subtotals)
                    final_max = max(subtotals)
                
                order.amount_total = final_total
                order.amount_avg = final_avg
                order.amount_max = final_max
            else:
                order.amount_total = 0.0
                order.amount_avg = 0.0
                order.amount_max = 0.0
    
    @api.constrains("discount_percent")
    def _check_discount_percent(self):
        for record in self:
            if record.discount_percent < 0:
                raise ValidationError("Discount percentage cannot be negative.")
            if record.discount_percent > 100:
                raise ValidationError("Discount percentage cannot exceed 100%.")
    
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
        help="Discount percentage for this line (0-100)"
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
            # Базовая сумма без скидки
            base_amount = line.quantity * line.price_unit
            
            # Применяем скидку строки (всегда от исходного значения)
            if line.discount and 0 <= line.discount <= 100:
                discount_amount = base_amount * (line.discount / 100.0)
                line.subtotal = base_amount - discount_amount
            else:
                line.subtotal = base_amount
    
    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError("Quantity cannot be negative.")
    
    @api.constrains("price_unit")
    def _check_price_unit(self):
        for record in self:
            if record.price_unit < 0:
                raise ValidationError("Unit price cannot be negative.")
    
    @api.constrains("discount")
    def _check_discount(self):
        for record in self:
            if record.discount < 0:
                raise ValidationError("Discount percentage cannot be negative.")
            if record.discount > 100:
                raise ValidationError("Discount percentage cannot exceed 100%.")
