# controllers/main.py

from odoo import http
from odoo.http import request


class JobCardDashboardController(http.Controller):

    @http.route('/job_card_dashboard', type='http', auth='user', website=False)
    def job_card_dashboard(self, **kwargs):
        JobCard = request.env['job.card.management']
        vehicle_in_count = JobCard.search_count([('vehicle_in_out', '=', 'vehicle_in')])
        vehicle_out_count = JobCard.search_count([('vehicle_in_out', '=', 'vehicle_out')])

        return request.render('your_module_name.template_job_card_dashboard', {
            'vehicle_in_count': vehicle_in_count,
            'vehicle_out_count': vehicle_out_count
        })
