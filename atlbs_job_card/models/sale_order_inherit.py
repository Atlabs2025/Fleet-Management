from odoo import models, fields, api



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    job_card_id = fields.Many2one("job.card.management", string="Job Card")

    def action_add_vehicle_products(self):
        return {
            'name': 'Add Vehicle Products',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.vehicle.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id},
        }

    def _create_invoices(self, **kwargs):
        invoices = super()._create_invoices(**kwargs)
        for order in self:
            if order.job_card_id:
                invoices.filtered(lambda inv: inv.invoice_origin == order.name).write({
                    "job_card_id": order.job_card_id.id
                })
        return invoices


# function commented on aug26
    # def action_create_job_card(self):
    #     self.ensure_one()
    #     job_card = self.env['job.card.management'].create({
    #         'sale_order_id': self.id,
    #         'partner_id': self.partner_id.id,
    #         'email': self.partner_id.email,
    #         'phone': self.partner_id.phone,
    #         'whatsapp_no': self.partner_id.whatsapp_no,
    #         'state': 'memo',
    #         # 'register_no': vehicle_make_id,
    #
    #     })
    #     job_card_line_obj = self.env['job.card.line']
    #     for line in self.order_line:
    #         job_card_line_obj.create({
    #             'job_card_id': job_card.id,
    #             'department': line.department,
    #             'product_template_id': line.product_template_id.id if hasattr(line, 'product_template_id') else False,
    #             'description': line.name,
    #             'price_unit': line.price_unit,
    #             'quantity': line.product_uom_qty,
    #             'tax_ids': [(6, 0, line.tax_id.ids)] if hasattr(line, 'tax_id') else False,
    #             'discount': line.discount,
    #             'after_discount': line.price_unit * (1 - (line.discount or 0.0) / 100),
    #             # compute tax_amount if you want here
    #             'uom': line.product_uom.id if hasattr(line, 'product_uom') else False,
    #         })
    #     return {
    #         'name': 'Job Card',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'job.card.management',
    #         'view_mode': 'form',
    #         'res_id': job_card.id,
    #         'target': 'current',
    #     }

    def action_create_job_card(self):
        self.ensure_one()
        job_card = self.env['job.card.management'].create({
            'sale_order_id': self.id,
            'partner_id': self.partner_id.id,
            'email': self.partner_id.email,
            'phone': self.partner_id.phone,
            'whatsapp_no': self.partner_id.whatsapp_no,
            'state': 'memo',
        })
        # link back to sale order
        self.job_card_id = job_card.id

        job_card_line_obj = self.env['job.card.line']
        for line in self.order_line:
            job_card_line_obj.create({
                'job_card_id': job_card.id,
                'department': line.department,
                'product_template_id': line.product_template_id.id if hasattr(line, 'product_template_id') else False,
                'description': line.name,
                'price_unit': line.price_unit,
                'quantity': line.product_uom_qty,
                'tax_ids': [(6, 0, line.tax_id.ids)] if hasattr(line, 'tax_id') else False,
                'discount': line.discount,
                'after_discount': line.price_unit * (1 - (line.discount or 0.0) / 100),
                'uom': line.product_uom.id if hasattr(line, 'product_uom') else False,
            })
        return {
            'name': 'Job Card',
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.management',
            'view_mode': 'form',
            'res_id': job_card.id,
            'target': 'current',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    department = fields.Selection([
        ('labour', 'Labour'),
        ('parts', 'Parts'),
        ('material', 'Material'),
        ('lubricant', 'Lubricant'),
        ('sublets', 'Sublets'),
        ('paint_material', 'Paint Material'),
        ('tyre', 'Tyre'),
        ('vehicle', 'Vehicle'),
    ], string="Department")
    # product_template_id_next = fields.Many2one('product.template', string="Part Number")



# part number onchange
#     @api.onchange('product_template_id_next')
#     def _onchange_product_template_id_next(self):
#         for line in self:
#             if line.product_template_id_next:
#                 # Find first variant of this template
#                 variant = self.env['product.product'].search([('product_tmpl_id', '=', line.product_template_id_next.id)],
#                                                              limit=1)
#                 if variant:
#                     line.product_id = variant.id  # set product_id for normal onchange chain
#                     line.product_uom = variant.uom_id
#                     line.product_uom_qty = 1
#                 else:
#                     line.product_id = False
#                     line.product_uom = False

