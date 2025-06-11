from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _rec_name = 'license_plate'

    vin_number = fields.Char(string='VIN Number')
    engine_no = fields.Char(string="Engine Number")
    partner_id = fields.Many2one('res.partner',string="Customer")

    # def name_get(self):
    #     context = self._context
    #     result = []
    #
    #     for record in self:
    #         if context.get('show_license_plate_only'):
    #             name = record.license_plate or 'No Plate'
    #         else:
    #             name = super(FleetVehicle, record).name_get()[0][1]
    #         result.append((record.id, name))
    #     return result

    # def name_get(self):
    #     print('reeeeeeeeeeeeeeee')
    #     result = []
    #     for rec in self:
    #         if self.env.context.get('reg_no'):
    #             name = rec.license_plate or "Empty"
    #             result.append((rec.id, name))
    #         else:
    #             name = rec.model_id.name + " [" + (rec.license_plate if rec.license_plate else "-") + "]"
    #             result.append((rec.id, name))
    #     return result

    def name_get(self):
        result = []
        for rec in self:
            name = rec.license_plate or 'No Plate'
            result.append((rec.id, name))
        return result