# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ref field is a default field of this class
    _sql_constraints = [('unique_ref', 'unique(ref)',
                         'Internal Reference for Customer should be unique!')]

    village_id = fields.Many2one('village.village', string="Village")
    tehsil_id = fields.Many2one('district.tehsil', string="Tehsil")
    district_id = fields.Many2one('state.district', string="District")
    local_name = fields.Char(string="Local Name")
    uuid = fields.Char(string = "UUID")
    attribute_ids = fields.One2many('res.partner.attributes', 'partner_id', string='Attributes')


    # inherited to update display name w.r.t. ref field 
    # and hence user can search customer with reference too
    @api.depends('is_company', 'name', 'parent_id.name',
                 'type', 'company_name', 'ref')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    # method is overridden to set ref in string returned by name_get
    @api.multi
    def name_get(self):
        res = []
        for partner in self:
            name = partner.name or ''
            if partner.ref:
                name += ' [' + partner.ref + ']'
            if partner.company_name or partner.parent_id:
                if not name and partner.type in ['invoice', 'delivery', 'other']:
                    name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
                if not partner.is_company:
                    name = "%s, %s" % (partner.commercial_company_name or partner.parent_id.name, name)
            if self._context.get('show_address_only'):
                name = partner._display_address(without_company=True)
            if self._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
            if self._context.get('show_email') and partner.email:
                name = "%s <%s>" % (name, partner.email)
            if self._context.get('html_format'):
                name = name.replace('\n', '<br/>')
            res.append((partner.id, name))
        return res

    @api.onchange('village_id')
    def onchange_village_id(self):
        if self.village_id:
            self.district_id = self.village_id.district_id.id
            self.tehsil_id = self.village_id.tehsil_id.id
            self.state_id = self.village_id.state_id.id
            self.country_id = self.village_id.country_id.id
            return {'domain': {'tehsil_id': [('id', '=', self.village_id.tehsil_id.id)],
                               'state_id': [('id', '=', self.village_id.state_id.id)],
                               'district_id': [('id', '=', self.village_id.district_id.id)],
                               'country_id': [('id', '=', self.village_id.country_id.id)]}}
        else:
            return {'domain': {'tehsil_id': [],
                               'state_id': [],
                               'district_id': [],
                               'country_id': []}}

class ResPartnerAttributes(models.Model):
    _name = 'res.partner.attributes'
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, index=True, readonly=False)
    name = fields.Char(string='Name', size=128, required=True)
    value = fields.Char(string='Value', size=128, required=False)
            
