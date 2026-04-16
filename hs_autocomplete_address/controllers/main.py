# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
import requests
import logging
from odoo import http
from odoo.http import request
from odoo.tools import html2plaintext
_logger = logging.getLogger(__name__)

FIELDS_MAPPING = {
    'country': ['country'],
    'street_number': ['number'],
    'locality': ['city'],
    'route': ['street'],
    'postal_code': ['zip'],
    'administrative_area_level_1': ['state', 'city'],
    'administrative_area_level_2': ['state', 'country']
}

FIELDS_PRIORITY = ['country', 'street_number', 'neighborhood', 'locality', 'route', 'postal_code', 'administrative_area_level_1', 'administrative_area_level_2']
GOOGLE_PLACES_ENDPOINT = 'https://maps.googleapis.com/maps/api/place'
TIMEOUT = 2.5
LOCALPARAM = {}

class AdressAutoComplete(http.Controller):
    def _google_translate(self, google_fields):
        standard_data = {}

        for google_field in google_fields:
            fields_standard = FIELDS_MAPPING[google_field['type']] if google_field['type'] in FIELDS_MAPPING else []

            for field_standard in fields_standard:
                if field_standard in standard_data:
                    continue
                if field_standard == 'country':
                    standard_data[field_standard] = request.env['res.country'].search([('code', '=', google_field['short_name'].upper())])[0].id
                elif field_standard == 'state':
                    state = request.env['res.country.state'].search([('code', '=', google_field['short_name'].upper()), ('country_id.id', '=', standard_data['country'])]) if 'country' in standard_data else request.env['res.country.state'].search([('code', '=', google_field['short_name'].upper())])
                    if len(state) == 1:
                        standard_data[field_standard] = state.id
                else:
                    standard_data[field_standard] = google_field['long_name']
        return standard_data

    def _get_number_input(self, input, address):
        guessed_house_number = input \
            .replace(address.get('zip', ''), '') \
            .replace(address.get('street', ''), '') \
            .replace(address.get('city', ''), '')
        guessed_house_number = guessed_house_number.split(',')[0].strip()
        return guessed_house_number

    def _address_search(self, partial_address, api_key=None, session_id=None, language_code=None, country_code=None):
        if len(partial_address) <= 5:
            return {
                'results': [],
                'session_id': session_id
            }
        params = {
            'key': api_key,
            'fields': 'formatted_address,name',
            'inputtype': 'textquery',
            'types': 'address',
            'input': partial_address,
            'language': request.env.user.lang,
        }

        if language_code: params['language'] = language_code
        if session_id: params['sessiontoken'] = session_id
        
        try:
            results = requests.get(f'{GOOGLE_PLACES_ENDPOINT}/autocomplete/json', params=params, timeout=TIMEOUT).json()
        except (TimeoutError, ValueError) as e:
            _logger.error(e)
            return {
                'results': [],
                'session_id': session_id
            }

        if results.get('error_message'):
            _logger.error(results['error_message'])

        results = results.get('predictions', [])

        return {
            'results': [{
                'formatted_address': result['description'],
                'google_place_id': result['place_id'],
            } for result in results],
            'session_id': session_id
        }

    def _complete_address_search(self, address, api_key=None, google_place_id=None, language_code=None, session_id=None):
        params = {
            'key': api_key,
            'place_id': google_place_id,
            'fields': 'address_component,adr_address',
            'language': request.env.user.lang,
        }

        if language_code: params['language'] = language_code
        if session_id: params['sessiontoken'] = session_id
        
        try:
            results = requests.get(f'{GOOGLE_PLACES_ENDPOINT}/details/json', params=params, timeout=TIMEOUT).json()
        except (TimeoutError, ValueError) as e:
            _logger.error(e)
            return {'address': None}

        if results.get('error_message'):
            _logger.error(results['error_message'])

        try:
            html_address = results['result']['adr_address']
            results = results['result']['address_components']
        except KeyError:
            return {'address': None}

        for res in results: res['type'] = res.pop('types')[0]

        results.sort(key=lambda r: FIELDS_PRIORITY.index(r['type']) if r['type'] in FIELDS_PRIORITY else 100)

        standard_address = self._google_translate(results)

        if 'number' not in standard_address:
            standard_address['number'] = self._get_number_input(address, standard_address)
            standard_address['formatted_street_number'] = f'{standard_address["number"]} {standard_address.get("street", "")}'
        else:
            formatted_from_html = html2plaintext(html_address.split(',')[0])
            formatted_manually = f'{standard_address["number"]} {standard_address.get("street", "")}'
            if len(formatted_from_html) >= len(formatted_manually):
                standard_address['formatted_street_number'] = formatted_from_html
            else:
                standard_address['formatted_street_number'] = formatted_manually
        return standard_address

    @http.route('/address/autocomplete', methods=['POST'], type='json', auth='public', website=True)
    def _autocomplete_address(self, partial_address, session_id=None):
        autocomplete = request.env['ir.config_parameter'].sudo().get_param('address_autocomplete')
        if(autocomplete):
            api_key = request.env['ir.config_parameter'].sudo().get_param('google_api_key')
            if(not api_key): return None
            return self._address_search(partial_address, session_id=session_id, api_key=api_key)

    @http.route('/address/autocomplete/full', methods=['POST'], type='json', auth='public', website=True)
    def _autocomplete_address_full(self, address, session_id=None, google_place_id=None, **kwargs):
        api_key = request.env['ir.config_parameter'].sudo().get_param('google_api_key')
        if(not api_key): return None
        return self._complete_address_search(address, google_place_id=google_place_id, session_id=session_id, api_key=api_key, **kwargs)
