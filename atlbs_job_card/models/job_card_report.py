import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError

class ReportJobCard(models.AbstractModel):
    _name = 'report.atlbs_job_card.report_job_card_template'
    _description = 'Job Card Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['job.card.management'].browse(docids)
        for doc in docs:
            if doc.vehicle_in_out != 'vehicle_in':
                raise UserError("Vehicle is not  'IN'. You cannot print the Job Card.")
        return {
            'doc_ids': docids,
            'doc_model': 'job.card.management',
            'docs': doc,
        }

