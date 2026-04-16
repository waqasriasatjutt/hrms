# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import SQL


class SBLProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def sbl_search_products_dynamic(self, config_id, search_term, limit=50):
        """Dynamic search for products not in initial POS load"""
        config = self.env['pos.config'].browse(config_id)
        
        if not config.sbl_enable_pos_speedup:
            return {'error': 'Dynamic search not enabled'}
        
        # Build search domain
        domain = []
        domain.extend([
            '|', '|', '|',
            ('name', 'ilike', search_term),
            ('default_code', 'ilike', search_term),
            ('barcode', 'ilike', search_term),
            ('product_tmpl_id.name', 'ilike', search_term),
        ])
        
        products = self.search(domain, limit=limit)
        fields = self._load_pos_data_fields(config_id)
        
        return {
            'products': products.read(fields, load=False),
            'count': len(products)
        }

    def _load_pos_data(self, data):
        """Override to implement smart loading when speedup is enabled"""
        config = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        
        if config.sbl_enable_pos_speedup:
            # Use smart loading for speedup
            return self._sbl_smart_product_loading(config, data)
        else:
            # Use standard Odoo behavior
            return super()._load_pos_data(data)

    def _sbl_smart_product_loading(self, config, data):
        """Smart product loading: Always load + Limited products"""
        # Get fields for product data
        fields = set(self._load_pos_data_fields(config.id))
        taxes = self.env['account.tax'].search(self.env['account.tax']._load_pos_data_domain(data))
        product_fields = taxes._eval_taxes_computation_prepare_product_fields()
        fields = list(fields.union(product_fields))

        # Step 1: Get "Always Load" products
        always_load_products = self.search([
            ('available_in_pos', '=', True),
            ('product_tmpl_id.sbl_always_load_in_pos', '=', True)
        ] + config._get_available_product_domain())

        # Step 2: Get limited products (excluding always load to avoid duplicates)
        regular_domain = config._get_available_product_domain()
        regular_domain.append(('product_tmpl_id.sbl_always_load_in_pos', '=', False))

        limited_products = self._sbl_get_limited_products_with_domain(
            regular_domain,
            config.sbl_initial_product_limit,
            fields
        )

        # Step 3: Combine both sets
        all_products = always_load_products | limited_products

        # Step 4: Read product data
        products_data = all_products.read(fields, load=False)

        # Step 5: Add missing products from draft orders (if pos.order.line data exists)
        if 'pos.order.line' in data and 'data' in data['pos.order.line']:
            self._add_missing_products(products_data, config.id, data)

        # Step 6: Set _product_default_values for tax computation (CRITICAL - fixes the error!)
        data['pos.config']['data'][0]['_product_default_values'] = \
            self.env['account.tax']._eval_taxes_computation_prepare_product_default_values(product_fields)

        # Step 7: Process products for POS UI (tax filtering, currency conversion)
        self._process_pos_ui_product_product(products_data, config)

        return {
            'data': products_data,
            'fields': fields,
        }

    def _sbl_get_limited_products_with_domain(self, domain, limit, fields):
        """Get limited products using the specified domain and limit"""
        # Use _where_calc to properly apply domain (same as base Odoo)
        query = self._where_calc(domain)

        sql = SQL(
            """
            WITH pm AS (
                  SELECT product_id,
                         MAX(write_date) date
                    FROM stock_move_line
                GROUP BY product_id
            )
               SELECT product_product.id
                 FROM %s
            LEFT JOIN pm ON product_product.id=pm.product_id
                WHERE %s
             ORDER BY product_product__product_tmpl_id.is_favorite DESC,
                      CASE WHEN product_product__product_tmpl_id.type = 'service' THEN 1 ELSE 0 END DESC,
                      pm.date DESC NULLS LAST,
                      product_product.write_date DESC
                LIMIT %s
            """,
            query.from_clause,
            query.where_clause or SQL("TRUE"),
            limit,
        )

        product_ids = [r[0] for r in self.env.execute_query(sql)]
        products = self.browse(product_ids)

        # Handle combo products (similar to standard implementation)
        product_combo = products.filtered(lambda p: p.type == 'combo')
        if product_combo:
            product_in_combo = product_combo.combo_ids.combo_item_ids.product_id
            products = products | product_in_combo

        return products

    @api.model
    def sbl_get_always_load_products_count(self, config_id):
        """Get count of products marked as always load for a specific config"""
        config = self.env['pos.config'].browse(config_id)
        domain = config._get_available_product_domain()
        domain.append(('product_tmpl_id.sbl_always_load_in_pos', '=', True))
        
        return self.search_count(domain)