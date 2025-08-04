from odoo import models, fields, api
from odoo.exceptions import UserError


class JobCardInvoiceWizard(models.TransientModel):
    _name = 'job.card.invoice.wizard'
    _description = 'Job Card Invoice Wizard'

    job_card_id = fields.Many2one('job.card.management', required=True, readonly=True)
    line_ids = fields.One2many('job.card.invoice.wizard.line', 'wizard_id')

    service_line_ids = fields.One2many('job.card.invoice.wizard.service.line', 'wizard_id', string="Service Lines")


    # @api.model
    # def default_get(self, fields):
    #     res = super().default_get(fields)
    #     active_id = self.env.context.get('active_id')
    #     job_card = self.env['job.card.management'].browse(active_id)
    #
    #     lines = []
    #     # for line in job_card.job_detail_line_ids.filtered(lambda l: not l.invoiced):
    #     for line in job_card.job_detail_line_ids.filtered(lambda l: not l.invoiced and l.line_state == 'complete'):
    #         print("Preparing line with ID:", line.id)
    #         lines.append((0, 0, {
    #             'line_id': line.id,  # This must be valid Many2one
    #             'description': line.description,
    #             'product_template_id': line.product_template_id,
    #             'price_unit': line.price_unit,
    #             'quantity': line.quantity,
    #             'discount': line.discount,
    #             'total': line.total,
    #             'department': line.department,
    #             'selected': False,
    #         }))
    #     res.update({
    #         'job_card_id': job_card.id,
    #         'line_ids': lines,
    #     })
    #     return res

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get('active_id')
        job_card = self.env['job.card.management'].browse(active_id)

        lines = []
        service_lines = []

        # Fetch job card lines for invoicing
        for line in job_card.job_detail_line_ids.filtered(lambda l: not l.invoiced and l.line_state == 'complete'):
            lines.append((0, 0, {
                'line_id': line.id,
                'description': line.description,
                'product_template_id': line.product_template_id.id,
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'discount': line.discount,
                'total': line.total,
                'department': line.department,
                'selected': False,
            }))

        # Fetch job card service lines
        for service_line in job_card.service_line_ids:
            service_lines.append((0, 0, {
                'service_line_id': service_line.id,
                'menu_service': service_line.menu_service,
                'service_amount': service_line.service_amount,
                'product_template_ids': service_line.product_template_ids.ids,
            }))

        res.update({
            'job_card_id': job_card.id,
            'line_ids': lines,
            'service_line_ids': service_lines,  # Add service lines to the wizard
        })
        return res








      # code changed for invoice creation and decreesing stock and creating vendor bills for sublet and service lines also invoiced
    # def action_create_invoice(self):
    #     self.ensure_one()
    #
    #     selected_lines = self.line_ids.filtered(lambda l: l.selected)
    #     selected_service_lines = self.service_line_ids.filtered(lambda l: l.service_selected)
    #
    #     if not selected_lines and not selected_service_lines:
    #         raise UserError("Please select at least one line or service to invoice.")
    #
    #     invoice_lines = []
    #     stock_moves = []
    #     sublet_vendor_bill_lines = []
    #
    #     # Job Card Detail Lines
    #     for line in selected_lines:
    #         if line.quantity <= 0:
    #             raise UserError(f"Quantity must be greater than 0 for line: {line.description}")
    #
    #         product_id = False
    #         if line.department == 'parts' and line.product_template_id:
    #             product = line.product_template_id.product_variant_id
    #             product_id = product.id
    #
    #             # Add to stock move list
    #             stock_moves.append((0, 0, {
    #                 'name': product.name,
    #                 'product_id': product.id,
    #                 'product_uom_qty': line.quantity,
    #                 'product_uom': product.uom_id.id,
    #                 'location_id': self.env.ref('stock.stock_location_stock').id,
    #                 'location_dest_id': self.job_card_id.partner_id.property_stock_customer.id,
    #             }))
    #
    #         invoice_lines.append((0, 0, {
    #             'name': f"{line.department or ''} - {line.description}",
    #             'product_id': product_id,
    #             'quantity': line.quantity,
    #             'price_unit': line.price_unit,
    #             'discount': line.discount,
    #         }))
    #
    #         # Prepare Sublet Vendor Bill lines
    #         if line.department == 'sublets':
    #             sublet_vendor_bill_lines.append((0, 0, {
    #                 'name': f"Sublet - {line.description}",
    #                 'quantity': line.quantity,
    #                 'price_unit': line.price_unit,
    #             }))
    #
    #     # Service Lines
    #     for service_line in selected_service_lines:
    #         if service_line.service_amount <= 0:
    #             raise UserError(f"Service amount must be greater than 0 for service: {service_line.menu_service}")
    #
    #         invoice_lines.append((0, 0, {
    #             'name': f"Service - {service_line.menu_service}",
    #             'quantity': 1,
    #             'price_unit': service_line.service_amount,
    #             'discount': 0.0,
    #         }))
    #
    #     if not invoice_lines:
    #         raise UserError("No valid lines to invoice.")
    #
    #     # Create Customer Invoice
    #     invoice_vals = {
    #         'partner_id': self.job_card_id.partner_id.id,
    #         'invoice_origin': f"Job Card: {self.job_card_id.name}",
    #         'move_type': 'out_invoice',
    #         'invoice_line_ids': invoice_lines,
    #         'job_card_id': self.job_card_id.id,
    #     }
    #     invoice = self.env['account.move'].create(invoice_vals)
    #
    #     # Create and validate delivery order if stock moves exist
    #     if stock_moves:
    #         picking = self.env['stock.picking'].create({
    #             'partner_id': self.job_card_id.partner_id.id,
    #             'picking_type_id': self.env.ref('stock.picking_type_out').id,
    #             'location_id': self.env.ref('stock.stock_location_stock').id,
    #             'location_dest_id': self.job_card_id.partner_id.property_stock_customer.id,
    #             'origin': f"Job Card: {self.job_card_id.name}",
    #             'move_ids_without_package': stock_moves,
    #         })
    #         picking.action_confirm()
    #         picking.action_assign()
    #         picking.button_validate()
    #
    #     # Create Vendor Bill if Sublet lines exist
    #     if sublet_vendor_bill_lines:
    #         vendor_bill_vals = {
    #             'partner_id': self.job_card_id.partner_id.id if self.job_card_id.partner_id else False,
    #             'invoice_origin': f"Sublet for Job Card: {self.job_card_id.name}",
    #             'move_type': 'in_invoice',
    #             'invoice_line_ids': sublet_vendor_bill_lines,
    #             'job_card_id': self.job_card_id.id,
    #         }
    #         vendor_bill = self.env['account.move'].create(vendor_bill_vals)
    #
    #     # Mark job detail lines as invoiced
    #     for wizard_line in selected_lines:
    #         if wizard_line.line_id:
    #             wizard_line.line_id.write({
    #                 'invoiced': True,
    #                 'line_state': 'x_state',
    #             })
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Customer Invoice',
    #         'view_mode': 'form',
    #         'res_model': 'account.move',
    #         'res_id': invoice.id,
    #         'target': 'current',
    #     }


# final code with above modifications and added is insurance claim also
#     def action_create_invoice(self):
#         self.ensure_one()
#
#         selected_lines = self.line_ids.filtered(lambda l: l.selected)
#         selected_service_lines = self.service_line_ids.filtered(lambda l: l.service_selected)
#
#         if not selected_lines and not selected_service_lines:
#             raise UserError("Please select at least one line or service to invoice.")
#
#         invoice_lines = []
#         stock_moves = []
#         sublet_vendor_bill_lines = []
#
#         # Job Card Detail Lines
#         for line in selected_lines:
#             if line.quantity <= 0:
#                 raise UserError(f"Quantity must be greater than 0 for line: {line.description}")
#
#             product_id = False
#             if line.department == 'parts' and line.product_template_id:
#                 product = line.product_template_id.product_variant_id
#                 product_id = product.id
#
#                 # Add to stock move list
#                 stock_moves.append((0, 0, {
#                     'name': product.name,
#                     'product_id': product.id,
#                     'product_uom_qty': line.quantity,
#                     'product_uom': product.uom_id.id,
#                     'location_id': self.env.ref('stock.stock_location_stock').id,
#                     'location_dest_id': self.job_card_id.partner_id.property_stock_customer.id,
#                 }))
#
#             invoice_lines.append((0, 0, {
#                 'name': f"{line.department or ''} - {line.description}",
#                 'product_id': product_id,
#                 'quantity': line.quantity,
#                 'price_unit': line.price_unit,
#                 'discount': line.discount,
#             }))
#
#             # Prepare Sublet Vendor Bill lines
#             if line.department == 'sublets':
#                 sublet_vendor_bill_lines.append((0, 0, {
#                     'name': f"Sublet - {line.description}",
#                     'quantity': line.quantity,
#                     'price_unit': line.price_unit,
#                 }))
#
#         # Service Lines
#         for service_line in selected_service_lines:
#             if service_line.service_amount <= 0:
#                 raise UserError(f"Service amount must be greater than 0 for service: {service_line.menu_service}")
#
#             invoice_lines.append((0, 0, {
#                 'name': f"Service - {service_line.menu_service}",
#                 'quantity': 1,
#                 'price_unit': service_line.service_amount,
#                 'discount': 0.0,
#             }))
#
#         if not invoice_lines:
#             raise UserError("No valid lines to invoice.")
#
#         # Determine correct partner for the customer invoice
#         invoice_partner = (
#             self.job_card_id.insurance_company_id
#             if self.job_card_id.is_insurance_claim
#             else self.job_card_id.partner_id
#         )
#
#         # Create Customer Invoice
#         invoice_vals = {
#             'partner_id': invoice_partner.id,
#             'invoice_origin': f"Job Card: {self.job_card_id.name}",
#             'move_type': 'out_invoice',
#             'invoice_line_ids': invoice_lines,
#             'job_card_id': self.job_card_id.id,
#         }
#         invoice = self.env['account.move'].create(invoice_vals)
#
#         # Create and validate delivery order if stock moves exist
#         if stock_moves:
#             picking = self.env['stock.picking'].create({
#                 'partner_id': self.job_card_id.partner_id.id,
#                 'picking_type_id': self.env.ref('stock.picking_type_out').id,
#                 'location_id': self.env.ref('stock.stock_location_stock').id,
#                 'location_dest_id': self.job_card_id.partner_id.property_stock_customer.id,
#                 'origin': f"Job Card: {self.job_card_id.name}",
#                 'move_ids_without_package': stock_moves,
#             })
#             picking.action_confirm()
#             picking.action_assign()
#             picking.button_validate()
#
#         # Create Vendor Bill if Sublet lines exist
#         if sublet_vendor_bill_lines:
#             vendor_bill_vals = {
#                 'partner_id': self.job_card_id.partner_id.id if self.job_card_id.partner_id else False,
#                 'invoice_origin': f"Sublet for Job Card: {self.job_card_id.name}",
#                 'move_type': 'in_invoice',
#                 'invoice_line_ids': sublet_vendor_bill_lines,
#                 'job_card_id': self.job_card_id.id,
#             }
#             vendor_bill = self.env['account.move'].create(vendor_bill_vals)
#
#         # Mark job detail lines as invoiced
#         for wizard_line in selected_lines:
#             if wizard_line.line_id:
#                 wizard_line.line_id.write({
#                     'invoiced': True,
#                     'line_state': 'x_state',
#                 })
#
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Customer Invoice',
#             'view_mode': 'form',
#             'res_model': 'account.move',
#             'res_id': invoice.id,
#             'target': 'current',
#         }
# new function added on auguest4 because of an error if any issue please refer above code ok
    def action_create_invoice(self):
        self.ensure_one()

        selected_lines = self.line_ids.filtered(lambda l: l.selected)
        selected_service_lines = self.service_line_ids.filtered(lambda l: l.service_selected)

        if not selected_lines and not selected_service_lines:
            raise UserError("Please select at least one line or service to invoice.")

        invoice_lines = []
        stock_moves = []
        sublet_vendor_bill_lines = []

        # Get stock location for current company
        stock_location = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('company_id', '=', self.job_card_id.company_id.id)
        ], limit=1)

        if not stock_location:
            raise UserError("No internal stock location found for the job card's company.")

        # Job Card Detail Lines
        for line in selected_lines:
            if line.quantity <= 0:
                raise UserError(f"Quantity must be greater than 0 for line: {line.description}")

            product_id = False
            if line.department == 'parts' and line.product_template_id:
                product = line.product_template_id.product_variant_id
                product_id = product.id

                # Add to stock move list
                stock_moves.append((0, 0, {
                    'name': product.name,
                    'product_id': product.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': product.uom_id.id,
                    'location_id': stock_location.id,
                    'location_dest_id': self.job_card_id.partner_id.property_stock_customer.id,
                }))

            invoice_lines.append((0, 0, {
                'name': f"{line.department or ''} - {line.description}",
                'product_id': product_id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }))

            # Prepare Sublet Vendor Bill lines
            if line.department == 'sublets':
                sublet_vendor_bill_lines.append((0, 0, {
                    'name': f"Sublet - {line.description}",
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                }))

        # Service Lines
        for service_line in selected_service_lines:
            if service_line.service_amount <= 0:
                raise UserError(f"Service amount must be greater than 0 for service: {service_line.menu_service}")

            invoice_lines.append((0, 0, {
                'name': f"Service - {service_line.menu_service}",
                'quantity': 1,
                'price_unit': service_line.service_amount,
                'discount': 0.0,
            }))

        if not invoice_lines:
            raise UserError("No valid lines to invoice.")

        # Determine correct partner for the customer invoice
        invoice_partner = (
            self.job_card_id.insurance_company_id
            if self.job_card_id.is_insurance_claim
            else self.job_card_id.partner_id
        )

        # Create Customer Invoice
        invoice_vals = {
            'partner_id': invoice_partner.id,
            'invoice_origin': f"Job Card: {self.job_card_id.name}",
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
            'job_card_id': self.job_card_id.id,
        }
        invoice = self.env['account.move'].create(invoice_vals)

        # Create and validate delivery order if stock moves exist
        if stock_moves:
            # Get picking type for current company
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('company_id', '=', self.job_card_id.company_id.id)
            ], limit=1)

            if not picking_type:
                raise UserError("No Delivery Order picking type found for the job card's company.")

            picking = self.env['stock.picking'].create({
                'partner_id': self.job_card_id.partner_id.id,
                'picking_type_id': picking_type.id,
                'location_id': stock_location.id,
                'location_dest_id': self.job_card_id.partner_id.property_stock_customer.id,
                'origin': f"Job Card: {self.job_card_id.name}",
                'move_ids_without_package': stock_moves,
            })
            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()

        # Create Vendor Bill if Sublet lines exist
        if sublet_vendor_bill_lines:
            vendor_bill_vals = {
                'partner_id': self.job_card_id.partner_id.id if self.job_card_id.partner_id else False,
                'invoice_origin': f"Sublet for Job Card: {self.job_card_id.name}",
                'move_type': 'in_invoice',
                'invoice_line_ids': sublet_vendor_bill_lines,
                'job_card_id': self.job_card_id.id,
            }
            vendor_bill = self.env['account.move'].create(vendor_bill_vals)

        # Mark job detail lines as invoiced
        for wizard_line in selected_lines:
            if wizard_line.line_id:
                wizard_line.line_id.write({
                    'invoiced': True,
                    'line_state': 'x_state',
                })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'target': 'current',
        }

    def action_select_all(self):
        # Select all non-readonly lines
        for line in self.line_ids:
            if not line.readonly:
                line.selected = True


        return {
            'type': 'ir.actions.act_window',
            'res_model': 'job.card.invoice.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }


class JobCardInvoiceWizardLine(models.TransientModel):
    _name = 'job.card.invoice.wizard.line'
    _description = 'Job Card Invoice Wizard Line'

    wizard_id = fields.Many2one('job.card.invoice.wizard', string="Wizard")
    line_id = fields.Many2one('job.card.line', string="Original Line")
    description = fields.Text(string="Description")
    price_unit = fields.Float(string="Price")
    quantity = fields.Float(string="Qty")
    discount = fields.Float(string="Discount")
    total = fields.Float(string="Total")
    department = fields.Selection([
        ('labour', 'Labour'),
        ('parts', 'Parts'),
        ('material', 'Material'),
        ('lubricant', 'Lubricant'),
        ('sublets', 'Sublets'),
        ('paint_material', 'Paint Material'),
        ('tyre', 'Tyre'),
    ], string="Department")
    product_template_id = fields.Many2one('product.template', string="Product")

    selected = fields.Boolean(string="Select")
    readonly = fields.Boolean(string="Already Invoiced", default=False)


class JobCardInvoiceWizardServiceLine(models.TransientModel):
    _name = 'job.card.invoice.wizard.service.line'
    _description = 'Job Card Service Line for Invoice Wizard'

    wizard_id = fields.Many2one('job.card.invoice.wizard', string="Wizard")
    service_line_id = fields.Many2one('job.card.service.line', string="Service Line")
    menu_service = fields.Selection([
        ('regular', 'Regular'),
        ('medium', 'Medium'),
        ('major', 'Major'),
        ('loop_services', 'Loop Services'),
    ], string="Menu Service")
    service_amount = fields.Float(string="Service Amount")
    product_template_ids = fields.Many2many('product.template', string="Products")

    service_selected = fields.Boolean(string="Select", default=False)
