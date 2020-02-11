# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RoundingOff(models.Model):
    _name = 'rounding.off'

    def round_off_value_to_nearest(self, value):
        round_off_by = self.env['ir.values'].get_default('sale.config.settings', 'round_off_by')
        if(round_off_by > 0):
            half_round_off_by = round_off_by / 2.0
            remainder = value % round_off_by
            return -remainder if remainder < half_round_off_by\
                else round_off_by - remainder
        return 0
