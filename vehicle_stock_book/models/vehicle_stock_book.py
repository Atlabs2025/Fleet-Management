import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError


class VehicleStockBook(models.Model):
    _name = 'vehicle.stock.book'
    _description = 'Vehicle Stock Book'


    partner_id = fields.Many2one('res.partner',string='Customer', required=1)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Make")
    vin = fields.Char(string="VIN")
    brand = fields.Char(string="Brand")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand")
    model = fields.Char(string="Model")
    quantity = fields.Integer(string="Quantity")
    image = fields.Char(string="image")
    name = fields.Char(string="Name")
    chasis_no = fields.Char(string="Chassis Number")
    engine_no = fields.Char(string="Engine Number")
    image_ids = fields.One2many('vehicle.stock.book.image', 'stock_book_id')
    order_date = fields.Date(string="Order Date", default=fields.Date.context_today)
    company_id = fields.Many2one('res.company',string="Company")
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    hours_spent = fields.Float(string="Hours Spent")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('quotation', 'Quotation'),
        ('invoice', 'Invoiced'),
    ], string='Status', default='draft', tracking=True)

    project_id = fields.Many2one('project.project', string="Project")
    assigning_date = fields.Date(string="Assigning Date")
    vehicle_in_date = fields.Date(string="Vehicle In")
    out_date = fields.Date(string="Out Date")
    odometer = fields.Float(string="Odometer Reading")
    repair_category_id = fields.Many2one('repair.category', string="Repair Category")
    payment_type = fields.Selection([
        ('free', 'Free'),
        ('paid', 'Paid')
    ], string="Payment Type")
    gears = fields.Integer(string="Gears")
    year = fields.Char(string="Year")
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric')
    ], string="Fuel Type")
    currency_id = fields.Many2one('res.currency', string="Currency")
    deadline = fields.Date(string="Deadline")
    tag_ids = fields.Many2many('project.tags', string="Tags")
    vehicle_type = fields.Selection([
        ('hatchback', 'Hatchback'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('truck', 'Truck'),
        ('cross_over', 'Cross Over'),
        ('coupe', 'Coupe'),
        ('convertable', 'Convertable'),
        ('luxury', 'Luxury'),
        ('super_luxury', 'Super Luxury')
    ], string="Vehicle Type")
    varient = fields.Char(string="Varient")
    date_of_purchase = fields.Date(string="Date Of Purchase")
    year_list = [(str(y), str(y)) for y in range(1980, datetime.datetime.now().year + 1)]
    year_of_manufacturing = fields.Selection(selection=year_list,string='Year Model'
    )
    date_of_manufacturing = fields.Date(string="Date Of Manufacturing")
    country_of_origin_id = fields.Many2one(
        'res.country',
        string='Country of Origin'
    )
    specification = fields.Char(string="Specification")
    number_of_cylinders = fields.Integer(string='Number of Cylinders')
    fuel_type = fields.Selection([
        ('cylinders', 'Cylinders'),
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('ev', 'EV'),
    ], string="Fuel")
    bought_from = fields.Char(string="Bought From")
    bought_by = fields.Char(string="Bought By")
    consignment = fields.Char(string="Consignment")
    consignment_location = fields.Char(string="Consignment Location")
    service_history = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('not_available', 'Not Available')
        ],
        string='Service History'
    )
    present_km = fields.Float(string="Odoo Meeter")
    colour_type = fields.Selection(
        selection=[
            ('interior', 'Interior'),
            ('Exterior', 'Exterior')
        ],
        string=' Body Colour'
    )
    interior_type = fields.Selection(
        selection=[
            ('leather', 'Leather'),
            ('fabric', 'Fabric')
        ],
        string='Interior Type'
    )
    additional_features = fields.Text(string='Additional Features')
    send_to_id = fields.Many2one(
        'res.partner',
        string='Send To'
    )

    landing_price = fields.Float(string="Landing Price")
    sales_cost = fields.Float(string="Margin Value")
    refurb_cost = fields.Float(string="Refurb Cost")
    additional_expenses = fields.Float(string="Additional Expenses")
    sales_price = fields.Float(string="Sales Price")
    stock_line_ids = fields.One2many('vehicle.stock.line', 'stock_book_id', string="Stock Lines")
    # sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    invoice_id = fields.Many2one('account.move', string="Invoice")  # Link to the invoice
    invoice_id = fields.Many2one('account.move', string="Invoice")
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_invoice_count')

    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = 1 if record.invoice_id else 0

    @api.model
    def create(self, vals):
        vals['state'] = 'quotation'
        return super(VehicleStockBook, self).create(vals)

    def write(self, vals):
        if not self.env.context.get('skip_state_change') and 'state' not in vals:
            vals['state'] = 'quotation'
        return super(VehicleStockBook, self).write(vals)

    def action_confirm_stock(self):
        for record in self:
            if not record.partner_id:
                raise UserError("Please select a Customer before confirming.")

            if not record.stock_line_ids:
                raise UserError("Please add at least one Stock Line.")

            invoice_lines = []
            for line in record.stock_line_ids:
                invoice_lines.append((0, 0, {
                    'name': line.description or 'Stock Line',
                    'quantity': line.quantity,
                    'price_unit': line.price,
                    # 'account_id': self.env['account.account'].search([('user_type_id.type', '=', 'income')], limit=1).id
                }))

            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': record.partner_id.id,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': invoice_lines,
            })

            record.invoice_id = invoice.id
            record.state = 'invoice'

    # def action_confirm_stock(self):
    #     for record in self:
    #         if not record.partner_id:
    #             raise UserError("Please select a Customer before confirming.")
    #
    #         order_lines = []
    #         for line in record.stock_line_ids:
    #             if not line.product_id:
    #                 raise UserError("Each line must have a Product selected.")
    #             order_lines.append((0, 0, {
    #                 'product_id': line.product_id.id,
    #                 'name': line.description or line.product_id.name,
    #                 'product_uom_qty': line.quantity,
    #                 'price_unit': line.price,
    #             }))
    #
    #         sale_order = self.env['sale.order'].create({
    #             'partner_id': record.partner_id.id,
    #             'order_line': order_lines,
    #         })
    #
    #         # Confirm the sale order immediately
    #         sale_order.action_confirm()
    #
    #         # Store the sale order reference
    #         record.sale_order_id = sale_order.id
    #
    #         # Update state if needed
    #         record.state = 'sale'







    def action_create_estimate(self):
        print('defffffffff')


class VehicleStockBookImage(models.Model):
    _name = 'vehicle.stock.book.image'
    _description = 'Vehicle Stock Book Images'

    stock_book_id = fields.Many2one('vehicle.stock.book', string="Stock Book")
    image = fields.Image(string="Image")
    name = fields.Char(string="Description")



class VehicleStockLine(models.Model):
    _name = 'vehicle.stock.line'
    _description = 'Vehicle Stock Line'

    stock_book_id = fields.Many2one('vehicle.stock.book', string="Stock Book", ondelete="cascade")
    # product_id = fields.Many2one('product.product', string='Product', required=True)
    description= fields.Char(string="Description")
    quantity = fields.Float(string="Quantity")
    price = fields.Float(string="Price")
    tax = fields.Float(string="Tax (%)")
    total = fields.Float(string="Total", compute="_compute_total", store=True)

    @api.depends('quantity', 'price', 'tax')
    def _compute_total(self):
        for line in self:
            subtotal = line.quantity * line.price
            tax_amount = subtotal * (line.tax / 100)
            line.total = subtotal + tax_amount
