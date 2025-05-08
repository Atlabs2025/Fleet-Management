import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    menu_service = fields.Selection([
        ('regular', 'Regular'),
        ('medium', 'Medium'),
        ('major', 'Major'),
        ('loop_services', 'Loop Services'),
    ], string="Menu Services")

    service_amount = fields.Float(string="Service Amount")

    @api.onchange('menu_service')
    def _onchange_menu_service(self):
        for rec in self:
            if rec.menu_service == 'regular':
                rec.service_amount = 500
            elif rec.menu_service == 'medium':
                rec.service_amount = 1000
            elif rec.menu_service == 'major':
                rec.service_amount = 2000
            elif rec.menu_service == 'loop_services':
                rec.service_amount = 300
            else:
                rec.service_amount = 0.0