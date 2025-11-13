from odoo import models, fields

class ServiceDescription(models.Model):
    _name = 'service.description'
    _description = 'Service Description'


    name = fields.Char(string="Service Name")
    parts_id = fields.Many2one(
        'product.template',string='Parts')
    labour_charge = fields.Float(string='Labour Charge')
    material = fields.Char(string='Material')
