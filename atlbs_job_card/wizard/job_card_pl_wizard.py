from odoo import models, fields
from datetime import date
import io
import base64
import xlsxwriter
from odoo import models, fields, api

class JobCardPLWizard(models.TransientModel):
    _name = 'job.card.pl.wizard'
    _description = 'Job Card P&L Report Wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    file_data = fields.Binary(string='File')
    file_name = fields.Char(string='File Name')

    def action_print_xlsx(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Job Card P&L")


        sheet.write(0, 0, "Period:")
        sheet.write(0, 1, f"{self.date_from} - {self.date_to}")


        headers = [
            "Date", "Job Card", "Estimate #", "Invoice #", "Vehicle / Plate", "VIN Number",
            "Labor", "Parts", "Material", "SubletCost", "Total",
            "Labor Cost", "Parts Cost", "Material Cost", "Sublet Cost", "Total Expense"
        ]
        for col, header in enumerate(headers):
            sheet.write(2, col, header)

        job_cards = self.env['job.card.management'].search([
            ('created_datetime', '>=', self.date_from),
            ('created_datetime', '<=', self.date_to),
        ])

        row = 3
        for jc in job_cards:
            total_revenue = jc.total_labour + jc.total_parts + jc.total_material + jc.total_sublets
            total_expense = 0.0

            sheet.write(row, 0, jc.created_datetime.strftime('%d/%m/%Y') if jc.created_datetime else '')
            sheet.write(row, 1, jc.name or '')
            sheet.write(row, 2, jc.estimate_number or '')
            sheet.write(row, 3, '')
            sheet.write(row, 4, f"{jc.register_no.name if jc.register_no else ''}")
            sheet.write(row, 5, jc.vin_sn or '')

            sheet.write(row, 6, jc.total_labour)
            sheet.write(row, 7, jc.total_parts)
            sheet.write(row, 8, jc.total_material)
            sheet.write(row, 9, jc.total_sublets)
            sheet.write(row, 10, total_revenue)


            sheet.write(row, 11, 0)
            sheet.write(row, 12, 0)
            sheet.write(row, 13, 0)
            sheet.write(row, 14, 0)
            sheet.write(row, 15, total_expense)

            row += 1

        workbook.close()
        output.seek(0)


        self.write({
            'file_data': base64.b64encode(output.read()),
            'file_name': f"Job_Card_PL_{self.date_from}_to_{self.date_to}.xlsx",
        })


        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self._name}/{self.id}/file_data/{self.file_name}?download=true",
            "target": "new",
        }


    def action_view_report(self):
        self.ensure_one()
        # Remove old lines (for fresh calculation)
        self.env['job.card.pl.line'].search([('wizard_id', '=', self.id)]).unlink()

        job_cards = self.env['job.card.management'].search([
            ('created_datetime', '>=', self.date_from),
            ('created_datetime', '<=', self.date_to),
        ])

        for jc in job_cards:
            total_revenue = jc.total_labour + jc.total_parts + jc.total_material + jc.total_sublets
            total_expense = 0.0  # replace with real expense calc

            self.env['job.card.pl.line'].create({
                'wizard_id': self.id,
                'date': jc.created_datetime,
                'job_card': jc.name,
                'estimate': jc.estimate_number,
                'invoice': '',  # if available
                'vehicle': jc.register_no.name if jc.register_no else '',
                'vin': jc.vin_sn,
                'labor': jc.total_labour,
                'parts': jc.total_parts,
                'material': jc.total_material,
                'sublet': jc.total_sublets,
                'total': total_revenue,
                'labor_cost': 0,
                'parts_cost': 0,
                'material_cost': 0,
                'sublet_cost': 0,
                'total_expense': total_expense,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Job Card P&L Report',
            'res_model': 'job.card.pl.line',
            'view_mode': 'list',
            'domain': [('wizard_id', '=', self.id)],
            'target': 'current',
        }






# for view the button function given above
class JobCardPLLine(models.TransientModel):
    _name = 'job.card.pl.line'
    _description = 'Job Card P&L Line'
    _order = 'date'

    wizard_id = fields.Many2one('job.card.pl.wizard', ondelete='cascade')
    date = fields.Date("Date")
    job_card = fields.Char("Job Card")
    estimate = fields.Char("Estimate #")
    invoice = fields.Char("Invoice #")
    vehicle = fields.Char("Vehicle / Plate")
    vin = fields.Char("VIN Number")
    labor = fields.Float("Labor")
    parts = fields.Float("Parts")
    material = fields.Float("Material")
    sublet = fields.Float("Sublet Cost")
    total = fields.Float("Total")
    labor_cost = fields.Float("Labor Cost")
    parts_cost = fields.Float("Parts Cost")
    material_cost = fields.Float("Material Cost")
    sublet_cost = fields.Float("Sublet Cost")
    total_expense = fields.Float("Total Expense")


