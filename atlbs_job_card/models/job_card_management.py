from datetime import datetime, date

datetime.now()
from importlib.resources._common import _
from xml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class VehicleStockBook(models.Model):
    _name = 'job.card.management'
    _description = 'Job Card Management'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Job Card Number', required=True, copy=False, readonly=True, default='New',tracking=True)
    # vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    register_no = fields.Many2one('fleet.vehicle',string="Plate No.")
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

    time_sheet_ids = fields.One2many('job.card.time.sheet','job_card_id',string="Time Sheets"
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

    service_advisor_id = fields.Many2one('res.users',string='Service Advisor',readonly=True,default=lambda self: self.env.user)

    created_datetime = fields.Datetime(string="Created Date",default=fields.Datetime.now,readonly=True)


    due_days = fields.Integer(string='Due Days', compute='_compute_due_days', store=True)
    due_days_label = fields.Char(string='Due In', compute='_compute_due_days', store=True)

    complaint_ids = fields.One2many('job.card.complaint', 'job_card_id', string='Complaints')

    is_estimate_printed = fields.Boolean(string='Estimate Printed', default=False)

    estimate_id = fields.Many2one('job.card.estimate', string="Estimate Reference")

    @api.depends('created_datetime')
    def _compute_due_days(self):
        for record in self:
            if record.created_datetime:
                diff = (fields.Date.today() - record.created_datetime.date()).days
                record.due_days = diff
                record.due_days_label = f"{diff} days"
            else:
                record.due_days = 0
                record.due_days_label = "0 days"



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




    # def action_print_estimate(self):
    #     self.ensure_one()
    #     if not self.estimate_id:
    #         raise UserError("No estimate linked to this Job Card.")
    #     return self.env.ref('atlbs_job_card.report_job_estimate_action').report_action(self.estimate_id)

    def action_print_estimate(self):
        self.ensure_one()
        if not self.estimate_id:
            raise UserError("No Estimate is linked to this Job Card.")

        self.is_estimate_printed = True  # Mark as printed
        return self.env.ref('atlbs_job_card.report_job_estimate_action').report_action(self.estimate_id)


    # here field hiding context added
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
                'from_job_card_origin': True,



            }
        }



    def action_complete_job_card(self):
        for rec in self:
            rec.state = 'completed'




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

    # def action_create_estimate(self):
    #     self.ensure_one()
    #
    #     estimate = self.env['job.card.estimate']
    #     if not self.job_estimate_id:
    #         # Auto-create estimate from job card
    #         estimate = estimate.create({
    #             'register_no': self.register_no.id,
    #             'vehicle_make_id': self.vehicle_make_id.id,
    #             'engine_no': self.engine_no,
    #             'odoo_meter_reading': self.odoo_meter_reading,
    #             'fuel_level': self.fuel_level,
    #             'vehicle_colour': self.vehicle_colour,
    #             'vin_sn': self.vin_sn,
    #             'partner_id': self.partner_id.id,
    #             'phone': self.phone,
    #             'email': self.email,
    #             'vat': self.vat,
    #             'whatsapp_no': self.whatsapp_no,
    #             'company_id': self.company_id.id,
    #             'vehicle_in_out': self.vehicle_in_out,
    #             'estimate_detail_line_ids': [
    #                 (0, 0, {
    #                     'department': line.department,
    #                     'description': line.description,
    #                     'product_template_id': line.product_template_id.id,
    #                     'price_unit': line.price_unit,
    #                     'quantity': line.quantity,
    #                     'tax_ids': [(6, 0, line.tax_ids.ids)],
    #                     'discount': line.discount,
    #                 }) for line in self.job_detail_line_ids if line.line_state != 'x_state'
    #             ],
    #         })
    #
    #         # Link back to job card
    #         self.job_estimate_id = estimate.id
    #     else:
    #         estimate = self.job_estimate_id
    #
    #     self.is_estimate_printed = True
    #     return self.env.ref('atlbs_job_card.report_job_estimate_action').report_action(estimate)

    # def action_create_estimate(self):
    #     self.ensure_one()
    #
    #     estimate = self.env['job.card.estimate'].create({
    #         'partner_id': self.partner_id.id,
    #         'register_no': self.register_no.id,
    #         'vehicle_make_id': self.vehicle_make_id.id,
    #         'engine_no': self.engine_no,
    #         'odoo_meter_reading': self.odoo_meter_reading,
    #         'fuel_level': self.fuel_level,
    #         'vehicle_colour': self.vehicle_colour,
    #         'vin_sn': self.vin_sn,
    #         'phone': self.phone,
    #         'email': self.email,
    #         'vat': self.vat,
    #         'whatsapp_no': self.whatsapp_no,
    #         'vehicle_in_out': self.vehicle_in_out,
    #         'company_id': self.company_id.id,
    #         'estimate_detail_line_ids': [(0, 0, {
    #             'description': line.description,
    #             'product_template_id': line.product_template_id.id,
    #             'quantity': line.quantity,
    #             'price_unit': line.price_unit,
    #             'department': line.department,
    #         }) for line in self.job_detail_line_ids]
    #     })
    #
    #     self.estimate_id = estimate.id  # create a Many2one field to link
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'job.card.estimate',
    #         'res_id': estimate.id,
    #         'view_mode': 'form',
    #         'target': 'current',
    #     }

    def action_create_estimate(self):
        self.ensure_one()
        estimate = self.env['job.card.estimate'].create({
            'register_no': self.register_no.id,
            'partner_id': self.partner_id.id,
            'vehicle_in_out': self.vehicle_in_out,
            'job_card_id': self.id,  # Link back
            'estimate_detail_line_ids': [(0, 0, {
                'description': l.description,
                'product_template_id': l.product_template_id.id,
                'quantity': l.quantity,
                'price_unit': l.price_unit,
                'department': l.department,
            }) for l in self.job_detail_line_ids]
        })
        self.estimate_id = estimate.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.estimate',
            'res_id': estimate.id,
            'view_mode': 'form',
            'target': 'current',
        }


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

    job_category_id = fields.Many2one(
        comodel_name='job.categories',
        string='Categories'
    )

    is_checked = fields.Boolean(string="Checked")






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

# removed this onchange and new one given for added tax
    # @api.onchange('product_template_id')
    # def _onchange_product_template_id(self):
    #     for line in self:
    #         if line.department == 'parts' and line.product_template_id:
    #             line.price_unit = line.product_template_id.list_price
    #             line.part_number = line.product_template_id.id

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        for line in self:
            if line.department == 'parts' and line.product_template_id:
                line.price_unit = line.product_template_id.list_price
                line.part_number = line.product_template_id.id

                # Set tax_ids to 5%DB tax if found
                tax = self.env['account.tax'].search([('name', '=', '5% DB')], limit=1)
                if tax:
                    line.tax_ids = [(6, 0, [tax.id])]



# added this funtion for fetching the labour line into time sheet
    @api.model
    def create(self, vals):
        print(">>> CREATE CALLED with vals:", vals)
        record = super().create(vals)

        if record.department == 'labour':
            print(">>> Creating time sheet for labour line")
            timesheet_vals = {
                'name': record.description,
                'assigned_hours': record.quantity,
                'job_category_id':record.job_category_id.id,
                'date': fields.Date.today(),
                'job_card_id': record.job_card_id.id,  # <-- ADD THIS
            }
            ts = self.env['job.card.time.sheet'].create(timesheet_vals)
            print(">>> Created timesheet ID:", ts.id)

        return record


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


class JobCardTimeSheet(models.Model):
    _name = 'job.card.time.sheet'
    _description = 'Job Card Time Sheet'
        # _rec_name = 'name'

    employee_id = fields.Many2one('hr.employee', string="Technician")
    start_time = fields.Float(string="Start Time")
    pause_time = fields.Float(string="Pause Time")
    end_time = fields.Float(string="End Time")
    status = fields.Selection([
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('paused', 'Paused'),
            ('done', 'Completed'),
        ], string="Status", default='new', tracking=True)

    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    date = fields.Date(string="Date", default=lambda self: fields.Date.today())
    name = fields.Char(string="Description")
    assigned_hours = fields.Float(string="Assigned Hours")
    working_hours = fields.Float(string="Working Hours", compute="_compute_working_hours", store=True)
    project_id = fields.Many2one('project.project', string='Project')
    analytic_line_id = fields.Many2one('account.analytic.line', string="Analytic Line")

    pause_start = fields.Float(string="Pause Start Time")
    pause_duration = fields.Float(string="Pause Duration", default=0.0)

    job_category_id = fields.Many2one(
        comodel_name='job.categories',
        string='Categories'
    )


    def _get_current_time_float(self):
        now = datetime.now()
        return now.hour + now.minute / 60.0 + now.second / 3600.0

    def action_start(self):
        current_time = self._get_current_time_float()
        self.write({
            'start_time': current_time,
            'status': 'in_progress',
            'pause_duration': 0.0,
            'pause_start': 0.0,
        })

    def action_pause(self):
        now = self._get_current_time_float()
        self.write({
            'pause_time': now,
            'status': 'paused',
        })

    # def action_resume(self):
    #     for rec in self:
    #         if rec.pause_start:
    #             now = rec._get_current_time_float()
    #             pause_time = now - rec.pause_start
    #             rec.write({
    #                 'pause_duration': rec.pause_duration + pause_time,
    #                 'pause_start': 0.0,
    #                 'status': 'in_progress',
    #             })

    def action_resume(self):
        for rec in self:
            if rec.pause_start:
                now = rec._get_current_time_float()
                duration = now - rec.pause_start
                rec.write({
                    'pause_duration': rec.pause_duration + duration,
                    'pause_start': 0.0,
                })
            # Update status regardless of pause_start
            rec.write({
                'status': 'in_progress',
            })

    def action_end(self):
        current_time = self._get_current_time_float()
        self.write({
            'end_time': current_time,
            'status': 'done',
        })

    # @api.depends('start_time', 'pause_time', 'end_time', 'status')
    # def _compute_working_hours(self):
    #     for rec in self:
    #         if rec.status == 'done' and rec.start_time and rec.end_time:
    #             pause = rec.pause_time or 0.0
    #             rec.working_hours = max((rec.end_time - rec.start_time) - pause, 0.0)
    #         else:
    #             rec.working_hours = 0.0

    @api.depends('start_time', 'end_time', 'pause_duration', 'status')
    def _compute_working_hours(self):
        print('fdeffffffff')
        for rec in self:
            if rec.status == 'done' and rec.start_time and rec.end_time:
                pause = rec.pause_duration or 0.0
                rec.working_hours = max((rec.end_time - rec.start_time) - pause, 0.0)
            else:
                rec.working_hours = 0.0

# commented and gave another create below
    # @api.model
    # def create(self, vals):
    #     # Set default project if not given
    #     if not vals.get('project_id'):
    #         project = self.env['project.project'].search([('id', '=', 1)], limit=1)
    #         vals['project_id'] = project.id if project else False
    #
    #     record = super().create(vals)
    #
    #     # Create related analytic line
    #     analytic_vals = {
    #         'date': record.date,
    #         'employee_id': record.employee_id.id,
    #         'project_id': record.project_id.id,
    #         'job_card_id': record.job_card_id.id,
    #         'name': record.name or 'Job Card Time Entry',
    #         'start_time': vals.get('start_time', 0.0),
    #         'pause_time': vals.get('pause_time', 0.0),
    #         'end_time': vals.get('end_time', 0.0),
    #         'status': vals.get('status', 'new'),
    #     }
    #     analytic = self.env['account.analytic.line'].create(analytic_vals)
    #     record.analytic_line_id = analytic.id
    #
    #     return record

#     def write(self, vals):
#         res = super().write(vals)
#         for rec in self:
#             if rec.analytic_line_id:
#                 rec.analytic_line_id.write({
#                     'employee_id': rec.employee_id.id,
#                     'start_time': rec.start_time,
#                     'pause_time': rec.pause_time,
#                     'end_time': rec.end_time,
#                     'status': rec.status,
#                 })
#         return res
#
#
#
#
#
#
# # added this create function for avoiding recursion and commented above
#     @api.model
#     def create(self, vals):
#         # Set default project if not given
#         if not vals.get('project_id'):
#             project = self.env['project.project'].search([('id', '=', 1)], limit=1)
#             vals['project_id'] = project.id if project else False
#
#         # Prevent recursion: If 'analytic_line_id' is already in vals, skip creating another analytic line
#         if 'analytic_line_id' in vals:
#             return super().create(vals)
#
#         # Create the job card time sheet record first
#         record = super().create(vals)
#
#         # Prepare analytic line values, link back to this time sheet record
#         analytic_vals = {
#             'date': record.date,
#             'employee_id': record.employee_id.id,
#             'project_id': record.project_id.id,
#             'job_card_id': record.job_card_id.id,
#             'name': record.name or 'Job Card Time Entry',
#             'start_time': record.start_time or 0.0,
#             'pause_time': record.pause_duration or record.pause_time or 0.0,
#             'end_time': record.end_time or 0.0,
#             'status': record.status or 'new',
#             'working_hours': record.working_hours or 0.0,
#             'assigned_hours': record.assigned_hours or 0.0,
#             # Optional: link back to the timesheet if you want two-way reference
#             # 'time_sheet_id': record.id,
#         }
#
#         # Create the analytic line record
#         analytic = self.env['account.analytic.line'].create(analytic_vals)
#
#         # Update the job card time sheet with the analytic line reference, but avoid recursion by writing directly (no triggers)
#         record.write({'analytic_line_id': analytic.id})
#
#         return record

    @api.model
    def create(self, vals):
        # Assign default project if not given
        if not vals.get('project_id'):
            project = self.env['project.project'].search([], limit=1)
            vals['project_id'] = project.id if project else False

        # Prevent recursion when creating analytic line
        if vals.get('analytic_line_id'):
            return super().create(vals)

        record = super().create(vals)

        # Create linked analytic line with context flag to prevent recursion
        analytic_vals = {
            'date': record.date,
            'employee_id': record.employee_id.id,
            'project_id': record.project_id.id,
            'job_card_id': record.job_card_id.id,
            'job_category_id': record.job_category_id.id,
            'name': record.name or 'Job Card Time Entry',
            'start_time': record.start_time or 0.0,
            'pause_time': record.pause_duration or record.pause_time or 0.0,
            'end_time': record.end_time or 0.0,
            'status': record.status or 'new',
            'working_hours': record.working_hours or 0.0,
            'assigned_hours': record.assigned_hours or 0.0,
            'job_card_time_sheet_id': record.id,
        }
        analytic = self.env['account.analytic.line'].with_context(skip_timesheet_sync=True).create(analytic_vals)

        # Link analytic line to timesheet
        record.write({'analytic_line_id': analytic.id})

        return record



    def write(self, vals):
        res = super(JobCardTimeSheet, self).write(vals)
        for rec in self:
            if self.env.context.get('skip_analytic_sync'):
                continue
            if rec.analytic_line_id:
                rec.analytic_line_id.with_context(skip_timesheet_sync=True).write({
                    'employee_id': rec.employee_id.id,
                    'start_time': rec.start_time,
                    'pause_time': rec.pause_time,
                    'end_time': rec.end_time,
                    'status': rec.status,
                    'working_hours': rec.working_hours,
                    'assigned_hours': rec.assigned_hours,
                    'job_category_id': rec.job_category_id.id,
                    'name': rec.name,
                    'date': rec.date,
                })
        return res






# class JobCardStage(models.Model):
#     _name = "job.card.stage"
#
#     name = fields.Char(string="Name")
#     value = fields.Char(string="Value")
#     color = fields.Char(string="Color")
#     job_card_id = fields.Many2one("job.card.management", string="Job Card")
#     count_vehicle_in = fields.Integer(string="Vehicle In Count", compute="compute_stage_records")
#     count_out = fields.Integer(string="Vehicle Out Count", compute="compute_stage_records")
#     count_total = fields.Integer(string="Total Count", compute="compute_stage_records")
#
#     def compute_stage_records(self):
#         """
#         Compute job card having state of Vehicle In
#         """
#         self.count_vehicle_in = self.env['job.card.management'].search_count(
#             [('vehicle_in_out', '=', 'vehicle_in')])
#         self.count_out = self.env['job.card.management'].search_count([('vehicle_in_out', '=', 'vehicle_out')])
#         self.count_total = self.env['job.card.management'].search_count([])
#
#     def get_action_job_card_ready(self):
#         """
#         Get action of job card
#         """
#         action_obj = self.env["ir.actions.actions"]
#         # Vehicle In
#         if self.value == 'vehicle_in':
#             action = action_obj._for_xml_id('atlbs_job_card.open_vehicle_in_job_card')
#
#
#         # Vehicle Out
#         if self.value == 'vehicle_out':
#             action = action_obj._for_xml_id('atlbs_job_card.open_out_job_card')
#             action['domain'] = [('vehicle_in_out', '=', 'vehicle_out')]
#
#
#         # Total
#         if self.value == 'total':
#             action = action_obj._for_xml_id('atlbs_job_card.open_total_job_card')
#
#         if action:
#             return action
#         return True


class JobCardComplaint(models.Model):
    _name = 'job.card.complaint'
    _description = 'Job Card Complaint'

    job_card_id = fields.Many2one('job.card.management', string='Job Card', ondelete='cascade')
    service_requested = fields.Char(string='Service Requested')
    description = fields.Text(string='Description')
    remarks = fields.Text(string='Remarks')