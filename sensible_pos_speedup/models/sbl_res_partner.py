# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import SQL


class SBLResPartner(models.Model):
    _inherit = 'res.partner'

    sbl_always_load_in_pos = fields.Boolean(
        string="Always Load in POS",
        default=False,
        help="Force this customer to be loaded immediately in POS, regardless of the configured customer limit. "
             "Use this for VIP customers, frequent buyers, or business partners."
    )

    @api.model
    def sbl_search_partners_dynamic(self, config_id, search_term, limit=50):
        """Dynamic search for partners not in initial POS load"""
        config = self.env['pos.config'].browse(config_id)

        if not config.sbl_enable_pos_speedup:
            return {'error': 'Dynamic search not enabled'}

        domain = [
            '|', '|', '|', '|',
            ('name', 'ilike', search_term),
            ('phone', 'ilike', search_term),
            ('mobile', 'ilike', search_term),
            ('email', 'ilike', search_term),
            ('barcode', 'ilike', search_term)
        ]

        partners = self.search(domain, limit=limit)
        fields = self._load_pos_data_fields(config_id)

        return {
            'partners': partners.read(fields, load=False),
            'count': len(partners)
        }

    def _load_pos_data(self, data):
        """Override to implement smart partner loading when speedup is enabled"""
        config = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])

        if config.sbl_enable_pos_speedup:
            # Use smart loading for speedup
            return self._sbl_smart_partner_loading(config, data)
        else:
            # Use standard Odoo behavior
            return super()._load_pos_data(data)

    def _sbl_smart_partner_loading(self, config, data):
        """Smart partner loading: Always load + Limited partners"""
        fields = self._load_pos_data_fields(config.id)

        # Step 1: Get "Always Load" partners
        always_load_partners = self.search([('sbl_always_load_in_pos', '=', True)])

        # Step 2: Get limited partners (excluding always load to avoid duplicates)
        limited_partner_ids = self._sbl_get_limited_partners_excluding_always_load(config)

        # Step 3: Get partners from loaded orders (if pos.order data exists)
        loaded_order_partner_ids = set()
        if 'pos.order' in data and 'data' in data['pos.order']:
            loaded_order_partner_ids = {order['partner_id'] for order in data['pos.order']['data'] if order.get('partner_id')}

        # Step 4: Ensure current user's partner is included
        limited_partner_ids.add(self.env.user.partner_id.id)

        # Step 5: Combine all partner IDs
        all_partner_ids = set(always_load_partners.ids).union(limited_partner_ids).union(loaded_order_partner_ids)

        # Step 6: Load partners
        partners = self.browse(list(all_partner_ids))
        partners_data = partners.read(fields, load=False)

        return {
            'data': partners_data,
            'fields': fields,
        }

    def _sbl_get_limited_partners_excluding_always_load(self, config):
        """Get limited partners excluding those marked as always load"""
        # Build domain similar to base Odoo, but exclude always_load partners
        domain = [
            ('sbl_always_load_in_pos', '=', False),
            ('active', '=', True),
            '|',
                ('company_id', '=', config.company_id.id),
                ('company_id', '=', False)
        ]

        # Use _where_calc to properly apply domain with all Odoo filters and security
        query = self._where_calc(domain)

        sql = SQL("""
            WITH pm AS (
                SELECT   partner_id,
                         Count(partner_id) order_count
                FROM     pos_order
                WHERE    partner_id IS NOT NULL
                GROUP BY partner_id
            )
            SELECT    res_partner.id
            FROM      %s
            LEFT JOIN pm ON res_partner.id = pm.partner_id
            WHERE     %s
            ORDER BY  Coalesce(pm.order_count, 0) DESC,
                      res_partner.write_date DESC
            LIMIT %s
        """, query.from_clause, query.where_clause or SQL("TRUE"), config.sbl_initial_customer_limit)

        result = self.env.execute_query(sql)
        return {r[0] for r in result}

    @api.model
    def sbl_get_always_load_partners_count(self, config_id):
        """Get count of partners marked as always load"""
        return self.search_count([('sbl_always_load_in_pos', '=', True)])