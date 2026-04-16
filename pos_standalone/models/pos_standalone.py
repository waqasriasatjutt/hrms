# -*- coding: utf-8 -*-

import os
import zipfile
import io
import json
import base64
import datetime
from odoo import models, fields, api
from odoo.tools import human_size


class PosStandaloneConfig(models.Model):
    _name = 'pos.standalone.config'
    _description = 'POS Standalone Configuration'
    _order = 'name'

    name = fields.Char(string='Configuration Name', required=True, default='POS Standalone')
    active = fields.Boolean(string='Active', default=True)
    
    # Connection Settings (computed from current environment)
    server_url = fields.Char(string='Server URL', compute='_compute_connection_settings', store=False)
    database_name = fields.Char(string='Database Name', compute='_compute_connection_settings', store=False)
    
    # Currency Settings
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env['res.currency'].search([('name', '=', 'IDR')], limit=1) or 
                                  self.env.company.currency_id)
    
    # Display Settings (computed from currency)
    currency_symbol = fields.Char(string='Currency Symbol', compute='_compute_currency_settings', store=False)
    thousand_separator = fields.Char(string='Thousand Separator', compute='_compute_currency_settings', store=False)
    decimal_separator = fields.Char(string='Decimal Separator', compute='_compute_currency_settings', store=False)
    
    # Security
    security_pin = fields.Char(string='Security PIN', help='PIN for session locking')
    
    # Sync Settings
    sync_interval = fields.Integer(string='Sync Interval (seconds)', default=300, 
                                   help='Auto-sync interval in seconds (0 = disabled)')
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    
    # Rounding
    rounding_method = fields.Selection([
        ('normal', 'Normal Rounding'),
        ('up', 'Round Up'),
        ('down', 'Round Down'),
        ('half_up', 'Half Up'),
    ], string='Rounding Method', default='normal')
    rounding_factor = fields.Float(string='Rounding Factor', default=0.01)
    
    # Business Info
    business_name = fields.Char(string='Business Name')
    business_address = fields.Text(string='Business Address')
    business_phone = fields.Char(string='Business Phone')
    business_email = fields.Char(string='Business Email')
    
    # Receipt Settings
    receipt_header = fields.Text(string='Receipt Header')
    receipt_footer = fields.Text(string='Receipt Footer')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    @api.depends("active")
    def _compute_connection_settings(self):
        """Compute server URL and database name from current environment"""
        for record in self:
            # Get current server URL from ir.config_parameter or web.base.url
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            if base_url:
                record.server_url = base_url.rstrip('/')
            else:
                # Fallback to request if available
                if hasattr(self.env, 'cr') and hasattr(self.env.cr, 'dbname'):
                    record.server_url = f'http://localhost:8069'
                else:
                    record.server_url = ''
            
            # Get current database name
            if hasattr(self.env, 'cr') and hasattr(self.env.cr, 'dbname'):
                record.database_name = self.env.cr.dbname
            else:
                record.database_name = ''

    @api.depends("currency_id")
    def _compute_currency_settings(self):
        """Compute currency display settings from selected currency"""
        for record in self:
            if record.currency_id:
                # Get currency symbol
                record.currency_symbol = record.currency_id.symbol or record.currency_id.name
                
                # Set separators based on currency
                if record.currency_id.name in ['IDR', 'MYR', 'TWD', 'VND']:
                    # Asian currencies typically use . for thousands and , for decimal
                    record.thousand_separator = '.'
                    record.decimal_separator = ','
                elif record.currency_id.name in ['USD', 'CAD', 'AUD', 'NZD', 'SGD', 'HKD']:
                    # Western currencies typically use , for thousands and . for decimal
                    record.thousand_separator = ','
                    record.decimal_separator = '.'
                else:
                    # Default to Western format
                    record.thousand_separator = ','
                    record.decimal_separator = '.'
            else:
                # Fallback defaults
                record.currency_symbol = 'Rp'
                record.thousand_separator = '.'
                record.decimal_separator = ','

    def action_download_standalone(self):
        """Download POS Standalone files as ZIP with real Odoo data"""
        self.ensure_one()
        
        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Get module path
            module_path = os.path.dirname(os.path.dirname(__file__))
            static_path = os.path.join(module_path, 'static')
            
            # Files to include in ZIP (root level files)
            files_to_include = [
                'static/pos_standalone.py',
                'static/index.html',
                'static/manifest.json',
                'static/service-worker.js',
            ]
            
            # Add individual files to root of ZIP
            for file_path in files_to_include:
                full_path = os.path.join(module_path, file_path)
                if os.path.exists(full_path):
                    # Extract filename for root level placement
                    filename = os.path.basename(file_path)
                    zip_file.write(full_path, filename)
            
            # Add src directory recursively, but skip db_service.js (will be injected separately)
            src_path = os.path.join(static_path, 'src')
            if os.path.exists(src_path):
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        file_full_path = os.path.join(root, file)
                        # Get relative path from src directory
                        rel_path = os.path.relpath(file_full_path, src_path)
                        
                        # Skip db_service.js as it will be injected with updated content
                        if file == 'db_service.js' and rel_path == 'services/db_service.js':
                            continue
                        
                        zip_file.write(file_full_path, f'src/{rel_path}')
            
            # Inject MOCK_DATA directly into db_service.js
            db_service_path = os.path.join(src_path, 'services', 'db_service.js')
            if os.path.exists(db_service_path):
                with open(db_service_path, 'r', encoding='utf-8') as f:
                    db_service_content = f.read()
                
                # Generate mock data and replace MOCK_DATA in the file
                mock_data_content = self._generate_mock_data_js()
                
                # Replace the MOCK_DATA variable with more precise pattern
                import re
                # Find the start and end of MOCK_DATA
                start_pattern = r'const MOCK_DATA = \{'
                end_pattern = r'\};'
                
                # Find start position
                start_match = re.search(start_pattern, db_service_content)
                if start_match:
                    start_pos = start_match.start()
                    # Find the matching closing brace for MOCK_DATA
                    brace_count = 0
                    pos = start_match.end() - 1  # Start from the opening brace
                    
                    while pos < len(db_service_content):
                        if db_service_content[pos] == '{':
                            brace_count += 1
                        elif db_service_content[pos] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                # Found the closing brace
                                end_pos = pos + 1
                                break
                        pos += 1
                    
                    if brace_count == 0:
                        # Replace the entire MOCK_DATA
                        updated_content = (
                            db_service_content[:start_pos] + 
                            f'const MOCK_DATA = {mock_data_content};' + 
                            db_service_content[end_pos:]
                        )
                    else:
                        # Fallback: use original pattern
                        pattern = r'const MOCK_DATA = \{[\s\S]*?\};'
                        updated_content = re.sub(pattern, f'const MOCK_DATA = {mock_data_content};', db_service_content)
                else:
                    # Fallback: use original pattern
                    pattern = r'const MOCK_DATA = \{[\s\S]*?\};'
                    updated_content = re.sub(pattern, f'const MOCK_DATA = {mock_data_content};', db_service_content)
                
                # Write the updated content to ZIP
                zip_file.writestr('src/services/db_service.js', updated_content)
            else:
                # Fallback: add data files with real Odoo data
                data_files = self._generate_odoo_data_files()
                for file_name, file_content in data_files.items():
                    zip_file.writestr(f'data/{file_name}', file_content)
        
        # Prepare ZIP data
        zip_buffer.seek(0)
        zip_data = zip_buffer.read()
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f'pos_standalone_{self.name.replace(" ", "_")}.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_data),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/zip',
        })
        
        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    def _generate_odoo_data_files(self):
        """Generate data files from Odoo database in the same format as export"""
        # Create main export data structure
        export_data = {
            "version": 6,
            "timestamp": datetime.datetime.now().isoformat(),
            "tables": {}
        }
        
        # Add all tables in the same format as exportDB()
        export_data["tables"]["config"] = [{"key": "db_initialized", "value": True}]
        export_data["tables"]["products"] = self._get_odoo_products()
        export_data["tables"]["categories"] = self._get_odoo_categories()
        export_data["tables"]["customers"] = self._get_odoo_customers()
        export_data["tables"]["payment_methods"] = self._get_odoo_payment_methods()
        export_data["tables"]["pricelists"] = self._get_odoo_pricelists()
        export_data["tables"]["pricelist_items"] = self._get_odoo_pricelist_items()
        export_data["tables"]["sync_queue"] = []
        
        # Add POS configuration as config entries
        pos_config = self._get_pos_config_data()['pos_config']
        for key, value in pos_config.items():
            export_data["tables"]["config"].append({"key": key, "value": value})
        
        # Generate single data file with export format
        data_files = {
            'pos_data.json': json.dumps(export_data, indent=2, default=str)
        }
        
        return data_files

    def _get_pos_config_data(self):
        """Get current POS configuration"""
        return {
            'pos_config': {
                'name': self.name,
                'currency_id': self.currency_id.id if self.currency_id else None,
                'currency_name': self.currency_id.name if self.currency_id else 'IDR',
                'currency_symbol': self.currency_symbol,
                'thousand_separator': self.thousand_separator,
                'decimal_separator': self.decimal_separator,
                'rounding_method': self.rounding_method,
                'rounding_factor': self.rounding_factor,
                'business_name': self.business_name or 'POS Standalone',
                'business_address': self.business_address or '',
                'business_phone': self.business_phone or '',
                'business_email': self.business_email or '',
                'receipt_header': self.receipt_header or '=== POS RECEIPT ===',
                'receipt_footer': self.receipt_footer or 'Thank you for shopping!',
                'security_pin': self.security_pin or '',
                'sync_interval': self.sync_interval,
                'server_url': self.server_url,
                'database_name': self.database_name,
            }
        }

    def _get_odoo_products(self):
        """Get actual products from Odoo database in the same format as export"""
        products = self.env['product.product'].search([
            ('sale_ok', '=', True),
            ('available_in_pos', '=', True)
        ], limit=100)  # Limit to prevent large files
        
        # Get XML IDs using export_data
        xml_ids = products.export_data(['id']).get('datas', [])
        
        return [{
            'id': product.id,
            'xml_id': xml_ids[i][0] if i < len(xml_ids) else None,
            'display_name': product.name,
            'barcode': product.barcode or '',
            'default_code': product.default_code or '',
            'categ_id': product.categ_id.id,
            'list_price': product.list_price,
            'stock_qty': 0,  # Will be updated if stock module is available
            'active': product.active,
            'image_1920': None  # File image field
        } for i, product in enumerate(products)]

    def _get_odoo_categories(self):
        """Get actual product categories from Odoo in the same format as export"""
        categories = self.env['product.category'].search([], limit=50)
        
        # Get XML IDs using export_data
        xml_ids = categories.export_data(['id']).get('datas', [])
        
        return [{
            'id': cat.id,
            'xml_id': xml_ids[i][0] if i < len(xml_ids) else None,
            'name': cat.name,
            'parent_id': cat.parent_id.id if cat.parent_id else None
        } for i, cat in enumerate(categories)]

    def _get_odoo_customers(self):
        """Get actual customers from Odoo in the same format as export"""
        customers = self.env['res.partner'].search([
            ('customer_rank', '>', 0)
        ], limit=50)
        
        # Get XML IDs using export_data
        xml_ids = customers.export_data(['id']).get('datas', [])
        
        return [{
            'id': customer.id,
            'xml_id': xml_ids[i][0] if i < len(xml_ids) else None,
            'name': customer.name,
            'email': customer.email or '',
            'phone': customer.phone or '',
            'pricelist_id': customer.property_product_pricelist.id if customer.property_product_pricelist else None
        } for i, customer in enumerate(customers)]

    def _get_odoo_payment_methods(self):
        """Get payment methods from Odoo"""
        payment_method_records = self.env['pos.payment.method'].search([('active', '=', True)])
        
        # Get XML IDs using export_data
        xml_ids = payment_method_records.export_data(['id']).get('datas', [])
        
        payment_methods = []
        for i, method in enumerate(payment_method_records):
            payment_data = {
                'id': method.id,
                'xml_id': xml_ids[i][0] if i < len(xml_ids) else None,
                'name': method.name,
                'type': getattr(method, 'type', 'cash'),
                'active': method.active
            }
            payment_methods.append(payment_data)
        
        return payment_methods

    def _get_odoo_pricelists(self):
        """Get pricelists from Odoo"""
        pricelist_records = self.env['product.pricelist'].search([('active', '=', True)])
        
        # Get XML IDs using export_data
        xml_ids = pricelist_records.export_data(['id']).get('datas', [])
        
        pricelists = []
        for i, pricelist in enumerate(pricelist_records):
            pricelist_data = {
                'id': pricelist.id,
                'xml_id': xml_ids[i][0] if i < len(xml_ids) else None,
                'name': pricelist.name,
                'active': pricelist.active
            }
            pricelists.append(pricelist_data)
        
        return pricelists

    def _get_odoo_pricelist_items(self):
        """Get pricelist items from Odoo"""
        # Get some sample pricelist items (remove active filter as it may not exist)
        item_records = self.env['product.pricelist.item'].search([], limit=10)
        
        # Get XML IDs using export_data
        xml_ids = item_records.export_data(['id']).get('datas', [])
        
        pricelist_items = []
        for i, item in enumerate(item_records):
            item_data = {
                'id': item.id,
                'xml_id': xml_ids[i][0] if i < len(xml_ids) else None,
                'pricelist_id': item.pricelist_id.id if item.pricelist_id else None,
                'product_id': item.product_id.id if item.product_id else None,
                'categ_id': item.categ_id.id if item.categ_id else None,
                'applied_on': getattr(item, 'applied_on', '3_global'),
                'compute_price': getattr(item, 'compute_price', 'fixed'),
                'percent_price': getattr(item, 'percent_price', 0),
                'fixed_price': getattr(item, 'fixed_price', 0),
                'min_quantity': getattr(item, 'min_quantity', 1)
            }
            pricelist_items.append(item_data)
        
        return pricelist_items

    def _generate_mock_data_js(self):
        """Generate JavaScript mock data from Odoo database"""
        # Get actual data from Odoo
        categories = self._get_odoo_categories()
        products = self._get_odoo_products()
        pricelists = self._get_odoo_pricelists()
        pricelist_items = self._get_odoo_pricelist_items()
        payment_methods = self._get_odoo_payment_methods()
        customers = self._get_odoo_customers()
        
        # Get POS configuration
        pos_config = self._get_pos_config_data()['pos_config']
        
        # Build JavaScript object structure with config
        mock_data = {
            'config': {
                'pos_config': pos_config
            },
            'categories': categories,
            'products': products,
            'pricelists': pricelists,
            'pricelist_items': pricelist_items,
            'payment_methods': payment_methods,
            'customers': customers
        }
        
        # Convert to JavaScript format
        return json.dumps(mock_data, indent=4)




