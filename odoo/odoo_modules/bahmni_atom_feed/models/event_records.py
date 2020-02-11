# -*- coding: utf-8 -*-
from odoo import models, fields, api


class EventRecords(models.Model):
    _name = 'event.records'
    _table = 'event_records'
    _description = 'Class for publishing events for changes done in odoo '\
                        'and needs to be synced with bahmni'

    uuid = fields.Char(string="UUID", translate=True, required=True)
    title = fields.Char(string="Title", translate=True, required=True)
    category = fields.Char(string="Category", translate=True, required=True)
    timestamp = fields.Datetime(string="Timestamp", required=True)
    uri = fields.Char(string="URI", translate=True)
    object = fields.Text(string="SerializedContents", required=True)