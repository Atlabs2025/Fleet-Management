from odoo import models, fields




class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    vin_number = fields.Char(string='VIN Number')
    engine_no = fields.Char(string="Engine Number")
