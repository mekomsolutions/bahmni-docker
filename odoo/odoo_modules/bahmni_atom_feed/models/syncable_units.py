# -*- coding: utf-8 -*-
from odoo import models, fields


class SyncableUnits(models.Model):
    _name = 'syncable.units'
    _description = "Units allowed to Sync as it is"

    name = fields.Char(string="Unit Name", required=True)
