# report/report_tax_invoice.py
from odoo import models, api
from collections import defaultdict

class ReportTaxInvoice(models.AbstractModel):
    _name = 'report.atlbs_job_vcard.report_tax_invoice'
    _description = 'Grouped Tax Invoice Report by Department'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        DEPT_LABELS = {
            'labour': 'Labour Charges',
            'parts': 'Spare Parts',
            'material': 'Materials',
            'lubricant': 'Lubricants',
            'sublets': 'Sublet Services',
            'paint_material': 'Paint & Materials',
            'tyre': 'Tyre Services',
        }

        for doc in docs:
            # Group lines by department
            dept_lines = defaultdict(list)
            for line in doc.invoice_line_ids:
                if line.department:
                    dept_lines[line.department].append(line)

            doc.dept_line_groups = dept_lines

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'department_labels': DEPT_LABELS,
        }
