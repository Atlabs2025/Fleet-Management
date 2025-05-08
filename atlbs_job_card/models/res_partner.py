from odoo import models, fields, api
import re



class ResPartner(models.Model):
    _inherit = 'res.partner'

    job_card_vehicle_ids = fields.One2many('job.card.management', 'partner_id', string="Vehicles")
    whatsapp_no = fields.Char(string="Whatsapp Number")
    customer_type = fields.Selection([
        ('retail_customer', 'Retail Customer'),
        ('fleet_customer', 'Fleet Customer'),
    ], string="Customer Type", default='', tracking=True)

    customer_code = fields.Char(string="Customer Code", copy=False, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('customer_type') and not vals.get('customer_code'):
            prefix = 'RT' if vals['customer_type'] == 'retail_customer' else 'FL'
            last_partner = self.search(
                [('customer_type', '=', vals['customer_type']), ('customer_code', 'like', prefix)],
                order='customer_code desc', limit=1
            )

            if last_partner and last_partner.customer_code:
                # Extract the numeric part using regex
                match = re.search(r'\d+', last_partner.customer_code)
                if match:
                    number = int(match.group(0)) + 1
                else:
                    number = 1
            else:
                number = 1

            vals['customer_code'] = f"{prefix}{str(number).zfill(3)}"

        return super(ResPartner, self).create(vals)

