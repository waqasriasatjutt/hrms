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


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _fmt(self, val):
        company = self.env.company
        sym = company.currency_id.symbol or '$'
        v = float(val or 0)
        if abs(v) >= 1_000_000:
            s = f"{v / 1_000_000:.1f}M"
        elif abs(v) >= 1_000:
            s = f"{v / 1_000:.1f}K"
        else:
            s = f"{v:,.2f}"
        return f"{sym} {s}"

    @api.model
    def get_accounting_kpis(self, period='month', date_from='', date_to='', filter_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        today = date.today()

        # Revenue (posted out_invoices in period)
        cr.execute("""
            SELECT COALESCE(SUM(am.amount_untaxed_signed), 0),
                   COALESCE(SUM(am.amount_tax), 0),
                   COALESCE(AVG(am.amount_total), 0),
                   COUNT(*)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.invoice_date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        rev_row = cr.fetchone()
        total_revenue = float(rev_row[0] or 0)
        tax_collected = float(rev_row[1] or 0)
        avg_invoice = float(rev_row[2] or 0)

        # Expenses (posted in_invoices in period)
        cr.execute("""
            SELECT COALESCE(SUM(am.amount_untaxed_signed), 0)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'in_invoice'
              AND am.state = 'posted'
              AND am.invoice_date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        exp_row = cr.fetchone()
        total_expenses = abs(float(exp_row[0] or 0))

        net_profit = total_revenue - total_expenses

        # AR: unpaid out_invoices
        cr.execute("""
            SELECT COALESCE(SUM(am.amount_residual), 0), COUNT(*)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.payment_state NOT IN ('paid', 'reversed', 'in_payment')
        """, (company_id,))
        ar_row = cr.fetchone()
        accounts_receivable = float(ar_row[0] or 0)
        outstanding_invoices = int(ar_row[1] or 0)

        # AP: unpaid in_invoices
        cr.execute("""
            SELECT COALESCE(SUM(am.amount_residual), 0)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'in_invoice'
              AND am.state = 'posted'
              AND am.payment_state NOT IN ('paid', 'reversed', 'in_payment')
        """, (company_id,))
        ap_row = cr.fetchone()
        accounts_payable = float(ap_row[0] or 0)

        # Overdue invoices
        cr.execute("""
            SELECT COUNT(*)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.payment_state NOT IN ('paid', 'reversed', 'in_payment')
              AND am.invoice_date_due < %s
        """, (company_id, str(today)))
        overdue_invoices = int(cr.fetchone()[0] or 0)

        return {
            'period_label': f"{d_from} → {d_to}",
            'total_revenue': self._fmt(total_revenue),
            'total_expenses': self._fmt(total_expenses),
            'net_profit': self._fmt(net_profit),
            'accounts_receivable': self._fmt(accounts_receivable),
            'accounts_payable': self._fmt(accounts_payable),
            'outstanding_invoices': outstanding_invoices,
            'overdue_invoices': overdue_invoices,
            'avg_invoice_value': self._fmt(avg_invoice),
            'tax_collected': self._fmt(tax_collected),
            'net_profit_raw': net_profit,
        }

    @api.model
    def get_accounting_income_expense_trend(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT TO_CHAR(am.invoice_date, 'YYYY-MM') AS mon,
                   TO_CHAR(am.invoice_date, 'Mon YY') AS mon_label,
                   COALESCE(SUM(CASE WHEN am.move_type = 'out_invoice' THEN am.amount_untaxed_signed ELSE 0 END), 0) AS income,
                   COALESCE(SUM(CASE WHEN am.move_type = 'in_invoice' THEN ABS(am.amount_untaxed_signed) ELSE 0 END), 0) AS expense
            FROM account_move am
            WHERE am.company_id = %s
              AND am.state = 'posted'
              AND am.move_type IN ('out_invoice', 'in_invoice')
              AND am.invoice_date BETWEEN %s AND %s
            GROUP BY 1, 2
            ORDER BY 1
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        labels = [r[1] for r in rows]
        income = [float(r[2]) for r in rows]
        expenses = [float(r[3]) for r in rows]
        return {'labels': labels, 'income': income, 'expenses': expenses}

    @api.model
    def get_accounting_ar_aging(self, period='month', date_from='', date_to=''):
        company_id = self.env.company.id
        cr = self._cr
        today = date.today()

        cr.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) <= 0 THEN am.amount_residual ELSE 0 END), 0) AS current_amt,
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) BETWEEN 1 AND 30 THEN am.amount_residual ELSE 0 END), 0) AS d1_30,
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) BETWEEN 31 AND 60 THEN am.amount_residual ELSE 0 END), 0) AS d31_60,
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) BETWEEN 61 AND 90 THEN am.amount_residual ELSE 0 END), 0) AS d61_90,
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) > 90 THEN am.amount_residual ELSE 0 END), 0) AS d90plus
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.payment_state NOT IN ('paid', 'reversed', 'in_payment')
        """, (company_id,))
        row = cr.fetchone()
        labels = ['Current', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
        values = [float(r or 0) for r in row]
        return {'labels': labels, 'values': values}

    @api.model
    def get_accounting_ap_aging(self, period='month', date_from='', date_to=''):
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) <= 0 THEN am.amount_residual ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) BETWEEN 1 AND 30 THEN am.amount_residual ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) BETWEEN 31 AND 60 THEN am.amount_residual ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) BETWEEN 61 AND 90 THEN am.amount_residual ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN (CURRENT_DATE - am.invoice_date_due) > 90 THEN am.amount_residual ELSE 0 END), 0)
            FROM account_move am
            WHERE am.company_id = %s
              AND am.move_type = 'in_invoice'
              AND am.state = 'posted'
              AND am.payment_state NOT IN ('paid', 'reversed', 'in_payment')
        """, (company_id,))
        row = cr.fetchone()
        labels = ['Current', '1-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
        values = [float(r or 0) for r in row]
        return {'labels': labels, 'values': values}

    @api.model
    def get_accounting_top_customers(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT rp.name, COALESCE(SUM(am.amount_untaxed_signed), 0) AS revenue
            FROM account_move am
            JOIN res_partner rp ON rp.id = am.partner_id
            WHERE am.company_id = %s
              AND am.move_type = 'out_invoice'
              AND am.state = 'posted'
              AND am.invoice_date BETWEEN %s AND %s
            GROUP BY rp.name
            ORDER BY revenue DESC
            LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_accounting_top_vendors(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT rp.name, COALESCE(SUM(ABS(am.amount_untaxed_signed)), 0) AS spend
            FROM account_move am
            JOIN res_partner rp ON rp.id = am.partner_id
            WHERE am.company_id = %s
              AND am.move_type = 'in_invoice'
              AND am.state = 'posted'
              AND am.invoice_date BETWEEN %s AND %s
            GROUP BY rp.name
            ORDER BY spend DESC
            LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {'labels': [r[0] for r in rows], 'values': [float(r[1]) for r in rows]}

    @api.model
    def get_accounting_monthly_pl(self, period='year', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT TO_CHAR(am.invoice_date, 'YYYY-MM') AS mon,
                   TO_CHAR(am.invoice_date, 'Mon YY') AS mon_label,
                   COALESCE(SUM(CASE WHEN am.move_type = 'out_invoice' THEN am.amount_untaxed_signed ELSE 0 END), 0) AS income,
                   COALESCE(SUM(CASE WHEN am.move_type = 'in_invoice' THEN ABS(am.amount_untaxed_signed) ELSE 0 END), 0) AS expense
            FROM account_move am
            WHERE am.company_id = %s
              AND am.state = 'posted'
              AND am.move_type IN ('out_invoice', 'in_invoice')
              AND am.invoice_date BETWEEN %s AND %s
            GROUP BY 1, 2
            ORDER BY 1
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {
            'labels': [r[1] for r in rows],
            'income': [float(r[2]) for r in rows],
            'expenses': [float(r[3]) for r in rows],
        }

    @api.model
    def get_accounting_comparison(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        prev_from, prev_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr

        def get_period_data(df, dt):
            cr.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN move_type='out_invoice' THEN amount_untaxed_signed ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN move_type='in_invoice' THEN ABS(amount_untaxed_signed) ELSE 0 END), 0),
                    COUNT(CASE WHEN move_type='out_invoice' THEN 1 END)
                FROM account_move
                WHERE company_id = %s AND state = 'posted'
                  AND move_type IN ('out_invoice','in_invoice')
                  AND invoice_date BETWEEN %s AND %s
            """, (company_id, df, dt))
            row = cr.fetchone()
            return {'revenue': float(row[0] or 0), 'expenses': float(row[1] or 0), 'invoices': int(row[2] or 0)}

        curr = get_period_data(d_from, d_to)
        prev = get_period_data(prev_from, prev_to)

        def pct(c, p):
            if p == 0:
                return None
            return round((c - p) / p * 100, 1)

        sym = self.env.company.currency_id.symbol or '$'

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
                {'name': 'Expenses', 'current': fmt(curr['expenses']), 'prev': fmt(prev['expenses']), 'pct': pct(curr['expenses'], prev['expenses'])},
                {'name': 'Net Profit', 'current': fmt(curr['revenue'] - curr['expenses']), 'prev': fmt(prev['revenue'] - prev['expenses']), 'pct': pct(curr['revenue'] - curr['expenses'], prev['revenue'] - prev['expenses'])},
                {'name': 'Invoices', 'current': str(curr['invoices']), 'prev': str(prev['invoices']), 'pct': pct(curr['invoices'], prev['invoices'])},
            ],
            'labels': ['Revenue', 'Expenses', 'Net Profit'],
            'current_vals': [curr['revenue'], curr['expenses'], curr['revenue'] - curr['expenses']],
            'prev_vals': [prev['revenue'], prev['expenses'], prev['revenue'] - prev['expenses']],
        }

    @api.model
    def get_accounting_recent_invoices(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr

        cr.execute("""
            SELECT am.id, am.name, rp.name, am.invoice_date, am.invoice_date_due,
                   am.amount_total, am.payment_state, am.move_type
            FROM account_move am
            LEFT JOIN res_partner rp ON rp.id = am.partner_id
            WHERE am.company_id = %s
              AND am.state = 'posted'
              AND am.move_type IN ('out_invoice', 'in_invoice')
              AND am.invoice_date BETWEEN %s AND %s
            ORDER BY am.invoice_date DESC
            LIMIT 20
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        sym = self.env.company.currency_id.symbol or '$'

        def fmt(v):
            v = float(v or 0)
            return f"{sym} {v:,.2f}"

        return [{
            'id': r[0],
            'name': r[1] or '',
            'partner': r[2] or 'N/A',
            'invoice_date': str(r[3]) if r[3] else '',
            'due_date': str(r[4]) if r[4] else '',
            'amount': fmt(r[5]),
            'state': (r[6] or 'draft').replace('_', ' ').title(),
            'type': 'Invoice' if r[7] == 'out_invoice' else 'Bill',
        } for r in rows]
