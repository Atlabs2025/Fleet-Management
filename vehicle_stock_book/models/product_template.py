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
    register_no = fields.Many2one('fleet.vehicle', string="Plate No.")
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    vin_sn = fields.Char(string="Chassis Number")
    engine_no = fields.Char(string="Engine Number")
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string="Make")
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
    ], string="Fuel")
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

    landing_price = fields.Float(string="Landing Price")
    sales_cost = fields.Float(string="Margin Value")
    refurb_cost = fields.Float(string="Refurb Cost")
    additional_expenses = fields.Float(string="Additional Expenses")
    sales_price = fields.Float(string="Sales Price")

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
    colour_type = fields.Selection(
        selection=[
            ('interior', 'Interior'),
            ('Exterior', 'Exterior')
        ],
        string=' Body Colour'
    )
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

    # @api.model
    # def create(self, vals):
    #     # If product_code is not already set
    #     if not vals.get('product_code') and vals.get('name'):
    #         base_name = vals['name'].replace(" ", "")
    #         # Find existing products with similar names
    #         existing_codes = self.search([('name', '=', vals['name'])], order='id desc')
    #         count = 1
    #         for record in existing_codes:
    #             if record.product_code and record.product_code.startswith(base_name):
    #                 # Extract last 3 digits and increment
    #                 suffix = record.product_code.replace(base_name + '-', '')
    #                 if suffix.isdigit():
    #                     count = int(suffix) + 1
    #                     break
    #         vals['product_code'] = f"{base_name}-{str(count).zfill(3)}"
    #
    #     return super(ProductTemplate, self).create(vals)


class ProductTemplateImage(models.Model):
    _name = 'product.template.image'
    _description = 'Vehicle Image'

    product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade')
    image = fields.Binary(string="Image", attachment=True)





















# import datetime
#
# from odoo import models, fields, api
# from odoo.exceptions import UserError
# from odoo import models, fields, api
# import datetime
#
#
#
#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     product_code = fields.Char(string="Product Code", readonly=True, copy=False)
#     vehicle_type = fields.Selection([
#         ('hatchback', 'Hatchback'),
#         ('sedan', 'Sedan'),
#         ('suv', 'SUV'),
#         ('truck', 'Truck'),
#         ('cross_over', 'Cross Over'),
#         ('coupe', 'Coupe'),
#         ('convertable', 'Convertable'),
#         ('luxury', 'Luxury'),
#         ('super_luxury', 'Super Luxury')
#     ], string="Vehicle Type")
#
#     vehicle_id = fields.Many2one('fleet.vehicle', string="Make")
#     model_id = fields.Many2one('fleet.vehicle.model', string="Model")
#     vin = fields.Char(string="VIN")
#     engine_no = fields.Char(string="Engine Number")
#     plate_no = fields.Char(string="Plate Number")
#     brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand")
#     specification = fields.Selection([
#         ('gcc_country', 'GCC'),
#         ('un_states', 'US'),
#         ('japan', 'Japan')
#     ], string="Specification")
#     fuel_type = fields.Selection([
#         ('petrol', 'Petrol'),
#         ('diesel', 'Diesel'),
#         ('hybrid', 'Hybrid'),
#         ('phev', 'PHEV'),
#         ('ev', 'EV'),
#     ], string="Fuel Type")
#
#     date_of_purchase = fields.Date(string="Date Of Purchase")
#     year_list = [(str(y), str(y)) for y in range(1997, datetime.datetime.now().year + 1)]
#     year_of_manufacturing = fields.Selection(selection=year_list, string='Year Model')
#     date_of_manufacturing = fields.Date(string="Date Of Manufacturing")
#     country_of_origin_id = fields.Many2one('res.country', string='Country of Origin')
#     number_of_cylinders = fields.Integer(string='Number of Cylinders')
#     order_date = fields.Date(string="Order Date", default=fields.Date.context_today)
#
#     landing_price = fields.Float(string="Landing Price")
#     sales_cost = fields.Float(string="Margin Value")
#     refurb_cost = fields.Float(string="Refurb Cost")
#     additional_expenses = fields.Float(string="Additional Expenses")
#     sales_price = fields.Float(string="Sales Price")
#
#     bought_from = fields.Char(string="Bought From")
#     bought_by = fields.Char(string="Bought By")
#     consignment = fields.Char(string="Consignment")
#     consignment_location = fields.Char(string="Consignment Location")
#     hours_spent = fields.Float(string="Hours Spent")
#     service_history = fields.Selection([
#         ('available', 'Available'),
#         ('not_available', 'Not Available')
#     ], string='Service History')
#
#     # odoo_meter = fields.Float(string="Odoo Meter")
#     colour_type = fields.Selection([
#         ('interior', 'Interior'),
#         ('exterior', 'Exterior')
#     ], string='Body Colour')
#     trim_colour = fields.Char(string="Trim Colour")
#     interior_type = fields.Selection([
#         ('leather', 'Leather'),
#         ('fabric', 'Fabric')
#     ], string='Interior Type')
#
#     additional_features = fields.Text(string='Additional Features')
#     send_to_id = fields.Many2one('res.partner', string='Send To')
#
#     @api.model
#     def create(self, vals):
#         # Automatically assign Vehicles category if vehicle fields are present
#         vehicle_cat = self.env['product.category'].search([('name', '=', 'Vehicles')], limit=1)
#         if not vehicle_cat:
#             vehicle_cat = self.env['product.category'].create({'name': 'Vehicles'})
#
#         # If any key vehicle field is present, assign category
#         vehicle_fields = ['vin', 'vehicle_type', 'model_id', 'engine_no']
#         if any(vals.get(f) for f in vehicle_fields):
#             vals['categ_id'] = vehicle_cat.id
#
#         return super(ProductTemplate, self).create(vals)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#



# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     vehicle_type = fields.Selection([
#         ('hatchback', 'Hatchback'),
#         ('sedan', 'Sedan'),
#         ('suv', 'SUV'),
#         ('truck', 'Truck'),
#         ('cross_over', 'Cross Over'),
#         ('coupe', 'Coupe'),
#         ('convertable', 'Convertable'),
#         ('luxury', 'Luxury'),
#         ('super_luxury', 'Super Luxury')
#     ], string="Vehicle Type")
#     vehicle_id = fields.Many2one('fleet.vehicle', string="Make")
#     model_id = fields.Many2one('fleet.vehicle.model', string="Model")
#     vin = fields.Char(string="VIN")
#     engine_no = fields.Char(string="Engine Number")
#     plate_no =  fields.Char(string="Plate Number")
#     brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand")
#     specification = fields.Selection([
#         ('gcc_country', 'GCC'),
#         ('un_states', 'US'),
#         ('japan', 'Japan')
#     ], string="Specification")
#     fuel_type = fields.Selection([
#         ('petrol', 'Petrol'),
#         ('diesel', 'Diesel'),
#         ('hybrid', 'Hybrid'),
#         ('phev', 'PHEV'),
#         ('ev', 'EV'),
#     ], string="Fuel")
#     date_of_purchase = fields.Date(string="Date Of Purchase")
#     year_list = [(str(y), str(y)) for y in range(1997, datetime.datetime.now().year + 1)]
#     year_of_manufacturing = fields.Selection(selection=year_list, string='Year Model')
#     date_of_manufacturing = fields.Date(string="Date Of Manufacturing")
#     country_of_origin_id = fields.Many2one(
#         'res.country',
#         string='Country of Origin'
#     )
#     number_of_cylinders = fields.Integer(string='Number of Cylinders')
#     order_date = fields.Date(string="Order Date", default=fields.Date.context_today)
#
#     landing_price = fields.Float(string="Landing Price")
#     sales_cost = fields.Float(string="Margin Value")
#     refurb_cost = fields.Float(string="Refurb Cost")
#     additional_expenses = fields.Float(string="Additional Expenses")
#     sales_price = fields.Float(string="Sales Price")
#
#     bought_from = fields.Char(string="Bought From")
#     bought_by = fields.Char(string="Bought By")
#     consignment = fields.Char(string="Consignment")
#     consignment_location = fields.Char(string="Consignment Location")
#     hours_spent = fields.Float(string="Hours Spent")
#     service_history = fields.Selection(
#         selection=[
#             ('available', 'Available'),
#             ('not_available', 'Not Available')
#         ],
#         string='Service History'
#     )
#     odoo_meeter = fields.Float(string="Odoo Meeter")
#     colour_type = fields.Selection(
#         selection=[
#             ('interior', 'Interior'),
#             ('Exterior', 'Exterior')
#         ],
#         string=' Body Colour'
#     )
#     trim_colour = fields.Char(string="Trim Colour")
#     interior_type = fields.Selection(
#         selection=[
#             ('leather', 'Leather'),
#             ('fabric', 'Fabric')
#         ],
#         string='Interior Type'
#     )
#
#     additional_features = fields.Text(string='Additional Features')
#     send_to_id = fields.Many2one(
#         'res.partner',
#         string='Send To'
#     )
#
#     image_ids = fields.One2many('product.template.image', 'product_tmpl_id', string="Images")
#     image = fields.Char(string="Image")
#     product_code = fields.Char(string="Product Code", readonly=True, copy=False)
#
#     @api.model
#     def create(self, vals):
#         # If product_code is not already set
#         if not vals.get('product_code') and vals.get('name'):
#             base_name = vals['name'].replace(" ", "")
#             # Find existing products with similar names
#             existing_codes = self.search([('name', '=', vals['name'])], order='id desc')
#             count = 1
#             for record in existing_codes:
#                 if record.product_code and record.product_code.startswith(base_name):
#                     # Extract last 3 digits and increment
#                     suffix = record.product_code.replace(base_name + '-', '')
#                     if suffix.isdigit():
#                         count = int(suffix) + 1
#                         break
#             vals['product_code'] = f"{base_name}-{str(count).zfill(3)}"
#
#         return super(ProductTemplate, self).create(vals)
#
#
# class ProductTemplateImage(models.Model):
#     _name = 'product.template.image'
#     _description = 'Vehicle Image'
#
#     product_tmpl_id = fields.Many2one('product.template', string="Product Template", ondelete='cascade')
#     image = fields.Binary(string="Image", attachment=True)
#
