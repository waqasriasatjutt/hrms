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
    return str(today - timedelta(days=29)), str(today)


def _prev_range(d_from_str, d_to_str):
    try:
        df = date.fromisoformat(d_from_str)
        dt = date.fromisoformat(d_to_str)
        delta = (dt - df).days + 1
        return str(df - timedelta(days=delta)), str(df - timedelta(days=1))
    except Exception:
        return d_from_str, d_to_str


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # ── helpers ───────────────────────────────────────────────────────────────

    def _fmt(self, val):
        company = self.env.company
        sym = company.currency_id.symbol
        before = company.currency_id.position == 'before'
        val = float(val or 0)
        if abs(val) >= 1_000_000:
            s = f"{val / 1_000_000:.2f}M"
        elif abs(val) >= 1_000:
            s = f"{val / 1_000:.1f}K"
        else:
            s = f"{val:,.2f}"
        return f"{sym} {s}" if before else f"{s} {sym}"

    def _fmt_full(self, val):
        company = self.env.company
        sym = company.currency_id.symbol
        before = company.currency_id.position == 'before'
        s = f"{float(val or 0):,.2f}"
        return f"{sym} {s}" if before else f"{s} {sym}"

    def _xf(self, config_id=None, cashier_id=None, alias='po'):
        """Return (sql_fragment, params_list) for optional config/cashier filters."""
        sql, params = "", []
        if config_id:
            sql += f" AND {alias}.config_id = %s"
            params.append(int(config_id))
        if cashier_id:
            sql += f" AND {alias}.user_id = %s"
            params.append(int(cashier_id))
        return sql, params

    # ── KPIs ──────────────────────────────────────────────────────────────────

    @api.model
    def get_dashboard_kpis(self, period='today', date_from=None, date_to=None,
                           config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        params = [company_id, d_from, d_to] + xp

        cr.execute(f"""
            SELECT
                COALESCE(SUM(CASE WHEN amount_total > 0 THEN amount_total END), 0)              AS revenue,
                COUNT(CASE WHEN amount_total > 0 THEN 1 END)                                    AS orders,
                COUNT(CASE WHEN amount_total < 0 THEN 1 END)                                    AS refunds,
                COALESCE(SUM(CASE WHEN amount_total < 0 THEN ABS(amount_total) END), 0)         AS refund_amt,
                COALESCE(AVG(CASE WHEN amount_total > 0 THEN amount_total END), 0)              AS avg_order,
                COALESCE(SUM(CASE WHEN amount_total > 0 THEN COALESCE(amount_tax,0) END), 0)    AS tax_amt
            FROM pos_order po
            WHERE po.company_id = %s
              AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced')
              {xsql}
        """, params)
        row = cr.fetchone()

        # Gross margin + discounts from lines
        cr.execute(f"""
            SELECT
                COALESCE(SUM(pol.price_subtotal), 0)                                    AS rev_excl,
                COALESCE(SUM(COALESCE(pol.total_cost, 0)), 0)                           AS cost,
                COALESCE(SUM(pol.price_unit * pol.qty * pol.discount / 100.0), 0)       AS discount
            FROM pos_order_line pol
            JOIN pos_order po ON po.id = pol.order_id
            WHERE po.company_id = %s
              AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced')
              AND po.amount_total > 0
              {xsql}
        """, params)
        fin = cr.fetchone()
        rev_excl = float(fin[0] or 0)
        cost     = float(fin[1] or 0)
        discount = float(fin[2] or 0)
        gp       = rev_excl - cost
        margin_pct = round(gp / rev_excl * 100, 1) if rev_excl > 0 else 0.0

        # Previous period for % change
        prev_from, prev_to = _prev_range(d_from, d_to)
        cr.execute(f"""
            SELECT
                COALESCE(SUM(CASE WHEN amount_total > 0 THEN amount_total END), 0),
                COUNT(CASE WHEN amount_total > 0 THEN 1 END)
            FROM pos_order po
            WHERE po.company_id = %s
              AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced')
              {xsql}
        """, [company_id, prev_from, prev_to] + xp)
        prev = cr.fetchone()

        def pct(c, p):
            c, p = float(c or 0), float(p or 0)
            return None if p == 0 else round((c - p) / p * 100, 1)

        cr.execute(f"""
            SELECT COALESCE(SUM(pol.qty), 0)
            FROM pos_order_line pol
            JOIN pos_order po ON po.id = pol.order_id
            WHERE po.company_id = %s
              AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced')
              {xsql}
        """, params)
        items_sold = int(cr.fetchone()[0] or 0)

        cr.execute("""
            SELECT COUNT(*) FROM pos_session s
            JOIN pos_config c ON c.id = s.config_id
            WHERE c.company_id = %s AND s.state = 'opened'
        """, (company_id,))
        open_sessions = int(cr.fetchone()[0] or 0)

        return {
            'revenue':        self._fmt(row[0]),
            'orders':         int(row[1] or 0),
            'refunds':        int(row[2] or 0),
            'refund_amt':     self._fmt(row[3]),
            'avg_order':      self._fmt(row[4]),
            'tax_collected':  self._fmt(row[5]),
            'items_sold':     items_sold,
            'open_sessions':  open_sessions,
            'gross_margin':   f"{margin_pct}%",
            'total_discount': self._fmt(discount),
            'rev_change':     pct(row[0], prev[0]),
            'ord_change':     pct(row[1], prev[1]),
            'period_label':   f"{d_from} → {d_to}",
        }

    # ── Sales Trend ───────────────────────────────────────────────────────────

    @api.model
    def get_sales_trend(self, period='week', date_from=None, date_to=None,
                        config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        try:
            df = date.fromisoformat(d_from)
            dt = date.fromisoformat(d_to)
            delta_days = (dt - df).days
        except Exception:
            delta_days = 7
        params = [company_id, d_from, d_to] + xp

        if delta_days == 0:
            cr.execute(f"""
                SELECT EXTRACT(hour FROM po.date_order)::int,
                       COALESCE(SUM(po.amount_total), 0), COUNT(po.id)
                FROM pos_order po
                WHERE po.company_id = %s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
                GROUP BY 1 ORDER BY 1
            """, params)
            rm = {r[0]: (float(r[1]), int(r[2])) for r in cr.fetchall()}
            labels = [f"{h:02d}:00" for h in range(24)]
            values = [rm.get(h, (0, 0))[0] for h in range(24)]
            counts = [rm.get(h, (0, 0))[1] for h in range(24)]
        elif delta_days <= 90:
            cr.execute(f"""
                SELECT po.date_order::date, COALESCE(SUM(po.amount_total), 0), COUNT(po.id)
                FROM pos_order po
                WHERE po.company_id = %s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
                GROUP BY 1 ORDER BY 1
            """, params)
            rm = {str(r[0]): (float(r[1]), int(r[2])) for r in cr.fetchall()}
            all_days = [df + timedelta(days=i) for i in range(delta_days + 1)]
            labels = [d.strftime('%d %b') for d in all_days]
            values = [rm.get(str(d), (0, 0))[0] for d in all_days]
            counts = [rm.get(str(d), (0, 0))[1] for d in all_days]
        else:
            cr.execute(f"""
                SELECT TO_CHAR(po.date_order,'YYYY-MM'), TO_CHAR(po.date_order,'Mon YY'),
                       COALESCE(SUM(po.amount_total), 0), COUNT(po.id)
                FROM pos_order po
                WHERE po.company_id = %s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
                GROUP BY 1,2 ORDER BY 1
            """, params)
            rows = cr.fetchall()
            labels = [r[1] for r in rows]
            values = [float(r[2]) for r in rows]
            counts = [int(r[3]) for r in rows]

        return {'labels': labels, 'values': values, 'counts': counts}

    # ── Revenue vs Refunds ────────────────────────────────────────────────────

    @api.model
    def get_revenue_vs_refunds(self, period='month', date_from=None, date_to=None,
                               config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        try:
            delta_days = (date.fromisoformat(d_to) - date.fromisoformat(d_from)).days
        except Exception:
            delta_days = 30
        grp = "po.date_order::date" if delta_days <= 90 else "DATE_TRUNC('month',po.date_order)::date"
        fmt = "'DD Mon'" if delta_days <= 90 else "'Mon YY'"
        params = [company_id, d_from, d_to] + xp
        cr.execute(f"""
            SELECT TO_CHAR({grp},{fmt}),
                   COALESCE(SUM(CASE WHEN po.amount_total > 0 THEN po.amount_total END), 0),
                   COALESCE(SUM(CASE WHEN po.amount_total < 0 THEN ABS(po.amount_total) END), 0)
            FROM pos_order po
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') {xsql}
            GROUP BY {grp} ORDER BY {grp}
        """, params)
        rows = cr.fetchall()
        return {'labels': [r[0] for r in rows],
                'revenue': [float(r[1]) for r in rows],
                'refunds':  [float(r[2]) for r in rows]}

    # ── Hourly heatmap ────────────────────────────────────────────────────────

    @api.model
    def get_hourly_heatmap(self, period='month', date_from=None, date_to=None,
                           config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT EXTRACT(dow FROM po.date_order)::int,
                   EXTRACT(hour FROM po.date_order)::int,
                   COUNT(po.id)
            FROM pos_order po
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
            GROUP BY 1,2
        """, [company_id, d_from, d_to] + xp)
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        matrix = [[0] * 24 for _ in range(7)]
        for dow, h, cnt in cr.fetchall():
            matrix[int(dow)][int(h)] = int(cnt)
        return {'days': days, 'matrix': matrix}

    # ── Payment breakdown ─────────────────────────────────────────────────────

    @api.model
    def get_payment_breakdown(self, period='month', date_from=None, date_to=None,
                              config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT pm.name->>'en_US', COALESCE(SUM(pp.amount),0), COUNT(DISTINCT pp.pos_order_id)
            FROM pos_payment pp
            JOIN pos_payment_method pm ON pm.id = pp.payment_method_id
            JOIN pos_order po ON po.id = pp.pos_order_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') {xsql}
            GROUP BY 1 ORDER BY 2 DESC
        """, [company_id, d_from, d_to] + xp)
        rows = cr.fetchall()
        return {'labels': [r[0] or 'Unknown' for r in rows],
                'values': [float(r[1]) for r in rows],
                'txns':   [int(r[2]) for r in rows]}

    # ── Top products ──────────────────────────────────────────────────────────

    @api.model
    def get_top_products(self, limit=10, period='month', date_from=None, date_to=None,
                         config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT pt.name->>'en_US', SUM(pol.qty), SUM(pol.price_subtotal_incl)
            FROM pos_order_line pol
            JOIN product_product pp ON pp.id=pol.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            JOIN pos_order po ON po.id=pol.order_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') {xsql}
            GROUP BY 1 ORDER BY 2 DESC LIMIT %s
        """, [company_id, d_from, d_to] + xp + [limit])
        rows = cr.fetchall()
        return {'names':   [r[0] or 'Unknown' for r in rows],
                'qty':     [float(r[1]) for r in rows],
                'revenue': [float(r[2]) for r in rows]}

    @api.model
    def get_top_products_by_revenue(self, limit=10, period='month', date_from=None,
                                    date_to=None, config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT pt.name->>'en_US', SUM(pol.qty), SUM(pol.price_subtotal_incl)
            FROM pos_order_line pol
            JOIN product_product pp ON pp.id=pol.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            JOIN pos_order po ON po.id=pol.order_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') {xsql}
            GROUP BY 1 ORDER BY 3 DESC LIMIT %s
        """, [company_id, d_from, d_to] + xp + [limit])
        rows = cr.fetchall()
        return {'names':   [r[0] or 'Unknown' for r in rows],
                'qty':     [float(r[1]) for r in rows],
                'revenue': [float(r[2]) for r in rows]}

    # ── Top customers ─────────────────────────────────────────────────────────

    @api.model
    def get_top_customers(self, limit=10, period='month', date_from=None, date_to=None,
                          config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT rp.name, COUNT(po.id), SUM(po.amount_total)
            FROM pos_order po
            JOIN res_partner rp ON rp.id=po.partner_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
            GROUP BY 1 ORDER BY 3 DESC LIMIT %s
        """, [company_id, d_from, d_to] + xp + [limit])
        rows = cr.fetchall()
        return {'names':  [r[0] for r in rows],
                'orders': [int(r[1]) for r in rows],
                'totals': [float(r[2]) for r in rows]}

    # ── Top categories ────────────────────────────────────────────────────────

    @api.model
    def get_top_categories(self, limit=10, period='month', date_from=None, date_to=None,
                           config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        params = [company_id, d_from, d_to] + xp + [limit]
        cr.execute(f"""
            SELECT COALESCE(pc.name->>'en_US', cat.complete_name, 'Uncategorised'), SUM(pol.qty)
            FROM pos_order_line pol
            JOIN product_product pp ON pp.id=pol.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            LEFT JOIN pos_category_product_template_rel rel ON rel.product_template_id=pt.id
            LEFT JOIN pos_category pc ON pc.id=rel.pos_category_id
            LEFT JOIN product_category cat ON cat.id=pt.categ_id
            JOIN pos_order po ON po.id=pol.order_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') {xsql}
            GROUP BY 1 ORDER BY 2 DESC LIMIT %s
        """, params)
        rows = cr.fetchall()
        if not rows:
            cr.execute(f"""
                SELECT cat.complete_name, SUM(pol.qty)
                FROM pos_order_line pol
                JOIN product_product pp ON pp.id=pol.product_id
                JOIN product_template pt ON pt.id=pp.product_tmpl_id
                JOIN product_category cat ON cat.id=pt.categ_id
                JOIN pos_order po ON po.id=pol.order_id
                WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') {xsql}
                GROUP BY 1 ORDER BY 2 DESC LIMIT %s
            """, params)
            rows = cr.fetchall()
        return {'names': [r[0] for r in rows], 'qty': [float(r[1]) for r in rows]}

    # ── Salesperson stats ─────────────────────────────────────────────────────

    @api.model
    def get_salesperson_stats(self, period='month', date_from=None, date_to=None,
                              config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT rp.name, COUNT(po.id), SUM(po.amount_total), AVG(po.amount_total)
            FROM pos_order po
            JOIN res_users ru ON ru.id=po.user_id
            JOIN res_partner rp ON rp.id=ru.partner_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
            GROUP BY 1 ORDER BY 3 DESC LIMIT 20
        """, [company_id, d_from, d_to] + xp)
        return [{'name': r[0], 'orders': int(r[1]),
                 'revenue': self._fmt_full(r[2]), 'avg_sale': self._fmt_full(r[3])}
                for r in cr.fetchall()]

    # ── Recent orders ─────────────────────────────────────────────────────────

    @api.model
    def get_recent_orders(self, limit=20, period='today', date_from=None, date_to=None,
                          config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT po.name,
                   COALESCE(rp.name,'Walk-in'), COALESCE(rpu.name,'—'),
                   pc.name, po.amount_total, po.state, po.date_order
            FROM pos_order po
            LEFT JOIN res_partner rp  ON rp.id=po.partner_id
            LEFT JOIN res_users   ru  ON ru.id=po.user_id
            LEFT JOIN res_partner rpu ON rpu.id=ru.partner_id
            LEFT JOIN pos_config  pc  ON pc.id=po.config_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s {xsql}
            ORDER BY po.date_order DESC LIMIT %s
        """, [company_id, d_from, d_to] + xp + [limit])
        sl = {'draft':'Draft','paid':'Paid','done':'Done','invoiced':'Invoiced','cancel':'Cancelled'}
        return [{'name': r[0], 'customer': r[1], 'cashier': r[2], 'terminal': r[3] or '—',
                 'amount': self._fmt_full(r[4]), 'state': sl.get(r[5], r[5]),
                 'date': r[6].strftime('%d %b %H:%M') if r[6] else '',
                 'is_refund': float(r[4] or 0) < 0}
                for r in cr.fetchall()]

    # ── Session status ────────────────────────────────────────────────────────

    @api.model
    def get_session_status(self):
        cr = self._cr
        company_id = self.env.company.id
        cr.execute("""
            SELECT c.name, s.state,
                   COALESCE(SUM(po.amount_total),0), COUNT(po.id), s.start_at
            FROM pos_config c
            LEFT JOIN pos_session s ON s.config_id=c.id AND s.state='opened'
            LEFT JOIN pos_order po ON po.session_id=s.id
                AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0
            WHERE c.company_id=%s
            GROUP BY c.name, s.state, s.start_at ORDER BY c.name
        """, (company_id,))
        result = []
        for r in cr.fetchall():
            state = r[1] or 'closed'
            result.append({'name': r[0], 'state': state,
                           'label': {'opened':'Open','opening_control':'Opening'}.get(state,'Closed'),
                           'revenue': self._fmt_full(r[2]), 'orders': int(r[3] or 0),
                           'since': r[4].strftime('%H:%M') if r[4] else '—'})
        return result

    # ── POS terminals list ────────────────────────────────────────────────────

    @api.model
    def get_pos_configs(self):
        cfgs = self.env['pos.config'].search([('company_id', '=', self.env.company.id)])
        return [{'id': c.id, 'name': c.name} for c in cfgs]

    # ── Cashiers list ─────────────────────────────────────────────────────────

    @api.model
    def get_cashiers(self):
        cr = self._cr
        cr.execute("""
            SELECT DISTINCT ru.id, rp.name
            FROM pos_order po
            JOIN res_users ru ON ru.id=po.user_id
            JOIN res_partner rp ON rp.id=ru.partner_id
            WHERE po.company_id=%s AND po.state IN ('paid','done','invoiced')
            ORDER BY rp.name
        """, (self.env.company.id,))
        return [{'id': r[0], 'name': r[1]} for r in cr.fetchall()]

    # ── Financial analytics tab ───────────────────────────────────────────────

    @api.model
    def get_financial_analytics(self, period='month', date_from=None, date_to=None,
                                config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        params = [company_id, d_from, d_to] + xp

        # A. Discounts by cashier
        cr.execute(f"""
            SELECT rp.name,
                   COALESCE(SUM(pol.price_unit * pol.qty * pol.discount / 100.0), 0)
            FROM pos_order_line pol
            JOIN pos_order po ON po.id=pol.order_id
            JOIN res_users ru ON ru.id=po.user_id
            JOIN res_partner rp ON rp.id=ru.partner_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0
              AND pol.discount > 0 {xsql}
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """, params)
        dcr = cr.fetchall()

        # B. Gross margin by category (using pol.total_cost = stored historical cost)
        cr.execute(f"""
            SELECT COALESCE(pc.name->>'en_US', cat.complete_name, 'Uncategorised'),
                   COALESCE(SUM(pol.price_subtotal), 0),
                   COALESCE(SUM(COALESCE(pol.total_cost,0)), 0)
            FROM pos_order_line pol
            JOIN product_product pp ON pp.id=pol.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            LEFT JOIN pos_category_product_template_rel rel ON rel.product_template_id=pt.id
            LEFT JOIN pos_category pc ON pc.id=rel.pos_category_id
            LEFT JOIN product_category cat ON cat.id=pt.categ_id
            JOIN pos_order po ON po.id=pol.order_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """, params)
        cat_rows = cr.fetchall()

        # C. Avg revenue per order by hour of day
        cr.execute(f"""
            SELECT EXTRACT(hour FROM po.date_order)::int,
                   COALESCE(AVG(po.amount_total), 0), COUNT(po.id)
            FROM pos_order po
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
            GROUP BY 1 ORDER BY 1
        """, params)
        hr = {r[0]: (float(r[1]), int(r[2])) for r in cr.fetchall()}

        # D. Top discounted products
        cr.execute(f"""
            SELECT pt.name->>'en_US', COUNT(*),
                   COALESCE(AVG(pol.discount),0),
                   COALESCE(SUM(pol.price_unit * pol.qty * pol.discount / 100.0), 0)
            FROM pos_order_line pol
            JOIN product_product pp ON pp.id=pol.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            JOIN pos_order po ON po.id=pol.order_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0
              AND pol.discount > 0 {xsql}
            GROUP BY 1 ORDER BY 4 DESC LIMIT 10
        """, params)
        disc_rows = cr.fetchall()

        return {
            'discounts_by_cashier': {
                'names':  [r[0] for r in dcr],
                'values': [float(r[1]) for r in dcr],
            },
            'margin_by_category': {
                'names':   [r[0] for r in cat_rows],
                'margins': [round((float(r[1] or 0) - float(r[2] or 0)) / float(r[1] or 1) * 100, 1)
                            for r in cat_rows],
            },
            'avg_rev_by_hour': {
                'labels': [f"{h:02d}:00" for h in range(24)],
                'values': [hr.get(h, (0, 0))[0] for h in range(24)],
                'counts': [hr.get(h, (0, 0))[1] for h in range(24)],
            },
            'top_discounted_products': [
                {'name': r[0] or 'Unknown', 'times': int(r[1]),
                 'avg_pct': float(r[2]), 'total': self._fmt_full(r[3])}
                for r in disc_rows
            ],
        }

    # ── Period comparison tab ─────────────────────────────────────────────────

    @api.model
    def get_comparison_data(self, period='month', date_from=None, date_to=None,
                            config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        prev_from, prev_to = _prev_range(d_from, d_to)
        xsql, xp = self._xf(config_id, cashier_id)

        try:
            df = date.fromisoformat(d_from)
            dt = date.fromisoformat(d_to)
            delta_days = (dt - df).days
        except Exception:
            delta_days = 7

        def _daily(start, end):
            cr.execute(f"""
                SELECT po.date_order::date, COALESCE(SUM(po.amount_total),0), COUNT(po.id)
                FROM pos_order po
                WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
                GROUP BY 1 ORDER BY 1
            """, [company_id, start, end] + xp)
            return {str(r[0]): (float(r[1]), int(r[2])) for r in cr.fetchall()}

        def _hourly(start, end):
            cr.execute(f"""
                SELECT EXTRACT(hour FROM po.date_order)::int,
                       COALESCE(SUM(po.amount_total),0), COUNT(po.id)
                FROM pos_order po
                WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0 {xsql}
                GROUP BY 1 ORDER BY 1
            """, [company_id, start, end] + xp)
            return {r[0]: (float(r[1]), int(r[2])) for r in cr.fetchall()}

        if delta_days == 0:
            cm, pm = _hourly(d_from, d_to), _hourly(prev_from, prev_to)
            labels   = [f"{h:02d}:00" for h in range(24)]
            current  = [cm.get(h, (0, 0))[0] for h in range(24)]
            previous = [pm.get(h, (0, 0))[0] for h in range(24)]
        else:
            n = delta_days + 1
            all_cur  = [df + timedelta(days=i) for i in range(n)]
            prev_df  = date.fromisoformat(prev_from)
            all_prev = [prev_df + timedelta(days=i) for i in range(n)]
            cm, pm   = _daily(d_from, d_to), _daily(prev_from, prev_to)
            labels   = [d.strftime('%d %b') for d in all_cur]
            current  = [cm.get(str(d), (0, 0))[0] for d in all_cur]
            previous = [pm.get(str(d), (0, 0))[0] for d in all_prev]

        def _kpis(start, end):
            cr.execute(f"""
                SELECT COALESCE(SUM(CASE WHEN amount_total>0 THEN amount_total END),0),
                       COUNT(CASE WHEN amount_total>0 THEN 1 END),
                       COALESCE(AVG(CASE WHEN amount_total>0 THEN amount_total END),0)
                FROM pos_order po
                WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') {xsql}
            """, [company_id, start, end] + xp)
            r = cr.fetchone()
            cr.execute(f"""
                SELECT COALESCE(SUM(pol.qty),0)
                FROM pos_order_line pol JOIN pos_order po ON po.id=pol.order_id
                WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced') {xsql}
            """, [company_id, start, end] + xp)
            items = int(cr.fetchone()[0] or 0)
            return float(r[0] or 0), int(r[1] or 0), float(r[2] or 0), items

        cr_rev, cr_ord, cr_avg, cr_items = _kpis(d_from, d_to)
        pr_rev, pr_ord, pr_avg, pr_items = _kpis(prev_from, prev_to)

        def pct(c, p):
            return None if p == 0 else round((c - p) / p * 100, 1)

        return {
            'labels': labels, 'current': current, 'previous': previous,
            'prev_label': f"{prev_from} → {prev_to}",
            'summary': {
                'revenue':    {'label': 'Revenue',    'current': self._fmt(cr_rev),  'previous': self._fmt(pr_rev),  'change_pct': pct(cr_rev, pr_rev)},
                'orders':     {'label': 'Orders',     'current': str(cr_ord),        'previous': str(pr_ord),        'change_pct': pct(cr_ord, pr_ord)},
                'avg_order':  {'label': 'Avg. Order', 'current': self._fmt(cr_avg),  'previous': self._fmt(pr_avg),  'change_pct': pct(cr_avg, pr_avg)},
                'items_sold': {'label': 'Items Sold', 'current': str(cr_items),      'previous': str(pr_items),      'change_pct': pct(cr_items, pr_items)},
            },
        }

    # ── New vs Returning customers ────────────────────────────────────────────

    @api.model
    def get_new_vs_returning(self, period='month', date_from=None, date_to=None,
                             config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)

        cr.execute(f"""
            SELECT
                COUNT(CASE WHEN first_date BETWEEN %s AND %s THEN 1 END) AS new_c,
                COUNT(CASE WHEN first_date < %s THEN 1 END)              AS ret_c
            FROM (
                SELECT partner_id, MIN(date_order::date) AS first_date
                FROM pos_order
                WHERE company_id=%s AND state IN ('paid','done','invoiced')
                  AND amount_total > 0 AND partner_id IS NOT NULL
                GROUP BY partner_id
            ) h
            WHERE partner_id IN (
                SELECT DISTINCT po.partner_id FROM pos_order po
                WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
                  AND po.state IN ('paid','done','invoiced')
                  AND po.amount_total > 0 AND po.partner_id IS NOT NULL {xsql}
            )
        """, [d_from, d_to, d_from, company_id, company_id, d_from, d_to] + xp)
        r = cr.fetchone()

        cr.execute(f"""
            SELECT COUNT(*) FROM pos_order po
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s
              AND po.state IN ('paid','done','invoiced') AND po.amount_total > 0
              AND po.partner_id IS NULL {xsql}
        """, [company_id, d_from, d_to] + xp)
        walk_ins = int(cr.fetchone()[0] or 0)

        return {'new': int(r[0] or 0), 'returning': int(r[1] or 0), 'walk_ins': walk_ins}

    # ── Export data ───────────────────────────────────────────────────────────

    @api.model
    def get_export_data(self, period='month', date_from=None, date_to=None,
                        config_id=None, cashier_id=None):
        company_id = self.env.company.id
        cr = self._cr
        d_from, d_to = _date_range(period, date_from, date_to)
        xsql, xp = self._xf(config_id, cashier_id)
        cr.execute(f"""
            SELECT po.name, po.date_order,
                   COALESCE(rpu.name,'—'), COALESCE(pc.name,'—'),
                   COALESCE(rp.name,'Walk-in'),
                   pt.name->>'en_US', cat.complete_name,
                   pol.qty, pol.price_unit, pol.discount,
                   ROUND((pol.price_unit * pol.qty * pol.discount / 100.0)::numeric, 2),
                   pol.price_subtotal, pol.price_subtotal_incl, po.state
            FROM pos_order_line pol
            JOIN pos_order po ON po.id=pol.order_id
            JOIN product_product pp ON pp.id=pol.product_id
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
            JOIN product_category cat ON cat.id=pt.categ_id
            LEFT JOIN res_partner rp  ON rp.id=po.partner_id
            LEFT JOIN res_users   ru  ON ru.id=po.user_id
            LEFT JOIN res_partner rpu ON rpu.id=ru.partner_id
            LEFT JOIN pos_config  pc  ON pc.id=po.config_id
            WHERE po.company_id=%s AND po.date_order::date BETWEEN %s AND %s {xsql}
            ORDER BY po.date_order DESC LIMIT 50001
        """, [company_id, d_from, d_to] + xp)
        rows = cr.fetchall()
        truncated = len(rows) > 50000
        cols = ['order_ref','date','cashier','terminal','customer','product','category',
                'qty','unit_price','discount_pct','discount_amt','price_excl_tax',
                'price_incl_tax','state']
        result = []
        for r in rows[:50000]:
            rec = dict(zip(cols, r))
            rec['date'] = rec['date'].strftime('%Y-%m-%d %H:%M') if rec['date'] else ''
            result.append(rec)
        return {'rows': result, 'truncated': truncated}
