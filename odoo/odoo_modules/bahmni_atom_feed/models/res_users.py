# -*- coding: utf-8 -*-
import odoo
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    password = fields.Char(invisible=True)
    shop_id = fields.Many2one('sale.shop', 'Shop')

    @api.model
    def check_credentials(self, password):
        # convert to base_crypt if needed
        self.env.cr.execute('SELECT password, password_crypt FROM res_users WHERE id=%s AND active', (self.env.uid,))
        encrypted = None
        user = self.env.user
        if self.env.cr.rowcount:
            stored, encrypted = self.env.cr.fetchone()
            if stored and not encrypted:
                user._set_password(stored)
                self.invalidate_cache()
        try:
            return super(ResUsers, self).check_credentials(password)
        except odoo.exceptions.AccessDenied:
            if encrypted:
                valid_pass, replacement = user._crypt_context()\
                        .verify_and_update(password, encrypted)
                if replacement is not None:
                    user._set_encrypted_password(replacement)
                if valid_pass:
                    return
            raise
