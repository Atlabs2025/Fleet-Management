# -*- coding: utf-8 -*-
{
    'name': 'Job Card',
    'version': '18.0.1.0.0',
    'category': 'Job Card Management',
    'summary': 'Atlabs Job Card Management',
    'description': 'job card',
    'depends': [
        'contacts', 'fleet','product','stock','material_purchase_requisitions','hr','purchase','stock'
    ],
'data': [
    'security/ir.model.access.csv',
    'report/report_action.xml',
    'report/job_card_template.xml',
    'report/estimate_template.xml',
    'report/tax_invoice_template.xml',
    'views/data.xml',
    'views/job_card_management.xml',
    'views/fleet_vehicle.xml',
    'views/res_partner.xml',
    'views/product_template.xml',
    'views/account_move.xml',
    'wizard/job_card_invoice_wizard.xml',

],
    'assets': {},
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}