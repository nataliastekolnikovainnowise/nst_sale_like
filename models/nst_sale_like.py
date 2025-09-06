# -*- coding: utf-8 -*-
from odoo import models, fields

class NSTOrder(models.Model):
    _name = "nst.order"
    _description = "NST Order (skeleton)"

    name = fields.Char(string="Name", required=True)

class NSTOrderLine(models.Model):
    _name = "nst.order.line"
    _description = "NST Order Line (skeleton)"

    name = fields.Char(string="Name")
