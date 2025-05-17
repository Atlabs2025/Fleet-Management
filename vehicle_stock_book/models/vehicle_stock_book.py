from odoo import models, fields, api
import datetime



class VehicleStockBook(models.Model):
    _name = 'vehicle.stock.book'
    _description = 'Vehicle Stock Book'

    # sequence_number = fields.Char(string="Sequence Number", readonly=True, copy=False)
    name = fields.Char(string="Vehicle Name", required=True)
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
    vehicle_id = fields.Many2one('fleet.vehicle', string="Make")
    model_id = fields.Many2one('fleet.vehicle.model', string="Model")
    vin = fields.Char(string="VIN")
    engine_no = fields.Char(string="Engine Number")
    plate_no = fields.Char(string="Plate Number")
    brand_id = fields.Many2one('fleet.vehicle.model.brand', string="Brand")
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
    year_of_manufacturing = fields.Selection(
        selection=[(str(y), str(y)) for y in range(1997, datetime.datetime.now().year + 1)],
        string='Year Model'
    )
    date_of_manufacturing = fields.Date(string="Date Of Manufacturing")
    country_of_origin_id = fields.Many2one('res.country', string='Country of Origin')
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
    service_history = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available')
    ], string='Service History')

    odoo_meeter = fields.Float(string="Odoo Meeter")
    colour_type = fields.Selection([
        ('interior', 'Interior'),
        ('exterior', 'Exterior')
    ], string='Body Colour')
    trim_colour = fields.Char(string="Trim Colour")
    interior_type = fields.Selection([
        ('leather', 'Leather'),
        ('fabric', 'Fabric')
    ], string='Interior Type')

    additional_features = fields.Text(string='Additional Features')
    send_to_id = fields.Many2one('res.partner', string='Send To')

    image_ids = fields.One2many('vehicle.stock.image', 'stock_book_id', string="Images")
    product_code = fields.Char(string="Product Code", readonly=True, copy=False)



    @api.model
    def create(self, vals):
        if not vals.get('product_code') and vals.get('vin'):
            vals['product_code'] = f"VEH-{vals['vin'][:8].upper()}"

        vehicle = super(VehicleStockBook, self).create(vals)

        # Automatically create a product in the "Cars" category
        product_category = self.env['product.category'].search([('name', '=', 'Cars')], limit=1)
        if not product_category:
            product_category = self.env['product.category'].create({'name': 'Cars'})

        self.env['product.template'].create({
            'name': vehicle.name,
            'default_code': vehicle.product_code,
            # 'type': 'product',
            'categ_id': product_category.id,
            'list_price': vehicle.sales_price,
            'standard_price': vehicle.landing_price,
            'description_sale': f"{vehicle.vehicle_type} - {vehicle.model_id.name or ''} ({vehicle.year_of_manufacturing})",
        })

        return vehicle






class VehicleStockImage(models.Model):
    _name = 'vehicle.stock.image'
    _description = 'Vehicle Image'

    stock_book_id = fields.Many2one('vehicle.stock.book', string="Stock Book", ondelete='cascade')
    image = fields.Binary(string="Image", attachment=True)






# from odoo import models, fields, api
# import datetime
#
#
# class VehicleStockBook(models.Model):
#     _name = 'vehicle.stock.book'
#     _description = 'Vehicle Stock Book'
#
#     name = fields.Char(string="Vehicle Name", required=True)
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
#     date_of_purchase = fields.Date(string="Date Of Purchase")
#     year_of_manufacturing = fields.Selection(
#         selection=[(str(y), str(y)) for y in range(1997, datetime.datetime.now().year + 1)],
#         string='Year Model'
#     )
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
#     odoo_meeter = fields.Float(string="Odometer")
#     colour_type = fields.Selection([
#         ('interior', 'Interior'),
#         ('exterior', 'Exterior')
#     ], string='Body Colour')
#     trim_colour = fields.Char(string="Trim Colour")
#     interior_type = fields.Selection([
#         ('leather', 'Leather'),
#         ('fabric', 'Fabric')
#     ], string='Interior Type')
#     additional_features = fields.Text(string='Additional Features')
#     send_to_id = fields.Many2one('res.partner', string='Send To')
#
#     image_ids = fields.One2many('vehicle.stock.image', 'stock_book_id', string="Images")
#     product_code = fields.Char(string="Product Code", readonly=True, copy=False)
#
#     @api.model
#     def create(self, vals):
#         if not vals.get('product_code') and vals.get('name'):
#             base_name = vals['name'].replace(" ", "")
#             existing_codes = self.search([('name', '=', vals['name'])], order='id desc')
#             count = len(existing_codes) + 1
#             vals['product_code'] = f"{base_name}-{str(count).zfill(3)}"
#
#         return super(VehicleStockBook, self).create(vals)
#
#
# class VehicleStockImage(models.Model):
#     _name = 'vehicle.stock.image'
#     _description = 'Vehicle Image'
#
#     stock_book_id = fields.Many2one('vehicle.stock.book', string="Stock Book", ondelete='cascade')
#     image = fields.Binary(string="Image", attachment=True)
