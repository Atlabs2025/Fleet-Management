import datetime
from importlib.resources._common import _
from xml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class VehicleStockBook(models.Model):
    _name = 'job.card.management'
    _description = 'Job Card Management'
    _rec_name = 'name'

    name = fields.Char(string='Job Card Number', required=True, copy=False, readonly=True, default='New')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    register_no = fields.Char(string="Register Number")
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string="Vehicle Model")
    # chassis_no = fields.Char(string="Chassis Number")
    engine_no = fields.Char(string="Engine Number")
    odoo_meter_reading = fields.Char(string="Odoo Meter Reading")
    fuel_level = fields.Char(string="Fuel Level")
    vehicle_colour = fields.Char(string="Vehicle Colour")
    # vin_number = fields.Char(string="VIN Number")
    vin_sn = fields.Char(string="Chassis Number")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('memo', 'Memo'),
        ('completed', 'Completed'),
    ], string="Status", default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Customer', required=1)
    company_id = fields.Many2one('res.company',string="Company")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    vat = fields.Char(string="VAT")
    whatsapp_no = fields.Char(string="Whatsapp Number")
    job_detail_line_ids = fields.One2many('job.card.line', 'job_card_id', string="Job Details")


    total_labour = fields.Float(string="Total Labour", compute="_compute_totals")
    total_parts = fields.Float(string="Total Parts", compute="_compute_totals")
    total_material = fields.Float(string="Total Material", compute="_compute_totals")
    total_lubricant = fields.Float(string="Total Lubricant", compute="_compute_totals")
    total_sublets = fields.Float(string="Total Sublets", compute="_compute_totals")
    total_paint_material = fields.Float(string="Total Paint Material", compute="_compute_totals")
    total_tyre = fields.Float(string="Total Tyre", compute="_compute_totals")

    total_price_amt = fields.Float(string="Total Price", compute="_compute_totals")
    total_discount = fields.Float(string="Discount", compute="_compute_totals")
    subtotal = fields.Float(string="Subtotal", compute="_compute_totals")
    vat_total = fields.Float(string="VAT 5%", compute="_compute_totals")
    total_amount = fields.Float(string="Grand Total", compute="_compute_totals")

    vehicle_in_out = fields.Selection([('vehicle_in', 'IN'),('vehicle_out', 'OUT')], string="Vehicle IN/OUT", default='', tracking=True)

    # invoiced = fields.Boolean(string="Invoiced", default=False)

    total_amount = fields.Monetary(
        string="Grand Total",
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )



    material_request_ids = fields.One2many(
        'job.card.material.request',
        'job_card_id',
        string='Material Requests'
    )

    service_line_ids = fields.One2many('job.card.service.line', 'job_card_id', string="Service Lines")

    is_insurance_claim = fields.Boolean(string="Is Insurance Claim", default=False, store=True)
    insurance_company_id = fields.Many2one('res.partner',string='Insurance Company')
    # insurance_company = fields.One2many('res.partner',string="Is Insurance Claim")

    # invoice_count = fields.Integer(string="Excess Invoice Count", compute='_compute_invoice_count')

    def open_excess_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Excess Invoices',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('job_card_id', '=', self.id), ('move_type', '=', 'out_invoice')],
            'context': {
                'default_job_card_id': self.id,
                # 'default_partner_id': self.insurance_company_id.id if self.is_insurance_claim else self.partner_id.id,
                'default_partner_id':self.partner_id.id,
                'default_move_type': 'out_invoice',
            },
        }



    def _compute_invoice_count(self):
        for record in self:
            # Compute the number of invoices related to the job card
            count = self.env['account.move'].search_count([
                ('job_card_id', '=', record.id),
                ('move_type', '=', 'out_invoice')
            ])
            record.invoice_count = count



    @api.depends('job_detail_line_ids.total')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.job_detail_line_ids.mapped('total'))



    # @api.depends('job_detail_line_ids.department', 'job_detail_line_ids.total')
    # def _compute_totals(self):
    #     for rec in self:
    #         rec.total_labour = sum(line.total for line in rec.job_detail_line_ids if line.department == 'labour')
    #         rec.total_parts = sum(line.total for line in rec.job_detail_line_ids if line.department == 'parts')
    #         rec.total_material = sum(line.total for line in rec.job_detail_line_ids if line.department == 'material')
    #         rec.total_lubricant = sum(line.total for line in rec.job_detail_line_ids if line.department == 'lubricant')
    #         rec.total_sublets = sum(line.total for line in rec.job_detail_line_ids if line.department == 'sublets')
    #         rec.total_paint_material = sum(
    #             line.total for line in rec.job_detail_line_ids if line.department == 'paint_material')
    #         rec.total_tyre = sum(line.total for line in rec.job_detail_line_ids if line.department == 'tyre')

    @api.depends('job_detail_line_ids.department', 'job_detail_line_ids.total',
                 'job_detail_line_ids.price_amt', 'job_detail_line_ids.after_discount',
                 'job_detail_line_ids.tax_amount')

    def _compute_totals(self):
        for rec in self:
            rec.total_labour = sum(line.total for line in rec.job_detail_line_ids if line.department == 'labour')
            rec.total_parts = sum(line.total for line in rec.job_detail_line_ids if line.department == 'parts')
            rec.total_material = sum(line.total for line in rec.job_detail_line_ids if line.department == 'material')
            rec.total_lubricant = sum(line.total for line in rec.job_detail_line_ids if line.department == 'lubricant')
            rec.total_sublets = sum(line.total for line in rec.job_detail_line_ids if line.department == 'sublets')
            rec.total_paint_material = sum(
                line.total for line in rec.job_detail_line_ids if line.department == 'paint_material')
            rec.total_tyre = sum(line.total for line in rec.job_detail_line_ids if line.department == 'tyre')

            rec.total_price_amt = sum(line.price_amt for line in rec.job_detail_line_ids)
            rec.total_discount = sum((line.price_amt - line.after_discount) for line in rec.job_detail_line_ids)
            rec.subtotal = sum(line.after_discount for line in rec.job_detail_line_ids)
            rec.vat_total = sum(line.tax_amount for line in rec.job_detail_line_ids)
            # rec.total_amount = rec.subtotal + rec.vat_total

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('job.card.management') or 'New'
        return super(VehicleStockBook, self).create(vals)

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        for rec in self:
            if rec.vehicle_id:
                rec.vehicle_make_id = rec.vehicle_id.model_id.brand_id
                # rec.vin_number = rec.vehicle_id.vin_number
                rec.vin_sn = rec.vehicle_id.vin_sn
                rec.engine_no = rec.vehicle_id.engine_no
                rec.register_no = rec.vehicle_id.license_plate

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.phone = rec.partner_id.phone
                rec.email = rec.partner_id.email
                rec.vat = rec.partner_id.vat
                rec.whatsapp_no = rec.partner_id.whatsapp_no

    def action_create_job_card(self):

        self.state = 'memo'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_create_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
            },
        }


    def action_preforma_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
            },
        }




    def action_create_estimate(self):
        return self.env.ref('atlbs_job_card.report_job_estimate_action').report_action(self)



    # def action_open_material_requisition_form(self):
    #     self.ensure_one()
    #     employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
    #
    #     return {
    #         'name': 'Create Material Requisition',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'material.purchase.requisition',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_job_card_id': self.id,
    #             'default_employee_id': employee.id if employee else False,
    #             'default_job_number': self.name,
    #         }
    #     }

    def action_open_material_requisition_form(self):
        self.ensure_one()
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        return {
            'name': 'Create Material Requisition',
            'type': 'ir.actions.act_window',
            'res_model': 'material.purchase.requisition',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_job_card_id': self.id,
                'default_employee_id': employee.id if employee else False,
                'default_job_number': self.name,
            }
        }



    def action_complete_job_card(self):
        for rec in self:
            rec.state = 'completed'



class JobCardLine(models.Model):
    _name = 'job.card.line'
    _description = 'Job Card Line'

    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    department = fields.Selection([
        ('labour', 'Labour'),
        ('parts', 'Parts'),
        ('material', 'Material'),
        ('lubricant', 'Lubricant'),
        ('sublets', 'Sublets'),
        ('paint_material', 'Paint Material'),
        ('tyre', 'Tyre'),
    ], string="Department")

    description = fields.Text(string="Description")
    product_template_id = fields.Many2one('product.template', string="Part Number")
    price_unit = fields.Float(string="Unit Price")
    price_amt = fields.Float(string="Amount")
    quantity = fields.Float(string="Qty")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    discount = fields.Float(string="Discount (%)")
    after_discount = fields.Float(string="After Discount")
    tax_amount = fields.Float(string="Tax Amount")


    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )


    total = fields.Monetary(
        string="Total",
        compute='_compute_total',
        store=True,
        currency_field='currency_id'
    )

    line_state = fields.Selection([
        ('memo', 'Memo'),
        ('complete', 'Complete'),
        ('x_state', 'X'),
    ], string="State", default='memo')

    invoiced = fields.Boolean(string="Invoiced", default=False,store=True)

    # is_request_completed = fields.Boolean(string="Is Completed",
    #                                       compute='_compute_is_request_completed', store=True)

    is_request_completed = fields.Boolean(
        string='Material Request Completed',
        compute='_compute_material_request_status',
        store=False
    )

    is_request_pending = fields.Boolean(
        string='Material Request Pending',
        compute='_compute_material_request_status',
        store=False
    )

    # part_number = fields.Char(string="Part Number")
    part_number = fields.Many2one(
        'product.template',
        string="Product",

    )



    @api.depends('product_template_id', 'job_card_id')
    def _compute_material_request_status(self):
        for line in self:
            completed = False
            pending = False
            if line.product_template_id and line.job_card_id:
                requests = self.env['job.card.material.request'].search([
                    ('job_card_id', '=', line.job_card_id.id),
                    ('product_id.product_tmpl_id', '=', line.product_template_id.id),
                ])
                for req in requests:
                    if req.id:  # Ensure it’s saved in DB
                        if req.state == 'completed':
                            completed = True
                        elif req.state == 'pending':
                            pending = True
            line.is_request_completed = completed
            line.is_request_pending = pending

    # @api.depends('price_unit', 'quantity', 'discount', 'tax_ids')
    # def _compute_total(self):
    #     for line in self:
    #         # Step 1: Calculate Amount (Quantity * Price)
    #         amount = line.price_unit * line.quantity
    #
    #         # Step 2: Apply Discount
    #         discount_amount = amount * (line.discount / 100.0)
    #         after_discount_amount = amount - discount_amount
    #         line.after_discount = after_discount_amount
    #
    #         # Step 3: Apply VAT (tax percentage)
    #         vat_amount = 0.0
    #         if line.tax_ids:
    #             for tax in line.tax_ids:
    #                 if tax.amount:  # Check if there's a valid tax percentage
    #                     vat_amount += after_discount_amount * (tax.amount / 100.0)
    #
    #         line.tax_amount = vat_amount
    #
    #         # Step 4: Total = After Discount + VAT Amount
    #         line.total = after_discount_amount + vat_amount

    @api.depends('price_unit', 'quantity', 'discount', 'tax_ids')
    def _compute_total(self):
        for line in self:
            # Step 1: Calculate Amount (Quantity * Price)
            amount = line.price_unit * line.quantity
            line.price_amt = amount  # Update the price_amt field with the calculated amount

            # Step 2: Apply Discount
            discount_amount = amount * (line.discount / 100.0)
            after_discount_amount = amount - discount_amount
            line.after_discount = after_discount_amount

            # Step 3: Apply VAT (tax percentage)
            vat_amount = 0.0
            if line.tax_ids:
                for tax in line.tax_ids:
                    if tax.amount:  # Check if there's a valid tax percentage
                        vat_amount += after_discount_amount * (tax.amount / 100.0)

            line.tax_amount = vat_amount

            # Step 4: Total = After Discount + VAT Amount
            line.total = after_discount_amount + vat_amount





    # @api.depends('price_unit', 'quantity', 'discount')
    # def _compute_total(self):
    #     for line in self:
    #         subtotal = line.price_unit * line.quantity
    #         discount_amount = subtotal * (line.discount / 100.0)
    #         line.total = subtotal - discount_amount

# commented on saturday complete button add cheyyan paranjath kondu
    def write(self, vals):
        res = super().write(vals)
        for line in self:
            job_card = line.job_card_id
            if job_card and all(l.invoiced for l in job_card.job_detail_line_ids):
                job_card.state = 'completed'
        return res



# making products mandatory for parts
    @api.constrains('department', 'product_template_id')
    def _check_product_required_for_parts(self):
        for rec in self:
            if rec.department == 'parts' and not rec.product_template_id:
                raise ValidationError("Please choose a product for Parts department.")


    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        for line in self:
            if line.department == 'parts' and line.product_template_id:
                line.price_unit = line.product_template_id.list_price
                line.part_number = line.product_template_id.default_code




class JobCardMaterialRequest(models.Model):
    _name = 'job.card.material.request'
    _description = 'Job Card Material Request'

    job_card_id = fields.Many2one(
        'job.card.management',
        string='Job Card',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True
    )

    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.today,
        required=True
    )

    requisition_type= fields.Selection(
        [('internal', 'Internal'), ('purchase', 'Purchase')],
        string='Requisition Type',
        default='internal'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    description = fields.Char(string='Description')

    qty = fields.Float(string='Quantity')

    uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure'
    )

    state = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ], string="Status", default='pending', tracking=True)

# for passing the completed information(merial request) into job card line
#     def write(self, vals):
#         res = super().write(vals)
#         if 'state' in vals and vals['state'] == 'completed':
#             for request in self:
#                 lines = self.env['job.card.line'].search([
#                     ('job_card_id', '=', request.job_card_id.id),
#                     ('product_template_id', '=', request.product_id.product_tmpl_id.id),
#                 ])
#                 lines._compute_is_request_completed()
#         return res

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            for request in self:
                lines = self.env['job.card.line'].search([
                    ('job_card_id', '=', request.job_card_id.id),
                    ('product_template_id', '=', request.product_id.product_tmpl_id.id),
                ])
                # Force recompute of both fields
                lines._compute_material_request_status()
        return res


class JobCardServiceLine(models.Model):
    _name = 'job.card.service.line'
    _description = 'Job Card Service Line'

    job_card_id = fields.Many2one('job.card.management', string="Job Card", required=True, ondelete="cascade")

    menu_service = fields.Selection([
        ('regular', 'Regular'),
        ('medium', 'Medium'),
        ('major', 'Major'),
        ('loop_services', 'Loop Services'),
    ], string="Menu Service")

    service_amount = fields.Float(string="Service Amount")

    product_template_ids = fields.Many2many('product.template', string="Products")


    @api.onchange('menu_service')
    def _onchange_menu_service(self):
        for rec in self:
            rec._compute_service_details()

    def _compute_service_details(self):
        """Common logic: set amount and products based on menu_service."""
        service_prices = {
            'regular': 500,
            'medium': 1000,
            'major': 2000,
            'loop_services': 300,
        }
        if self.menu_service:
            self.service_amount = service_prices.get(self.menu_service, 0.0)
            products = self.env['product.template'].search([('menu_service', '=', self.menu_service)])
            self.product_template_ids = [(6, 0, products.ids)]
        else:
            self.service_amount = 0.0
            self.product_template_ids = [(5, 0, 0)]  # clear

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._compute_service_details()
        return records


