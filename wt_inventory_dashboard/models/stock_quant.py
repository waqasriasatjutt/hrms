# -*- coding: utf-8 -*-
from datetime import date, timedelta
from odoo import api, models


def _date_range(period, date_from=None, date_to=None):
    today = date.today()
    if period == 'today':
        return str(today), str(today)
    elif period == 'yesterday':
        d = today - timedelta(days=1)
        return str(d), str(d)
    elif period == 'week':
        return str(today - timedelta(days=6)), str(today)
    elif period == 'last_week':
        end = today - timedelta(days=today.weekday() + 1)
        return str(end - timedelta(days=6)), str(end)
    elif period == 'month':
        return str(today.replace(day=1)), str(today)
    elif period == 'last_month':
        first_this = today.replace(day=1)
        last_prev = first_this - timedelta(days=1)
        return str(last_prev.replace(day=1)), str(last_prev)
    elif period == 'quarter':
        q_start_month = ((today.month - 1) // 3) * 3 + 1
        return str(today.replace(month=q_start_month, day=1)), str(today)
    elif period == 'year':
        return str(today.replace(month=1, day=1)), str(today)
    elif period == 'custom' and date_from and date_to:
        return date_from, date_to
    return str(today.replace(day=1)), str(today)


def _prev_range(d_from_str, d_to_str):
    try:
        df = date.fromisoformat(d_from_str)
        dt = date.fromisoformat(d_to_str)
        delta = (dt - df).days + 1
        return str(df - timedelta(days=delta)), str(df - timedelta(days=1))
    except Exception:
        return d_from_str, d_to_str


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _fmt(self, val):
        sym = self.env.company.currency_id.symbol or '$'
        v = float(val or 0)
        if abs(v) >= 1_000_000:
            return f"{sym} {v/1_000_000:.1f}M"
        if abs(v) >= 1_000:
            return f"{sym} {v/1_000:.1f}K"
        return f"{sym} {v:,.2f}"

    @api.model
    def get_inventory_kpis(self, period='month', date_from='', date_to='', filter_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        # Products in stock (internal locations)
        cr.execute("""
            SELECT COUNT(DISTINCT sq.product_id)
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE sl.usage = 'internal'
              AND sq.company_id = %s
              AND sq.quantity > 0
        """, (company_id,))
        products_in_stock = int(cr.fetchone()[0] or 0)

        # Stock value from valuation layer
        cr.execute("""
            SELECT COALESCE(SUM(svl.value), 0)
            FROM stock_valuation_layer svl
            WHERE svl.company_id = %s
              AND svl.create_date::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        stock_value = float(cr.fetchone()[0] or 0)

        # Out of stock (qty <= 0 in internal)
        cr.execute("""
            SELECT COUNT(DISTINCT sq.product_id)
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE sl.usage = 'internal'
              AND sq.company_id = %s
              AND sq.quantity <= 0
        """, (company_id,))
        out_of_stock = int(cr.fetchone()[0] or 0)

        # Pending receipts qty
        cr.execute("""
            SELECT COALESCE(SUM(sm.product_uom_qty), 0)
            FROM stock_move sm
            JOIN stock_picking sp ON sp.id = sm.picking_id
            JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            WHERE sm.company_id = %s
              AND spt.code = 'incoming'
              AND sp.state IN ('confirmed', 'assigned', 'waiting')
              AND sm.state NOT IN ('done', 'cancel')
        """, (company_id,))
        pending_receipts = int(cr.fetchone()[0] or 0)

        # Pending deliveries qty
        cr.execute("""
            SELECT COALESCE(SUM(sm.product_uom_qty), 0)
            FROM stock_move sm
            JOIN stock_picking sp ON sp.id = sm.picking_id
            JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
            WHERE sm.company_id = %s
              AND spt.code = 'outgoing'
              AND sp.state IN ('confirmed', 'assigned', 'waiting')
              AND sm.state NOT IN ('done', 'cancel')
        """, (company_id,))
        pending_deliveries = int(cr.fetchone()[0] or 0)

        # Stock moves done in period
        cr.execute("""
            SELECT COUNT(*)
            FROM stock_move sm
            WHERE sm.company_id = %s
              AND sm.state = 'done'
              AND sm.date::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        stock_moves = int(cr.fetchone()[0] or 0)

        # Average product value via valuation layer
        cr.execute("""
            SELECT COALESCE(SUM(svl.value) / NULLIF(COUNT(DISTINCT svl.product_id), 0), 0)
            FROM stock_valuation_layer svl
            WHERE svl.company_id = %s
        """, (company_id,))
        avg_product_value = float(cr.fetchone()[0] or 0)

        # Locations with stock
        cr.execute("""
            SELECT COUNT(DISTINCT sq.location_id)
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            WHERE sl.usage = 'internal'
              AND sq.company_id = %s
              AND sq.quantity > 0
        """, (company_id,))
        locations_with_stock = int(cr.fetchone()[0] or 0)

        # Low stock: products where on-hand qty < reorder min qty (orderpoint)
        cr.execute("""
            SELECT COUNT(DISTINCT sop.product_id)
            FROM stock_warehouse_orderpoint sop
            WHERE sop.company_id = %s
              AND COALESCE((
                  SELECT SUM(sq.quantity) FROM stock_quant sq
                  WHERE sq.product_id = sop.product_id
                    AND sq.location_id = sop.location_id
              ), 0) < sop.product_min_qty
        """, (company_id,))
        low_stock_alerts = int(cr.fetchone()[0] or 0)

        return {
            'period_label': f"{d_from} → {d_to}",
            'products_in_stock': products_in_stock,
            'stock_value': self._fmt(stock_value),
            'low_stock_alerts': low_stock_alerts,
            'out_of_stock': out_of_stock,
            'pending_receipts': pending_receipts,
            'pending_deliveries': pending_deliveries,
            'stock_moves': stock_moves,
            'avg_product_value': self._fmt(avg_product_value),
            'locations_with_stock': locations_with_stock,
        }

    @api.model
    def get_inventory_movement_trend(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        try:
            df = date.fromisoformat(d_from)
            dt = date.fromisoformat(d_to)
            delta_days = (dt - df).days
        except Exception:
            delta_days = 30

        if delta_days <= 90:
            cr.execute("""
                SELECT sm.date::date AS day,
                       COALESCE(SUM(CASE WHEN sl_dest.usage = 'internal' AND sl_src.usage != 'internal' THEN sm.product_uom_qty ELSE 0 END), 0) AS incoming,
                       COALESCE(SUM(CASE WHEN sl_src.usage = 'internal' AND sl_dest.usage != 'internal' THEN sm.product_uom_qty ELSE 0 END), 0) AS outgoing
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                WHERE sm.company_id = %s
                  AND sm.state = 'done'
                  AND sm.date::date BETWEEN %s AND %s
                GROUP BY 1 ORDER BY 1
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            rm = {str(r[0]): (float(r[1]), float(r[2])) for r in rows}
            try:
                all_days = [df + timedelta(days=i) for i in range(delta_days + 1)]
            except Exception:
                all_days = []
            labels = [d.strftime('%d %b') for d in all_days]
            incoming = [rm.get(str(d), (0, 0))[0] for d in all_days]
            outgoing = [rm.get(str(d), (0, 0))[1] for d in all_days]
        else:
            cr.execute("""
                SELECT TO_CHAR(sm.date, 'YYYY-MM') AS mon,
                       TO_CHAR(sm.date, 'Mon YY') AS mon_label,
                       COALESCE(SUM(CASE WHEN sl_dest.usage = 'internal' AND sl_src.usage != 'internal' THEN sm.product_uom_qty ELSE 0 END), 0),
                       COALESCE(SUM(CASE WHEN sl_src.usage = 'internal' AND sl_dest.usage != 'internal' THEN sm.product_uom_qty ELSE 0 END), 0)
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                WHERE sm.company_id = %s AND sm.state = 'done'
                  AND sm.date::date BETWEEN %s AND %s
                GROUP BY 1, 2 ORDER BY 1
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            labels = [r[1] for r in rows]
            incoming = [float(r[2]) for r in rows]
            outgoing = [float(r[3]) for r in rows]

        return {'labels': labels, 'incoming': incoming, 'outgoing': outgoing}

    @api.model
    def get_inventory_top_by_value(self, period='month', date_from='', date_to=''):
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT pt.name->>'en_US' AS product_name,
                   COALESCE(SUM(svl.value), 0) AS total_value
            FROM stock_valuation_layer svl
            JOIN product_product pp ON pp.id = svl.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE svl.company_id = %s
            GROUP BY pt.name->>'en_US'
            ORDER BY total_value DESC
            LIMIT 10
        """, (company_id,))
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_inventory_by_category(self, period='month', date_from='', date_to=''):
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT pc.name AS cat_name,
                   COALESCE(SUM(sq.quantity), 0) AS qty
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            JOIN product_product pp ON pp.id = sq.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN product_category pc ON pc.id = pt.categ_id
            WHERE sl.usage = 'internal'
              AND sq.company_id = %s
              AND sq.quantity > 0
            GROUP BY pc.name
            ORDER BY qty DESC
            LIMIT 10
        """, (company_id,))
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_inventory_comparison(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        prev_from, prev_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr

        def get_moves(df, dt):
            cr.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN sl_dest.usage='internal' AND sl_src.usage!='internal' THEN sm.product_uom_qty ELSE 0 END), 0) AS recv,
                    COALESCE(SUM(CASE WHEN sl_src.usage='internal' AND sl_dest.usage!='internal' THEN sm.product_uom_qty ELSE 0 END), 0) AS sent,
                    COUNT(*)
                FROM stock_move sm
                JOIN stock_location sl_src ON sl_src.id = sm.location_id
                JOIN stock_location sl_dest ON sl_dest.id = sm.location_dest_id
                WHERE sm.company_id = %s AND sm.state = 'done'
                  AND sm.date::date BETWEEN %s AND %s
            """, (company_id, df, dt))
            row = cr.fetchone()
            return {'received': float(row[0] or 0), 'sent': float(row[1] or 0), 'moves': int(row[2] or 0)}

        curr = get_moves(d_from, d_to)
        prev = get_moves(prev_from, prev_to)

        def pct(c, p):
            if p == 0:
                return None
            return round((c - p) / p * 100, 1)

        return {
            'current_label': f"{d_from} → {d_to}",
            'prev_label': f"{prev_from} → {prev_to}",
            'metrics': [
                {'name': 'Received (qty)', 'current': str(int(curr['received'])), 'prev': str(int(prev['received'])), 'pct': pct(curr['received'], prev['received'])},
                {'name': 'Sent (qty)', 'current': str(int(curr['sent'])), 'prev': str(int(prev['sent'])), 'pct': pct(curr['sent'], prev['sent'])},
                {'name': 'Total Moves', 'current': str(curr['moves']), 'prev': str(prev['moves']), 'pct': pct(curr['moves'], prev['moves'])},
            ],
            'labels': ['Received', 'Sent', 'Total Moves'],
            'current_vals': [curr['received'], curr['sent'], curr['moves']],
            'prev_vals': [prev['received'], prev['sent'], prev['moves']],
        }

    @api.model
    def get_inventory_low_stock_items(self, period='month', date_from='', date_to=''):
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT sop.id,
                   pt.name->>'en_US' AS product_name,
                   COALESCE((
                       SELECT SUM(sq.quantity) FROM stock_quant sq
                       WHERE sq.product_id = sop.product_id
                         AND sq.location_id = sop.location_id
                   ), 0) AS qty_on_hand,
                   sop.product_min_qty,
                   sop.product_max_qty
            FROM stock_warehouse_orderpoint sop
            JOIN product_product pp ON pp.id = sop.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE sop.company_id = %s
              AND COALESCE((
                  SELECT SUM(sq2.quantity) FROM stock_quant sq2
                  WHERE sq2.product_id = sop.product_id
                    AND sq2.location_id = sop.location_id
              ), 0) < sop.product_min_qty
            ORDER BY (sop.product_min_qty - COALESCE((
                SELECT SUM(sq3.quantity) FROM stock_quant sq3
                WHERE sq3.product_id = sop.product_id
                  AND sq3.location_id = sop.location_id
            ), 0)) DESC
            LIMIT 20
        """, (company_id,))
        rows = cr.fetchall()
        return [{
            'id': r[0],
            'name': r[1] or 'Unknown',
            'on_hand': float(r[2] or 0),
            'min_qty': float(r[3] or 0),
            'max_qty': float(r[4] or 0),
            'shortage': float((r[3] or 0) - (r[2] or 0)),
        } for r in rows]
