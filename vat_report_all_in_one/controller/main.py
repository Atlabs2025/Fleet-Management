# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request


class VATReportXLSXDownload(http.Controller):

    @http.route(
        ["/web/binary/download_xlsx_report/<int:file>"],
        type='http',
        auth="public",
        website=True,
        sitemap=False)
    def download_proxy_detail_excel(self, file=None, **post):
        if file:
            file_id = request.env['od.vat.report.download'].sudo().browse([file])
            if file_id and file_id.excel_file:
                content_base64 = base64.b64decode(file_id.excel_file or '')
                headers = [
                    ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                    ('Content-Disposition', f'attachment; filename="{file_id.file_name}"'),
                ]
                return request.make_response(content_base64, headers=headers)
        return request.not_found()






# # -*- coding: utf-8 -*-
# import base64
# from odoo import http
# from odoo.http import request
#
#
# class VATReportXLSXDownload(http.Controller):
#
#     @http.route(
#         ["/web/binary/download_xlsx_report/<int:file>"],
#         type='http',
#         auth="public",
#         website=True,
#         sitemap=False)
#     def download_proxy_detail_excel(self, file=None, **post):
#         if file:
#             file_id = request.env['od.vat.report.download'].browse([file])
#             if file_id:
#                 status, headers, content = request.env['ir.http'].sudo().binary_content(model='od.vat.report.download', id=file_id.id, field='excel_file', filename_field=file_id.file_name)
#                 content_base64 = base64.b64decode(content) if content else ''
#                 headers.append(('Content-Type', 'application/vnd.ms-excel'))
#                 headers.append(('Content-Disposition', 'attachment; filename=' + file_id.file_name + ';'))
#                 return request.make_response(content_base64, headers)
#         return False
