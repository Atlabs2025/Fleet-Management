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









# class JobCardPLWizard(models.TransientModel):
#     _name = 'job.card.pl.wizard'
#     _description = 'Job Card P&L Wizard'
#
#     date_from = fields.Date(string="From Date", required=True, default=lambda self: date.today().replace(day=1))
#     date_to = fields.Date(string="To Date", required=True, default=lambda self: date.today())
#
#     def action_print_xlsx(self):
#         data = {
#             'date_from': self.date_from.strftime('%Y-%m-%d'),
#             'date_to': self.date_to.strftime('%Y-%m-%d')
#         }
#         return self.env.ref('atlbs_job_card.job_card_pl_xlsx_report').report_action(self, data=data)




# class JobCardPLXlsx(models.AbstractModel):
#     _name = 'report.atlbs_job_card.job_card_pl_xlsx'
#     _inherit = 'report.report_xlsx.abstract'
#     _description = 'Job Card P&L XLSX Report'
#
#     def generate_xlsx_report(self, workbook, data, partners):
#         sheet = workbook.add_worksheet("Job Card P&L")
#
#         # Formats
#         bold = workbook.add_format({'bold': True})
#         date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
#         money_format = workbook.add_format({'num_format': '#,##0.00'})
#
#         # Title
#         sheet.merge_range('A1:O1', "Job Card P&L", bold)
#         period = f"Period: {data['date_from']} - {data['date_to']}"
#         sheet.write('A2', period, bold)
#
#         # Headers
#         headers = [
#             "Date", "Job Card", "Estimate #", "Invoice #", "Vehicle /Plate",
#             "VIN Number", "Labor", "Parts", "Material", "SubletCost", "Total",
#             "Labor Cost", "Parts Cost", "Material Cost", "Sublet Cost", "Total"
#         ]
#         sheet.write_row('A4', headers, bold)
#
#         # Fetch data
#         domain = [
#             ('created_datetime', '>=', data['date_from']),
#             ('created_datetime', '<=', data['date_to'])
#         ]
#         job_cards = self.env['job.card.management'].search(domain)
#
#         row = 4
#         for jc in job_cards:
#             sheet.write_datetime(row, 0, jc.created_datetime, date_format)
#             sheet.write(row, 1, jc.name or '')
#             sheet.write(row, 2, jc.estimate_id.name or '')
#             sheet.write(row, 3, '')  # Invoice #
#             plate = f"{jc.register_no.model_id.name}/{jc.register_no.license_plate}"
#             sheet.write(row, 4, plate)
#             sheet.write(row, 5, jc.vin_sn or '')
#
#             # Revenue columns
#             sheet.write_number(row, 6, jc.total_labour or 0, money_format)
#             sheet.write_number(row, 7, jc.total_parts or 0, money_format)
#             sheet.write_number(row, 8, jc.total_material or 0, money_format)
#             sheet.write_number(row, 9, jc.total_sublets or 0, money_format)
#             sheet.write_number(row, 10, jc.total_amount or 0, money_format)
#
#             # Expense columns — adjust to your actual fields
#             sheet.write_number(row, 11, 0, money_format)  # Labor cost
#             sheet.write_number(row, 12, 0, money_format)  # Parts cost
#             sheet.write_number(row, 13, 0, money_format)  # Material cost
#             sheet.write_number(row, 14, 0, money_format)  # Sublet cost
#             sheet.write_number(row, 15, 0, money_format)  # Total expense
#
#             row += 1
#
#
#
#
#
