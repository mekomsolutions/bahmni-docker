# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import json
import uuid

STATE_CODE_PREFIX = 'UNKNOWN-'
_logger = logging.getLogger(__name__)


class AtomEventWorker(models.Model):
    _name = 'atom.event.worker'
    _auto = False

    @api.model
    def process_event(self, vals):
        '''Method getting triggered from Bahmni side'''
        _logger.info("vals")
        _logger.info(vals)
        category = vals.get("category")
#         patient_ref = vals.get("ref")
        try:
            if category == "create.customer":
                self._create_or_update_customer(vals)
            elif category == "create.drug":
                self.env['drug.data.service'].create_or_update_drug(vals)
            elif category == "create.sale.order":
                self.env['order.save.service'].create_orders(vals)
            elif category == 'create.drug.category':
                self.env['drug.data.service'].create_or_update_drug_category(vals)
            elif category == 'create.drug.uom':
                self.env['product.uom.service'].create_or_update_product_uom(vals)
            elif category == 'create.drug.uom.category':
                self.env['product.uom.service'].create_or_update_product_uom_category(vals)
            elif category == "create.radiology.test":
                self.env['reference.data.service'].create_or_update_ref_data(vals, 'Radiology')
            elif category == "create.lab.test":
                self.env['reference.data.service'].create_or_update_ref_data(vals, 'Test')
            elif category == "create.lab.panel":
                self.env['reference.data.service'].create_or_update_ref_data(vals, 'Panel')
            elif category == "create.service.saleable":
                self.env['reference.data.service'].create_or_update_ref_data(vals, 'Others')

            return {'success': True}    
        except Exception as err:
            _logger.info("\n Processing event threw error: %s", err)
            raise

    @api.model
    def _update_marker(self,  feed_uri_for_last_read_entry, last_read_entry_id, marker_ids):
        for marker_id in marker_ids:
            marker = self.env['atom.feed.marker']
            marker._update_marker(marker_id,last_read_entry_id, feed_uri_for_last_read_entry)


    @api.model
    def _create_marker(self, feed_uri_for_last_read_entry, last_read_entry_id, feed_uri):
        marker = {'feed_uri': feed_uri, 'last_read_entry_id': last_read_entry_id,
                  'feed_uri_for_last_read_entry': feed_uri_for_last_read_entry}
        self.env['atom.feed.marker'].create(marker)


    @api.model
    def _create_or_update_marker(self, vals):
        '''Method to Create or Update entries for markers table for the event taking place'''
        is_failed_event = vals.get('is_failed_event',False)
        if is_failed_event:
            return

        last_read_entry_id = vals.get('last_read_entry_id')
        feed_uri_for_last_read_entry = vals.get('feed_uri_for_last_read_entry')
        feed_uri = vals.get('feed_uri')

        # Rohan/Mujir - do not update markers for failed events (failed events have empty 'feed_uri_for_last_read_entry')
        if not feed_uri_for_last_read_entry or not feed_uri or "$param" in feed_uri_for_last_read_entry or "$param" in feed_uri:
            return

        marker = self.env['atom.feed.marker'].search([('feed_uri', '=', feed_uri)],
                                                     limit=1)
      
        if marker:
            self._update_marker(feed_uri_for_last_read_entry, last_read_entry_id, marker)
        else:
            self._create_marker(feed_uri_for_last_read_entry, last_read_entry_id, feed_uri)

    @api.model
    def _create_or_update_customer(self, vals):
        patient_ref = vals.get("ref")
        customer_vals = self._get_customer_vals(vals)
        # removing null values, as while updating null values in write method will remove old values

        for rec in customer_vals.keys():
            if not customer_vals[rec]:
                del customer_vals[rec]
        existing_customer = self.env['res.partner'].search([('ref', '=', patient_ref)])
        if existing_customer:
            existing_customer.write(customer_vals)
            self._create_or_update_person_attributes(existing_customer.id,vals)
        else:
            customer = self.env['res.partner'].create(customer_vals)
            self._create_or_update_person_attributes(customer.id,vals)

    @api.model
    def _get_address_details(self, address):
        res = {}
        if address.get('address1'):
            res.update({'street': address['address1']})
        if address.get('address2'):
            res.update({'street2': address['address2']})

        auto_create_customer_address_levels = self.env.ref('bahmni_sale.auto_create_customer_address_levels').value
        country = self._find_country(address)
        state = None
        district = None
        if address.get("stateProvince") and country:
            state = self._find_or_create_state(country, address['stateProvince'], auto_create_customer_address_levels)
            if state:
                res.update({'state_id': state.id})

        if address.get('countyDistrict') and state:
            district = self._find_or_create_district(country, state, address.get('countyDistrict'), auto_create_customer_address_levels)
            if district:
                res.update({'district_id': district.id})

        # for now, from bahmni side, Taluka is sent as address3
        if address.get('address3') and district:
            # =ilike operator will ignore the case of letters while comparing
            tehsil = self._find_or_create_level3(state, district, address['address3'], auto_create_customer_address_levels)
            if tehsil:
                res.update({'tehsil_id': tehsil.id})

        return res

    @api.model
    def _find_country(self, address):
        # TODO: from bahmni side, no country is getting passed, so using company's country id
        # once from bahmni side country name is passed properly, replace with that key
        return self.env.user.company_id.country_id

    @api.model
    def _find_or_create_level3(self, state, district, level_name, auto_create_customer_address_levels):
        levels = self.env['district.tehsil'].search([('name', '=ilike', level_name),
                                                    ('district_id', '=', district.id if district else False)])
        if not levels and auto_create_customer_address_levels == '1':
            # TODO, check if configuration enabled to create level3 if not present
            level = self.env['district.tehsil'].create({'name': level_name,
                                                        'district_id': district.id if district else False,
                                                        'state_id': state.id if state else False})
        else:
            level = levels[0]
        return level

    @api.model
    def _find_or_create_district(self, country, state, district_county_name, auto_create_customer_address_levels):
        districts = self.env['state.district'].search([('name', '=ilike', district_county_name),
                                                      ('state_id', '=', state.id if state else None)])
        if not districts and auto_create_customer_address_levels == '1':
            # TODO, check if configuration enabled to create state if not present
            district = self.env['state.district'].create({'name': district_county_name,
                                                          'state_id': state.id if state else None,
                                                          'country_id': country.id})
        else:
            district = districts[0]
        return district

    @api.model
    def _find_or_create_state(self, country, state_province_name, auto_create_customer_address_levels):
        states = self.env['res.country.state'].search([('name', '=ilike', state_province_name),
                                                      ('country_id', '=', country.id)])
        if not states and auto_create_customer_address_levels == '1':
            # TODO, check if configuration enabled to create state if not present
            state_code = STATE_CODE_PREFIX + str(uuid.uuid4())
            state = self.env['res.country.state'].create({'name': state_province_name,
                                                          'code': state_code,
                                                          'country_id': country.id})
        else:
            state = states[0]
        return state

    def _get_customer_vals(self, vals):
        res = {}
        res.update({'ref': vals.get('ref'),
                    'name': vals.get('name'),
                    'local_name': vals.get('local_name'),
                    'uuid': vals.get('uuid')})
        address_data = vals.get('preferredAddress')
        # get validated address details
        address_details = self._get_address_details(json.loads(address_data))
        # update address details
        res.update(address_details)
        # update other details : for now there is only scope of updating contact.
        if vals.get('primaryContact'):
            res.update({'phone': vals['primaryContact']})
        return res
        
    def _create_or_update_person_attributes(self, cust_id, vals):#TODO whole method
        attributes = json.loads(vals.get("attributes", "{}"))
        openmrs_patient_attributes = str(self.env.ref('bahmni_atom_feed.openmrs_patient_attributes').value)
        openmrs_attributes_list = filter(lambda s: len(s) > 0, map(str.strip, openmrs_patient_attributes.split(',')))
        _logger.info("\n List of Patient Attributes to Sync = %s", openmrs_attributes_list)
        for key in attributes:
            if key in openmrs_attributes_list:
                column_dict = {'partner_id': cust_id}
                existing_attribute = self.env['res.partner.attributes'].search([('partner_id', '=', cust_id),('name', '=', key)])
                if any(existing_attribute):
                    existing_attribute.unlink()
                column_dict.update({"name": key, "value" : attributes[key]})
                self.env['res.partner.attributes'].create(column_dict)
