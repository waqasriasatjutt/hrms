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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _fmt(self, val):
        sym = self.env.company.currency_id.symbol or '$'
        v = float(val or 0)
        if abs(v) >= 1_000_000:
            return f"{sym} {v/1_000_000:.1f}M"
        if abs(v) >= 1_000:
            return f"{sym} {v/1_000:.1f}K"
        return f"{sym} {v:,.2f}"

    @api.model
    def get_sale_kpis(self, period='month', date_from='', date_to='', filter_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        # Revenue + confirmed count + avg + tax
        cr.execute("""
            SELECT
                COALESCE(SUM(so.amount_untaxed), 0) AS revenue,
                COUNT(*) AS confirmed,
                COALESCE(AVG(so.amount_untaxed), 0) AS avg_order,
                COALESCE(SUM(so.amount_tax), 0) AS tax
            FROM sale_order so
            WHERE so.company_id = %s
              AND so.state IN ('sale', 'done')
              AND so.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        row = cr.fetchone()
        total_revenue = float(row[0] or 0)
        confirmed_orders = int(row[1] or 0)
        avg_order_value = float(row[2] or 0)
        tax_collected = float(row[3] or 0)

        # Quotations
        cr.execute("""
            SELECT COUNT(*)
            FROM sale_order so
            WHERE so.company_id = %s
              AND so.state IN ('draft', 'sent')
              AND so.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        quotations = int(cr.fetchone()[0] or 0)

        # Distinct customers
        cr.execute("""
            SELECT COUNT(DISTINCT so.partner_id)
            FROM sale_order so
            WHERE so.company_id = %s
              AND so.state IN ('sale', 'done')
              AND so.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        customers = int(cr.fetchone()[0] or 0)

        # Items sold
        cr.execute("""
            SELECT COALESCE(SUM(sol.product_uom_qty), 0)
            FROM sale_order_line sol
            JOIN sale_order so ON so.id = sol.order_id
            WHERE so.company_id = %s
              AND so.state IN ('sale', 'done')
              AND so.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        items_sold = int(cr.fetchone()[0] or 0)

        # Conversion rate
        total = confirmed_orders + quotations
        conversion_rate = round(confirmed_orders / total * 100, 1) if total > 0 else 0.0

        return {
            'period_label': f"{d_from} → {d_to}",
            'total_revenue': self._fmt(total_revenue),
            'confirmed_orders': confirmed_orders,
            'avg_order_value': self._fmt(avg_order_value),
            'quotations': quotations,
            'customers': customers,
            'items_sold': items_sold,
            'conversion_rate': f"{conversion_rate}%",
            'tax_collected': self._fmt(tax_collected),
            'pending_delivery': 0,
        }

    @api.model
    def get_sale_trend(self, period='month', date_from='', date_to=''):
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
                SELECT so.date_order::date, COALESCE(SUM(so.amount_untaxed), 0), COUNT(*)
                FROM sale_order so
                WHERE so.company_id = %s AND so.state IN ('sale','done')
                  AND so.date_order::date BETWEEN %s AND %s
                GROUP BY 1 ORDER BY 1
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            rm = {str(r[0]): (float(r[1]), int(r[2])) for r in rows}
            try:
                all_days = [df + timedelta(days=i) for i in range(delta_days + 1)]
            except Exception:
                all_days = []
            labels = [d.strftime('%d %b') for d in all_days]
            values = [rm.get(str(d), (0, 0))[0] for d in all_days]
            counts = [rm.get(str(d), (0, 0))[1] for d in all_days]
        else:
            cr.execute("""
                SELECT TO_CHAR(so.date_order,'YYYY-MM'), TO_CHAR(so.date_order,'Mon YY'),
                       COALESCE(SUM(so.amount_untaxed), 0), COUNT(*)
                FROM sale_order so
                WHERE so.company_id = %s AND so.state IN ('sale','done')
                  AND so.date_order::date BETWEEN %s AND %s
                GROUP BY 1, 2 ORDER BY 1
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            labels = [r[1] for r in rows]
            values = [float(r[2]) for r in rows]
            counts = [int(r[3]) for r in rows]

        return {'labels': labels, 'values': values, 'counts': counts}

    @api.model
    def get_sale_top_products_qty(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT pt.name->>'en_US' AS pname,
                   COALESCE(SUM(sol.product_uom_qty), 0) AS qty
            FROM sale_order_line sol
            JOIN sale_order so ON so.id = sol.order_id
            JOIN product_product pp ON pp.id = sol.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE so.company_id = %s AND so.state IN ('sale','done')
              AND so.date_order::date BETWEEN %s AND %s
            GROUP BY pt.name->>'en_US'
            ORDER BY qty DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_sale_top_products_revenue(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT pt.name->>'en_US' AS pname,
                   COALESCE(SUM(sol.price_subtotal), 0) AS revenue
            FROM sale_order_line sol
            JOIN sale_order so ON so.id = sol.order_id
            JOIN product_product pp ON pp.id = sol.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE so.company_id = %s AND so.state IN ('sale','done')
              AND so.date_order::date BETWEEN %s AND %s
            GROUP BY pt.name->>'en_US'
            ORDER BY revenue DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_sale_top_customers(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT rp.name, COALESCE(SUM(so.amount_untaxed), 0) AS revenue, COUNT(*) AS orders
            FROM sale_order so
            JOIN res_partner rp ON rp.id = so.partner_id
            WHERE so.company_id = %s AND so.state IN ('sale','done')
              AND so.date_order::date BETWEEN %s AND %s
            GROUP BY rp.name ORDER BY revenue DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] for r in rows], 'values': [float(r[1]) for r in rows], 'counts': [int(r[2]) for r in rows]}

    @api.model
    def get_sale_salesperson_stats(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        sym = self.env.company.currency_id.symbol or '$'

        cr.execute("""
            SELECT rp.name, COUNT(*) AS orders, COALESCE(SUM(so.amount_untaxed), 0) AS revenue
            FROM sale_order so
            JOIN res_users ru ON ru.id = so.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE so.company_id = %s AND so.state IN ('sale','done')
              AND so.date_order::date BETWEEN %s AND %s
            GROUP BY rp.name ORDER BY revenue DESC LIMIT 15
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()

        def fmt(v):
            v = float(v)
            if abs(v) >= 1_000_000:
                return f"{sym} {v/1_000_000:.1f}M"
            if abs(v) >= 1_000:
                return f"{sym} {v/1_000:.1f}K"
            return f"{sym} {v:,.2f}"

        return [{'name': r[0], 'orders': int(r[1]), 'revenue': fmt(r[2]),
                 'avg': fmt(r[2] / r[1]) if r[1] > 0 else f"{sym} 0.00"} for r in rows]

    @api.model
    def get_sale_recent_orders(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        sym = self.env.company.currency_id.symbol or '$'

        cr.execute("""
            SELECT so.id, so.name, rp.name, so.date_order::date,
                   so.amount_untaxed, so.amount_total, so.state
            FROM sale_order so
            LEFT JOIN res_partner rp ON rp.id = so.partner_id
            WHERE so.company_id = %s
              AND so.date_order::date BETWEEN %s AND %s
            ORDER BY so.date_order DESC LIMIT 20
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()

        def fmt(v):
            return f"{sym} {float(v or 0):,.2f}"

        state_map = {'draft': 'Quotation', 'sent': 'Sent', 'sale': 'Confirmed', 'done': 'Done', 'cancel': 'Cancelled'}
        return [{'id': r[0], 'name': r[1], 'customer': r[2] or 'N/A', 'date': str(r[3]) if r[3] else '',
                 'subtotal': fmt(r[4]), 'total': fmt(r[5]),
                 'state': state_map.get(r[6], r[6])} for r in rows]

    @api.model
    def get_sale_comparison(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        prev_from, prev_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr
        sym = self.env.company.currency_id.symbol or '$'

        def get_data(df, dt):
            cr.execute("""
                SELECT COALESCE(SUM(amount_untaxed), 0), COUNT(*)
                FROM sale_order
                WHERE company_id = %s AND state IN ('sale','done')
                  AND date_order::date BETWEEN %s AND %s
            """, (company_id, df, dt))
            row = cr.fetchone()
            return {'revenue': float(row[0] or 0), 'orders': int(row[1] or 0)}

        curr = get_data(d_from, d_to)
        prev = get_data(prev_from, prev_to)

        def pct(c, p):
            return None if p == 0 else round((c - p) / p * 100, 1)

        def fmt(v):
            v = float(v)
            if abs(v) >= 1_000_000:
                return f"{sym} {v/1_000_000:.1f}M"
            if abs(v) >= 1_000:
                return f"{sym} {v/1_000:.1f}K"
            return f"{sym} {v:,.2f}"

        return {
            'current_label': f"{d_from} → {d_to}",
            'prev_label': f"{prev_from} → {prev_to}",
            'metrics': [
                {'name': 'Revenue', 'current': fmt(curr['revenue']), 'prev': fmt(prev['revenue']), 'pct': pct(curr['revenue'], prev['revenue'])},
                {'name': 'Orders', 'current': str(curr['orders']), 'prev': str(prev['orders']), 'pct': pct(curr['orders'], prev['orders'])},
            ],
            'labels': ['Revenue', 'Orders'],
            'current_vals': [curr['revenue'], curr['orders']],
            'prev_vals': [prev['revenue'], prev['orders']],
        }
