from odoo import models, fields, api, tools
from collections import defaultdict


class JobCardCostAnalysisReport(models.Model):
    _name = 'job.card.cost.analysis.report'
    _description = 'Job Card Cost Analysis Report'
    _auto = False  # This will be a database view

    job_card_id = fields.Many2one('job.card.management', string="Job Card")
    partner_id = fields.Many2one('res.partner', string="Customer")
    vin_sn = fields.Char(string="VIN No")
    department = fields.Char(string="Department")
    product_id = fields.Many2one('product.product', string="Product")

    revenue = fields.Float(string="Revenue")
    cost = fields.Float(string="Cost")
    profit = fields.Float(string="Profit")



# changes this function on dec 08 for seeing only logined users records
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'job_card_cost_analysis_report')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW job_card_cost_analysis_report AS (
                SELECT
                    row_number() OVER() AS id,
                    jc.id AS job_card_id,
                    jc.partner_id,
                    jc.vin_sn,
                    COALESCE(ai_line.department, av_line.department) AS department,
                    COALESCE(ai_line.product_id, av_line.product_id) AS product_id,

                    SUM(CASE WHEN ai.id IS NOT NULL THEN ai_line.price_subtotal ELSE 0 END) AS revenue,
                    SUM(CASE WHEN av.id IS NOT NULL THEN av_line.price_subtotal ELSE 0 END) AS cost,
                    SUM(CASE WHEN ai.id IS NOT NULL THEN ai_line.price_subtotal ELSE 0 END)
                    - SUM(CASE WHEN av.id IS NOT NULL THEN av_line.price_subtotal ELSE 0 END) AS profit

                FROM job_card_management jc

                LEFT JOIN account_move ai ON ai.job_card_id = jc.id
                    AND ai.move_type = 'out_invoice' AND ai.state IN ('draft', 'posted')
                LEFT JOIN account_move_line ai_line ON ai_line.move_id = ai.id

                LEFT JOIN account_move av ON av.job_card_id = jc.id
                    AND av.move_type = 'in_invoice' AND av.state IN ('draft', 'posted')
                LEFT JOIN account_move_line av_line ON av_line.move_id = av.id

                -- 🔥 Show only job cards created by the logged-in user
                WHERE jc.create_uid = %s

                GROUP BY jc.id, jc.partner_id, jc.vin_sn,
                         COALESCE(ai_line.department, av_line.department),
                         COALESCE(ai_line.product_id, av_line.product_id)
            )
        """, (self.env.uid,))



    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, 'job_card_cost_analysis_report')
    #     self.env.cr.execute("""
    #         CREATE OR REPLACE VIEW job_card_cost_analysis_report AS (
    #             SELECT
    #                 row_number() OVER() AS id,
    #                 jc.id AS job_card_id,
    #                 jc.partner_id,
    #                 jc.vin_sn,
    #                 COALESCE(ai_line.department, av_line.department) AS department,
    #                 COALESCE(ai_line.product_id, av_line.product_id) AS product_id,
    #
    #                 SUM(CASE WHEN ai.id IS NOT NULL THEN ai_line.price_subtotal ELSE 0 END) AS revenue,
    #                 SUM(CASE WHEN av.id IS NOT NULL THEN av_line.price_subtotal ELSE 0 END) AS cost,
    #                 SUM(CASE WHEN ai.id IS NOT NULL THEN ai_line.price_subtotal ELSE 0 END)
    #                 - SUM(CASE WHEN av.id IS NOT NULL THEN av_line.price_subtotal ELSE 0 END) AS profit
    #
    #             FROM job_card_management jc
    #
    #             LEFT JOIN account_move ai ON ai.job_card_id = jc.id
    #                 AND ai.move_type = 'out_invoice' AND ai.state IN ('draft', 'posted')
    #             LEFT JOIN account_move_line ai_line ON ai_line.move_id = ai.id
    #
    #             LEFT JOIN account_move av ON av.job_card_id = jc.id
    #                 AND av.move_type = 'in_invoice' AND av.state IN ('draft', 'posted')
    #             LEFT JOIN account_move_line av_line ON av_line.move_id = av.id
    #
    #             GROUP BY jc.id, jc.partner_id, jc.vin_sn,
    #                      COALESCE(ai_line.department, av_line.department),
    #                      COALESCE(ai_line.product_id, av_line.product_id)
    #         )
    #     """)
