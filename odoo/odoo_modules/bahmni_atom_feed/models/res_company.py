# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    dhis2_code = fields.Char(string="DHIS Code")

    _header_main_wo_placeholders = """
            <header>
                <pageTemplate>
                    <frame id="first" x1="1.3cm" y1="3.0cm" height="21.7cm" width="19.0cm"/>
                     <stylesheet>
                        <paraStyle name="main_footer"  fontName="DejaVu Sans" fontSize="8.0" alignment="CENTER"/>
                        <paraStyle name="main_header"  fontName="DejaVu Sans" fontSize="8.0" leading="10" alignment="LEFT" spaceBefore="0.0" spaceAfter="0.0"/>
                     </stylesheet>
                    <pageGraphics>
                        <drawString x="1.3cm" y="27.3cm">[[ company.partner_id.name ]]</drawString>
                        <place x="1.3cm" y="25.3cm" height="1.8cm" width="15.0cm">
                            <para style="main_header">[[ display_address(company.partner_id) or  '' ]]</para>
                        </place>
                   </pageGraphics>
                </pageTemplate>
            </header>"""

    _header_a4 = _header_main_wo_placeholders