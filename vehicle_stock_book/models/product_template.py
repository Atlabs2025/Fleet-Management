import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
    # vehicle_id = fields.Many2one('fleet.vehicle', string="Make")
    # register_no = fields.Many2one('fleet.vehicle', string="Plate No.")
    register_no = fields.Char(string="Plate No.")
    # model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    model_id = fields.Char(string="Model")
    vin_sn = fields.Char(string="Chassis Number")
    engine_no = fields.Char(string="Engine Number")
    # vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string="Make")
    vehicle_make_id = fields.Char(string="Make")
    variant = fields.Selection([
        ('se', 'SE'),
        ('xle', 'XLE'),
        ('gt', 'GT')
    ], string="Variant")
    specification = fields.Selection([
        ('gcc_country', 'GCC'),
        ('un_states', 'US'),
        ('japan', 'Japan')
    ], string="Specification")
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('phev', 'PHEV'),
        ('ev', 'EV'),
    ], string="Fuel Type")
    date_of_purchase = fields.Date(string="Date Of Purchase")
    year_list = [(str(y), str(y)) for y in range(1997, datetime.datetime.now().year + 1)]
    year_of_manufacturing = fields.Selection(selection=year_list, string='Year Model')
    date_of_manufacturing = fields.Date(string="Date Of Manufacturing")
    country_of_origin_id = fields.Many2one(
        'res.country',
        string='Country of Origin'
    )
    number_of_cylinders = fields.Integer(string='Number of Cylinders')
    order_date = fields.Date(string="Order Date", default=fields.Date.context_today)

    purchase_price = fields.Float(string="Purchase Price")
    landing_price = fields.Float(string="Landing Price")
    sales_cost = fields.Float(string="Margin Value")
    refurb_cost = fields.Float(string="Refurb Cost")
    additional_expenses = fields.Float(string="Additional Expenses")
    sales_price = fields.Float(string="Selling Price")
    offer_price = fields.Float(string="Offer Price")
    loan_price = fields.Float(string="Loan")
    vat_applicable = fields.Selection(
        selection=[
            ('yes', 'YES'),
            ('no', 'NO')
        ],
        string='VAT Applicable'
    )

    bought_from = fields.Char(string="Bought From")
    bought_by = fields.Char(string="Bought By")
    consignment = fields.Char(string="Consignment")
    consignment_location = fields.Char(string="Consignment Location")
    hours_spent = fields.Float(string="Hours Spent")
    service_history = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('not_available', 'Not Available')
        ],
        string='Service History'
    )
    odoo_meeter = fields.Float(string="Odoo Meeter")
    colour_type = fields.Char(string='Body Colour')
    trim_colour = fields.Char(string="Trim Colour")
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

    image_ids = fields.One2many('product.template.image', 'product_tmpl_id', string="Images")
    image = fields.Char(string="Image")
    product_code = fields.Char(string="Product Code", readonly=True, copy=False)
    engine_capacity = fields.Char(string="Engine Capacity")
    transmission = fields.Selection(
        selection=[
            ('manual', 'Manual'),
            ('automatic', 'Automatic'),
            ('cvt', 'CVT'),
            ('dct', 'DCT'),
        ],
        string='Transmission'
    )
    drivetrain = fields.Selection(
        selection=[
            ('fwd', 'FWD'),
            ('rwd', 'RWD'),
            ('awd', 'AWD'),
            ('4wd', '4WD'),
        ],
        string='Drivetrain'
    )
    number_of_doors = fields.Integer(string='No.of Doors')
    number_of_seats = fields.Integer(string='No.of Seats')
    ownership_status = fields.Selection(
        selection=[
            ('new', 'New'),
            ('used', 'Used'),
            ('certified', 'Certified'),
            ('pre_owned', 'Pre-Owned'),
        ],
        string='Ownership Status')
    rta_passing = fields.Char(string="RTA Passing")


    accident_history = fields.Boolean(string="Accident History")
    accident_details = fields.Text(string="Accident Details")

    interior_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string="Interior Condition")

    exterior_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string="Exterior Condition")

    tyre_condition = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
    ], string="Tyre Condition")
    tyre_life_percent = fields.Integer(string="Tyre Life Left (%)")

    no_of_keys = fields.Integer(string="Number of Keys")


class ProductTemplateImage(models.Model):
    _name = 'product.template.image'
    _description = 'Vehicle Image'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade')
    image = fields.Binary(string="Image", attachment=True)


