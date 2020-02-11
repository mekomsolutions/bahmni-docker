# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class AtomFeedMarker(models.Model):
    _name = 'atom.feed.marker'
    _table = 'markers'
    
    @api.model
    def _update_marker(self, marker_id,last_read_entry_id,feed_uri_for_last_read_entry):
        _logger.info("\n\n***marker_id=%s",marker_id)
        marker = self.browse(marker_id.id)
        marker.write({'last_read_entry_id': last_read_entry_id,'feed_uri_for_last_read_entry': feed_uri_for_last_read_entry,})
        _logger.info("\n\n***marker=%s",marker) 
    feed_uri = fields.Char(string="uuid",size=250,translate=True,required=True)
    last_read_entry_id = fields.Char(string="Title", size=250, translate=True, required=True)
    feed_uri_for_last_read_entry = fields.Char(string="Category", size=100, translate=True, required=True)
