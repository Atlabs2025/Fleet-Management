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

    part_no = fields.Char(string="Part.No")

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

    @api.onchange('part_no')
    def _onchange_part_no(self):
        if self.part_no != self.default_code:
            self.default_code = self.part_no



    @api.onchange('default_code')
    def _onchange_default_code(self):
        if self.default_code != self.part_no:
            self.part_no = self.default_code