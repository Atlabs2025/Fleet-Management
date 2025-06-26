from datetime import datetime
datetime.now()
from importlib.resources._common import _
from xml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class JobCardEstimate(models.Model):
    _name = 'job.card.estimate'
    _description = 'Job Card Estimate'
    _rec_name = 'name'

    name = fields.Char(string='Estimate Number', required=True, copy=False, readonly=True, default='New')
    # vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    register_no = fields.Many2one('fleet.vehicle',string="Reg.No")
    # register_id = fields.Many2one('fleet.vehicle', string="Register Number")

    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string="Vehicle Model")
    engine_no = fields.Char(string="Engine Number")
    odoo_meter_reading = fields.Char(string="Odoo Meter Reading")
    fuel_level = fields.Char(string="Fuel Level")
    vehicle_colour = fields.Char(string="Vehicle Colour")
    # vin_number = fields.Char(string="VIN Number")
    vin_sn = fields.Char(string="VIN Number")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('memo', 'Memo'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ], string="Status", default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Customer', required=1)
    company_id = fields.Many2one('res.company',string="Company")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    vat = fields.Char(string="VAT")
    whatsapp_no = fields.Char(string="Whatsapp Number")
    estimate_detail_line_ids = fields.One2many('job.estimate.line', 'job_estimate_id', string="Job Details")


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

    is_insurance_claim = fields.Boolean(string="Is Insurance Claim", default=False, store=True)
    insurance_company_id = fields.Many2one('res.partner',string='Insurance Company')
    # insurance_company = fields.One2many('res.partner',string="Is Insurance Claim")

    # invoice_count = fields.Integer(string="Excess Invoice Count", compute='_compute_invoice_count')

    contract_status = fields.Selection([
        ('incontract', 'In Contract'),
        ('outcontract', 'Out of Contract'),
    ], string='Contract Status')
    service_contract_id = fields.Many2one('fleet.vehicle.log.contract', string='Service Contract', store=True)
    # contract_invoice_status = fields.Boolean('Contract Invoice Status')

    created_datetime = fields.Datetime(string="Created Date",default=fields.Datetime.now,readonly=True)

    job_card_id = fields.Many2one('job.card.management', string="Job Card")

    job_card_stage = fields.Selection([
        ('', ''),
        ('wip', 'Work in Progress'),
        ('hold', 'Hold'),
        ('no_action', 'No Action'),
        ('awaiting_parts', 'Waiting For Parts'),
        ('awaiting_approval', 'Waiting For Approval'),
        ('ready', 'Ready For Delivery'),
        ('delivered_not_invoiced', 'Delivered Not Invoiced'),
        ('insurance', 'Insurance'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ], string="Stage", store=True)

    @api.depends('estimate_detail_line_ids.total')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.estimate_detail_line_ids.mapped('total'))




    @api.depends('estimate_detail_line_ids.department', 'estimate_detail_line_ids.total',
                 'estimate_detail_line_ids.price_amt', 'estimate_detail_line_ids.after_discount',
                 'estimate_detail_line_ids.tax_amount')

    def _compute_totals(self):
        for rec in self:
            rec.total_labour = sum(line.total for line in rec.estimate_detail_line_ids if line.department == 'labour')
            rec.total_parts = sum(line.total for line in rec.estimate_detail_line_ids if line.department == 'parts')
            rec.total_material = sum(line.total for line in rec.estimate_detail_line_ids if line.department == 'material')
            rec.total_lubricant = sum(line.total for line in rec.estimate_detail_line_ids if line.department == 'lubricant')
            rec.total_sublets = sum(line.total for line in rec.estimate_detail_line_ids if line.department == 'sublets')
            rec.total_paint_material = sum(
                line.total for line in rec.estimate_detail_line_ids if line.department == 'paint_material')
            rec.total_tyre = sum(line.total for line in rec.estimate_detail_line_ids if line.department == 'tyre')

            rec.total_price_amt = sum(line.price_amt for line in rec.estimate_detail_line_ids)
            rec.total_discount = sum((line.price_amt - line.after_discount) for line in rec.estimate_detail_line_ids)
            rec.subtotal = sum(line.after_discount for line in rec.estimate_detail_line_ids)
            rec.vat_total = sum(line.tax_amount for line in rec.estimate_detail_line_ids)
            # rec.total_amount = rec.subtotal + rec.vat_total

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('job.card.estimate') or 'New'
        return super(JobCardEstimate, self).create(vals)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            if rec.partner_id:
                rec.phone = rec.partner_id.phone
                rec.email = rec.partner_id.email
                rec.vat = rec.partner_id.vat
                rec.whatsapp_no = rec.partner_id.whatsapp_no



    def action_create_estimate(self):

        self.state = 'memo'

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'








# here field hiding context added




    # @api.onchange('register_no')
    # def _onchange_register_no(self):
    #     if self.register_no:
    #         self.vehicle_make_id = self.register_no.brand_id.id
    #         self.engine_no = self.register_no.engine_no
    #         self.vin_sn = self.register_no.vin_sn
    #         self.partner_id = self.register_no.partner_id.id
    #
    #         # Fetch related service contract
    #         contract = self.env['fleet.vehicle.log.contract'].search([
    #             ('vehicle_id', '=', self.register_no.id)
    #         ], order='id desc', limit=1)
    #
    #         if contract and contract.state == 'open':
    #             self.contract_status = 'incontract'
    #         else:
    #             self.contract_status = 'outcontract'
    #     else:
    #         self.vehicle_make_id = False
    #         self.engine_no = ''
    #         self.vin_sn = ''
    #         self.contract_status = False

    @api.onchange('register_no')
    def _onchange_register_no(self):
        if self.register_no:
            self.vehicle_make_id = self.register_no.brand_id.id
            self.engine_no = self.register_no.engine_no
            self.vin_sn = self.register_no.vin_sn
            self.odoo_meter_reading = self.register_no.odometer
            self.partner_id = self.register_no.partner_id.id

            # Fetch the latest contract (open or closed)
            contract = self.env['fleet.vehicle.log.contract'].search([
                ('vehicle_id', '=', self.register_no.id)
            ], order='id desc', limit=1)

            if contract:
                self.service_contract_id = contract.id
                self.contract_status = 'incontract' if contract.state == 'open' else 'outcontract'
            else:
                self.service_contract_id = False
                self.contract_status = False
        else:
            self.vehicle_make_id = False
            self.engine_no = ''
            self.vin_sn = ''
            self.odoo_meter_reading = 0.0
            self.partner_id = False
            self.service_contract_id = False
            self.contract_status = False

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone:
            partner = self.env['res.partner'].search([('phone', '=', self.phone)], limit=1)
            if partner:
                self.partner_id = partner.id
                self.email = partner.email
                self.whatsapp_no = partner.whatsapp_no
            else:
                self.partner_id = False
                self.email = False
                self.whatsapp_no = False
        else:
            self.partner_id = False
            self.email = False
            self.whatsapp_no = False



    @api.onchange('vin_sn')
    def _onchange_vin_sn(self):
        if self.vin_sn:
            vehicle = self.env['fleet.vehicle'].search([('vin_sn', '=', self.vin_sn)], limit=1)
            if vehicle:
                self.vehicle_make_id = vehicle.brand_id.id
                self.engine_no = vehicle.engine_no
                self.register_no = vehicle.id

    # def action_create_job_card(self):
    #     self.ensure_one()
    #
    #     # Create Job Card and optionally lines
    #     job_card = self.env['job.card.management'].create({
    #         'partner_id': self.partner_id.id,
    #         'register_no': self.register_no.id,
    #         'vehicle_in_out': self.vehicle_in_out,
    #         'job_estimate_id': self.id,
    #         # 'job_estimate_id': self.id,
    #         'job_detail_line_ids': [(0, 0, {
    #             'description': line.description,
    #             'product_template_id': line.product_template_id.id,
    #             'quantity': line.quantity,
    #             'price_unit': line.price_unit,
    #             'department': line.department,
    #         }) for line in self.estimate_detail_line_ids],
    #     })
    #
    #     # self.job_card_id = job_card.id
    #
    #
    #     # Optionally redirect to the Job Card
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Job Card',
    #         'res_model': 'job.card.management',
    #         'res_id': job_card.id,
    #         'view_mode': 'form',
    #         'target': 'current',
    #     }

    def action_create_job_card(self):
        self.ensure_one()
        job_card = self.env['job.card.management'].create({
            'register_no': self.register_no.id,
            'partner_id': self.partner_id.id,
            'vehicle_in_out': self.vehicle_in_out,
            'estimate_id': self.id,
            'job_detail_line_ids': [(0, 0, {
                'description': l.description,
                'product_template_id': l.product_template_id.id,
                'quantity': l.quantity,
                'price_unit': l.price_unit,
                'department': l.department,
            }) for l in self.estimate_detail_line_ids]
        })
        self.job_card_id = job_card.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.management',
            'res_id': job_card.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_approve_estimate(self):
        for rec in self:
            rec.state = 'approved'

class JobCardLine(models.Model):
    _name = 'job.estimate.line'
    _description = 'Job Card Line'

    job_estimate_id = fields.Many2one('job.card.estimate', string="Estimate")
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





    # part_number = fields.Char(string="Part Number")
    part_number = fields.Many2one(
        'product.template',
        string="Product",

    )

    job_category_id = fields.Many2one(
        comodel_name='job.categories',
        string='Categories'
    )

    @api.depends('price_unit', 'quantity', 'discount', 'tax_ids')
    def _compute_total(self):
        for line in self:
            # Step 1: Calculate Amount (Quantity * Price)
            amount = line.price_unit * line.quantity
            line.price_amt = amount

            # Step 2: Apply Discount
            discount_amount = amount * (line.discount / 100.0)
            after_discount_amount = amount - discount_amount
            line.after_discount = after_discount_amount

            # Step 3: Apply VAT (tax percentage)
            vat_amount = 0.0
            if line.tax_ids:
                for tax in line.tax_ids:
                    if tax.amount:
                        vat_amount += after_discount_amount * (tax.amount / 100.0)

            line.tax_amount = vat_amount

            # Step 4: Total = After Discount + VAT Amount
            line.total = after_discount_amount + vat_amount







# commented on saturday complete button add cheyyan paranjath kondu
#     def write(self, vals):
#         res = super().write(vals)
#         for line in self:
#             job_estimate = line.job_estimate_id
#             if job_estimate and all(l.invoiced for l in job_estimate.estimate_detail_line_ids):
#                 job_estimate.state = 'completed'
#         return res



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
                line.part_number = line.product_template_id.id
















