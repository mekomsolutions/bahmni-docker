# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StateDistrict(models.Model):
    _name = 'state.district'

    name = fields.Char(string="Name")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one('res.country', string="Country")

    @api.onchange('state_id')
    def onchange_state_id(self):
        domain = []
        # assign country from which state belongs too, and set domain restricted to it, so that user won't change it.
        if self.state_id:
            self.country_id = self.state_id.country_id.id
            domain = [('id', '=', self.state_id.country_id.id)]
        return {'domain': {'country_id': domain}}


class DistrictTehsil(models.Model):
    _name = 'district.tehsil'

    name = fields.Char(string="Name")
    district_id = fields.Many2one('state.district', string="District")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")

    @api.onchange('district_id')
    def onchange_district_id(self):
        domain = {}
        # assign state from which district belongs too, and set domain restricted to it, so that user won't change it.
        if self.district_id:
            self.state_id = self.district_id.state_id.id
            domain.update({'state_id': [('id', '=', self.district_id.state_id.id)]})
        return {'domain': domain}
 
    @api.onchange('state_id')
    def onchange_state_id(self):
        domain = {}
        # assign country from which state belongs too, and set domain restricted to it, so that user won't change it.
        if self.state_id:
            if self.district_id and self.state_id.id != self.district_id.state_id.id:
                self.district_id = False
                district_ids = self.env['state.district'].search([('state_id', '=', self.state_id.id)])
                domain.update({'district_id': [('id', 'in', district_ids.ids)]})
            self.country_id = self.state_id.country_id.id
            domain.update({'country_id': [('id', '=', self.state_id.country_id.id)]})
        return {'domain': domain}
 
    @api.onchange('country_id')
    def onchange_country_id(self):
        domain = {}
        if self.country_id:
            if self.state_id and self.country_id.id != self.state_id.country_id.id:
                self.state_id = False
                state_ids = self.env['res.country.state'].search([('country_id', '=', self.country_id.id)])
                domain.update({'state_id': [('id', 'in', state_ids.ids)]})
                self.district_id = False
                district_ids = self.env['state.district'].search([('state_id', 'in', state_ids.ids)])
                domain.update({'district_id': [('id', 'in', district_ids.ids)]})
        return {'domain': domain}


class VillageVillage(models.Model):
    _name = 'village.village'

    name = fields.Char(string="Name")
    district_id = fields.Many2one("state.district", string="District")
    tehsil_id = fields.Many2one("district.tehsil", string="Tehsil")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")

    @api.onchange('tehsil_id')
    def onchange_tehsil_id(self):
        domain = []
        if self.tehsil_id:
            self.district_id = self.tehsil_id.district_id.id
            domain = [('id', '=', self.tehsil_id.district_id.id)]
        return {'domain': {'district_id': domain}}

    @api.onchange('district_id')
    def onchange_district_id(self):
        domain = {}
        if self.district_id:
            if self.tehsil_id and self.tehsil_id.district_id.id != self.district_id.id:
                self.tehsil_id = False
                tehsil_ids = self.env['district.tehsil'].search([('district_id', '=', self.district_id.id)])
                domain.update({'tehsil_id': [('id', 'in', tehsil_ids.ids)]})
            self.state_id = self.district_id.state_id.id
            domain.update({'state_id': [('id', '=', self.district_id.state_id.id)]})
        return {'domain': domain}

    @api.onchange('state_id')
    def onchange_state_id(self):
        domain = {}
        if self.state_id:
            if self.district_id and self.district_id.state_id != self.state_id:
                self.district_id = False
                district_ids = self.env['state.district'].search([('state_id', '=', self.state_id.id)])
                domain.update({'district_id': [('id', 'in', district_ids.ids)]})
                self.tehsil_id = False
                tehsil_ids = self.env['district.tehsil'].search([('district_id', 'in', district_ids.ids)])
                domain.update({'tehsil_id': [('id', 'in', tehsil_ids)]})
            self.country_id = self.state_id.country_id.id
            domain = [('id', '=', self.state_id.country_id.id)]
        return {'domain': {'country_id': domain}}
