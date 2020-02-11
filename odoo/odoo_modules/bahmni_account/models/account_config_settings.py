# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    round_off_by = fields.Float(string="Round off by", related="company_id.round_off_by")

    @api.multi
    def set_round_off_by_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'round_off_by', self.round_off_by)
            

