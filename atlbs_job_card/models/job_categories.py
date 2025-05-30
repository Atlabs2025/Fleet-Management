from odoo import models, fields, api



class JobCategories(models.Model):
    _name = 'job.categories'
    _description = 'Job Categories'

    name = fields.Char(string="Name", required=True)