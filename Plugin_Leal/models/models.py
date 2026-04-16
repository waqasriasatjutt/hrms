# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_product_if_in_pos_category(self, product_id, category_name):
        """
        Devuelve el producto si pertenece a una categoría POS cuyo nombre (en minúsculas)
        contiene `category_name` (también en minúsculas).
        """
        query = """
            SELECT pp.*
            FROM product_product pp
            INNER JOIN pos_category_product_template_rel pcptr ON pp.product_tmpl_id = pcptr.product_template_id
            INNER JOIN pos_category pc ON pcptr.pos_category_id = pc.id
            WHERE pp.id = %s
              AND LOWER(pc.name::varchar) LIKE %s
        """
        category_pattern = f'%{category_name.lower()}%'
        self._cr.execute(query, [product_id, category_pattern])
        result = self._cr.dictfetchone()
        
        # _logger.critical(f"Query executed: {self._cr.query}")
        # _logger.critical(f"result: {result}")

        return result

