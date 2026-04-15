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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _fmt(self, val):
        sym = self.env.company.currency_id.symbol or '$'
        v = float(val or 0)
        if abs(v) >= 1_000_000:
            return f"{sym} {v/1_000_000:.1f}M"
        if abs(v) >= 1_000:
            return f"{sym} {v/1_000:.1f}K"
        return f"{sym} {v:,.2f}"

    @api.model
    def get_purchase_kpis(self, period='month', date_from='', date_to='', filter_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        # Total spend + count + avg + tax
        cr.execute("""
            SELECT
                COALESCE(SUM(po.amount_untaxed), 0),
                COUNT(*),
                COALESCE(AVG(po.amount_untaxed), 0),
                COALESCE(SUM(po.amount_tax), 0)
            FROM purchase_order po
            WHERE po.company_id = %s
              AND po.state IN ('purchase', 'done')
              AND po.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        row = cr.fetchone()
        total_spend = float(row[0] or 0)
        purchase_orders = int(row[1] or 0)
        avg_po_value = float(row[2] or 0)
        tax_amount = float(row[3] or 0)

        # RFQs
        cr.execute("""
            SELECT COUNT(*) FROM purchase_order po
            WHERE po.company_id = %s AND po.state IN ('draft','sent')
              AND po.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        rfqs = int(cr.fetchone()[0] or 0)

        # Vendors
        cr.execute("""
            SELECT COUNT(DISTINCT po.partner_id) FROM purchase_order po
            WHERE po.company_id = %s AND po.state IN ('purchase','done')
              AND po.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        vendors = int(cr.fetchone()[0] or 0)

        # Items ordered
        cr.execute("""
            SELECT COALESCE(SUM(pol.product_qty), 0)
            FROM purchase_order_line pol
            JOIN purchase_order po ON po.id = pol.order_id
            WHERE po.company_id = %s AND po.state IN ('purchase','done')
              AND po.date_order::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        items_ordered = int(cr.fetchone()[0] or 0)

        # Bills to process (draft vendor bills)
        cr.execute("""
            SELECT COUNT(*)
            FROM account_move am
            WHERE am.company_id = %s AND am.state = 'draft'
              AND am.move_type = 'in_invoice'
        """, (company_id,))
        bills_to_process = int(cr.fetchone()[0] or 0)

        # Overdue bills
        cr.execute("""
            SELECT COUNT(*), COALESCE(SUM(am.amount_residual), 0)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'in_invoice'
              AND am.state = 'posted'
              AND am.payment_state NOT IN ('paid', 'reversed')
              AND am.invoice_date_due < CURRENT_DATE
        """, (company_id,))
        ob_row = cr.fetchone()
        overdue_bills = int(ob_row[0] or 0)

        return {
            'period_label': f"{d_from} → {d_to}",
            'total_spend': self._fmt(total_spend),
            'purchase_orders': purchase_orders,
            'avg_po_value': self._fmt(avg_po_value),
            'rfqs': rfqs,
            'vendors': vendors,
            'items_ordered': items_ordered,
            'bills_to_process': bills_to_process,
            'overdue_bills': overdue_bills,
            'tax_amount': self._fmt(tax_amount),
        }

    @api.model
    def get_purchase_trend(self, period='month', date_from='', date_to=''):
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
                SELECT po.date_order::date, COALESCE(SUM(po.amount_untaxed), 0), COUNT(*)
                FROM purchase_order po
                WHERE po.company_id = %s AND po.state IN ('purchase','done')
                  AND po.date_order::date BETWEEN %s AND %s
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
                SELECT TO_CHAR(po.date_order,'YYYY-MM'), TO_CHAR(po.date_order,'Mon YY'),
                       COALESCE(SUM(po.amount_untaxed), 0), COUNT(*)
                FROM purchase_order po
                WHERE po.company_id = %s AND po.state IN ('purchase','done')
                  AND po.date_order::date BETWEEN %s AND %s
                GROUP BY 1, 2 ORDER BY 1
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            labels = [r[1] for r in rows]
            values = [float(r[2]) for r in rows]
            counts = [int(r[3]) for r in rows]

        return {'labels': labels, 'values': values, 'counts': counts}

    @api.model
    def get_purchase_top_vendors(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT rp.name, COALESCE(SUM(po.amount_untaxed), 0) AS spend, COUNT(*) AS orders
            FROM purchase_order po
            JOIN res_partner rp ON rp.id = po.partner_id
            WHERE po.company_id = %s AND po.state IN ('purchase','done')
              AND po.date_order::date BETWEEN %s AND %s
            GROUP BY rp.name ORDER BY spend DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] for r in rows], 'values': [float(r[1]) for r in rows], 'counts': [int(r[2]) for r in rows]}

    @api.model
    def get_purchase_top_products(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT pt.name->>'en_US' AS pname,
                   COALESCE(SUM(pol.product_qty), 0) AS qty
            FROM purchase_order_line pol
            JOIN purchase_order po ON po.id = pol.order_id
            JOIN product_product pp ON pp.id = pol.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE po.company_id = %s AND po.state IN ('purchase','done')
              AND po.date_order::date BETWEEN %s AND %s
            GROUP BY pt.name->>'en_US' ORDER BY qty DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_purchase_spend_by_category(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT pc.name AS cat_name,
                   COALESCE(SUM(pol.price_subtotal), 0) AS spend
            FROM purchase_order_line pol
            JOIN purchase_order po ON po.id = pol.order_id
            JOIN product_product pp ON pp.id = pol.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN product_category pc ON pc.id = pt.categ_id
            WHERE po.company_id = %s AND po.state IN ('purchase','done')
              AND po.date_order::date BETWEEN %s AND %s
            GROUP BY pc.name ORDER BY spend DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_purchase_rfq_vs_orders(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT TO_CHAR(po.date_order,'YYYY-MM') AS mon,
                   TO_CHAR(po.date_order,'Mon YY') AS mon_label,
                   COUNT(CASE WHEN po.state IN ('draft','sent') THEN 1 END) AS rfqs,
                   COUNT(CASE WHEN po.state IN ('purchase','done') THEN 1 END) AS orders
            FROM purchase_order po
            WHERE po.company_id = %s AND po.date_order::date BETWEEN %s AND %s
            GROUP BY 1, 2 ORDER BY 1
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {
            'labels': [r[1] for r in rows],
            'rfqs': [int(r[2]) for r in rows],
            'orders': [int(r[3]) for r in rows],
        }

    @api.model
    def get_purchase_recent_pos(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        sym = self.env.company.currency_id.symbol or '$'

        cr.execute("""
            SELECT po.id, po.name, rp.name, po.date_order::date,
                   po.amount_untaxed, po.amount_total, po.state
            FROM purchase_order po
            LEFT JOIN res_partner rp ON rp.id = po.partner_id
            WHERE po.company_id = %s AND po.date_order::date BETWEEN %s AND %s
            ORDER BY po.date_order DESC LIMIT 20
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()

        def fmt(v):
            return f"{sym} {float(v or 0):,.2f}"

        state_map = {'draft': 'RFQ', 'sent': 'Sent', 'purchase': 'PO', 'done': 'Done', 'cancel': 'Cancelled'}
        return [{'id': r[0], 'name': r[1], 'vendor': r[2] or 'N/A', 'date': str(r[3]) if r[3] else '',
                 'subtotal': fmt(r[4]), 'total': fmt(r[5]),
                 'state': state_map.get(r[6], r[6])} for r in rows]

    @api.model
    def get_purchase_vendor_stats(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        sym = self.env.company.currency_id.symbol or '$'

        cr.execute("""
            SELECT rp.name, COUNT(*) AS orders, COALESCE(SUM(po.amount_untaxed), 0) AS spend
            FROM purchase_order po
            JOIN res_partner rp ON rp.id = po.partner_id
            WHERE po.company_id = %s AND po.state IN ('purchase','done')
              AND po.date_order::date BETWEEN %s AND %s
            GROUP BY rp.name ORDER BY spend DESC LIMIT 15
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()

        def fmt(v):
            v = float(v)
            if abs(v) >= 1_000_000:
                return f"{sym} {v/1_000_000:.1f}M"
            if abs(v) >= 1_000:
                return f"{sym} {v/1_000:.1f}K"
            return f"{sym} {v:,.2f}"

        return [{'name': r[0], 'orders': int(r[1]), 'spend': fmt(r[2]),
                 'avg': fmt(r[2] / r[1]) if r[1] > 0 else f"{sym} 0.00"} for r in rows]

    @api.model
    def get_purchase_comparison(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        prev_from, prev_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr
        sym = self.env.company.currency_id.symbol or '$'

        def get_data(df, dt):
            cr.execute("""
                SELECT COALESCE(SUM(amount_untaxed), 0), COUNT(*)
                FROM purchase_order
                WHERE company_id = %s AND state IN ('purchase','done')
                  AND date_order::date BETWEEN %s AND %s
            """, (company_id, df, dt))
            row = cr.fetchone()
            return {'spend': float(row[0] or 0), 'orders': int(row[1] or 0)}

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
                {'name': 'Spend', 'current': fmt(curr['spend']), 'prev': fmt(prev['spend']), 'pct': pct(curr['spend'], prev['spend'])},
                {'name': 'Orders', 'current': str(curr['orders']), 'prev': str(prev['orders']), 'pct': pct(curr['orders'], prev['orders'])},
            ],
            'labels': ['Spend', 'Orders'],
            'current_vals': [curr['spend'], curr['orders']],
            'prev_vals': [prev['spend'], prev['orders']],
        }
