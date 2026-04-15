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


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_crm_kpis(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        p_from, p_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr

        # Total leads created in period
        cr.execute("""
            SELECT COUNT(*) FROM crm_lead
            WHERE company_id = %s AND type = 'lead'
              AND create_date::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        new_leads = cr.fetchone()[0] or 0

        # Opportunities created in period
        cr.execute("""
            SELECT COUNT(*) FROM crm_lead
            WHERE company_id = %s AND type = 'opportunity'
              AND create_date::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        new_opportunities = cr.fetchone()[0] or 0

        # Won opportunities in period
        cr.execute("""
            SELECT COUNT(*), COALESCE(SUM(expected_revenue), 0)
            FROM crm_lead
            WHERE company_id = %s AND probability = 100
              AND date_closed::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        row = cr.fetchone()
        won_count = row[0] or 0
        won_revenue = row[1] or 0.0

        # Lost opportunities in period
        cr.execute("""
            SELECT COUNT(*) FROM crm_lead
            WHERE company_id = %s AND active = false
              AND write_date::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        lost_count = cr.fetchone()[0] or 0

        # Active pipeline (open opportunities)
        cr.execute("""
            SELECT COUNT(*), COALESCE(SUM(expected_revenue), 0)
            FROM crm_lead
            WHERE company_id = %s AND active = true AND type = 'opportunity'
              AND probability < 100
        """, (company_id,))
        row = cr.fetchone()
        pipeline_count = row[0] or 0
        pipeline_value = row[1] or 0.0

        # Total expected revenue in period
        cr.execute("""
            SELECT COALESCE(SUM(expected_revenue), 0)
            FROM crm_lead
            WHERE company_id = %s AND type = 'opportunity'
              AND create_date::date BETWEEN %s AND %s
        """, (company_id, d_from, d_to))
        total_expected = cr.fetchone()[0] or 0.0

        # Win rate
        total_closed = won_count + lost_count
        win_rate = round(won_count / total_closed * 100, 1) if total_closed > 0 else 0.0

        # Average deal size
        avg_deal = round(won_revenue / won_count, 2) if won_count > 0 else 0.0

        # Active sales team members
        cr.execute("""
            SELECT COUNT(DISTINCT cl.user_id)
            FROM crm_lead cl
            WHERE cl.company_id = %s AND cl.active = true AND cl.user_id IS NOT NULL
        """, (company_id,))
        team_members = cr.fetchone()[0] or 0

        # Overdue activities
        cr.execute("""
            SELECT COUNT(DISTINCT res_id)
            FROM mail_activity ma
            JOIN crm_lead cl ON cl.id = ma.res_id
            WHERE ma.res_model = 'crm.lead' AND cl.company_id = %s
              AND cl.active = true AND ma.date_deadline < %s
        """, (company_id, str(date.today())))
        overdue_activities = cr.fetchone()[0] or 0

        # Previous period won for comparison
        cr.execute("""
            SELECT COUNT(*) FROM crm_lead
            WHERE company_id = %s AND probability = 100
              AND date_closed::date BETWEEN %s AND %s
        """, (company_id, p_from, p_to))
        prev_won = cr.fetchone()[0] or 0
        won_change = None
        if prev_won > 0:
            won_change = round((won_count - prev_won) / prev_won * 100, 1)

        # Format currency values
        currency = self.env.company.currency_id
        fmt = lambda v: f"{currency.symbol}{v:,.0f}" if v >= 1000 else f"{currency.symbol}{v:,.2f}"

        period_label = f"{d_from} → {d_to}"
        return {
            'new_leads': new_leads,
            'new_opportunities': new_opportunities,
            'won_count': won_count,
            'won_revenue': fmt(won_revenue),
            'lost_count': lost_count,
            'pipeline_count': pipeline_count,
            'pipeline_value': fmt(pipeline_value),
            'total_expected': fmt(total_expected),
            'win_rate': f"{win_rate}%",
            'avg_deal': fmt(avg_deal),
            'team_members': team_members,
            'overdue_activities': overdue_activities,
            'won_change': won_change,
            'period_label': period_label,
        }

    @api.model
    def get_crm_lead_trend(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        df = date.fromisoformat(d_from)
        dt = date.fromisoformat(d_to)
        days = (dt - df).days

        if days <= 60:
            cr.execute("""
                SELECT cl.create_date::date AS d,
                       COUNT(*) FILTER (WHERE cl.type = 'lead') AS leads,
                       COUNT(*) FILTER (WHERE cl.type = 'opportunity') AS opps
                FROM crm_lead cl
                WHERE cl.company_id = %s
                  AND cl.create_date::date BETWEEN %s AND %s
                GROUP BY d ORDER BY d
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            all_days = [df + timedelta(days=i) for i in range(days + 1)]
            lead_map = {r[0]: r[1] for r in rows}
            opp_map = {r[0]: r[2] for r in rows}
            labels = [str(d) for d in all_days]
            lead_vals = [lead_map.get(d, 0) for d in all_days]
            opp_vals = [opp_map.get(d, 0) for d in all_days]
        else:
            cr.execute("""
                SELECT TO_CHAR(DATE_TRUNC('month', cl.create_date), 'YYYY-MM') AS m,
                       COUNT(*) FILTER (WHERE cl.type = 'lead') AS leads,
                       COUNT(*) FILTER (WHERE cl.type = 'opportunity') AS opps
                FROM crm_lead cl
                WHERE cl.company_id = %s
                  AND cl.create_date::date BETWEEN %s AND %s
                GROUP BY m ORDER BY m
            """, (company_id, d_from, d_to))
            rows = cr.fetchall()
            labels = [r[0] for r in rows]
            lead_vals = [r[1] for r in rows]
            opp_vals = [r[2] for r in rows]

        return {'labels': labels, 'lead_vals': lead_vals, 'opp_vals': opp_vals}

    @api.model
    def get_crm_pipeline_by_stage(self):
        company_id = self.env.company.id
        cr = self._cr
        cr.execute("""
            SELECT cs.name->>'en_US' AS stage_name,
                   COUNT(*) AS cnt,
                   COALESCE(SUM(cl.expected_revenue), 0) AS revenue
            FROM crm_lead cl
            JOIN crm_stage cs ON cs.id = cl.stage_id
            WHERE cl.active = true AND cl.company_id = %s
              AND cl.type = 'opportunity' AND cl.probability < 100
            GROUP BY cs.name->>'en_US', cs.sequence
            ORDER BY cs.sequence
        """, (company_id,))
        rows = cr.fetchall()
        return {
            'labels': [r[0] or 'Unknown' for r in rows],
            'counts': [r[1] for r in rows],
            'revenues': [float(r[2]) for r in rows],
        }

    @api.model
    def get_crm_top_salespeople(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        currency = self.env.company.currency_id
        fmt = lambda v: f"{currency.symbol}{v:,.0f}"

        cr.execute("""
            SELECT rp.name AS uname,
                   COUNT(*) AS total,
                   COUNT(*) FILTER (WHERE cl.probability = 100) AS won,
                   COALESCE(SUM(cl.expected_revenue) FILTER (WHERE cl.probability = 100), 0) AS revenue
            FROM crm_lead cl
            JOIN res_users ru ON ru.id = cl.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE cl.company_id = %s AND cl.type = 'opportunity'
              AND cl.create_date::date BETWEEN %s AND %s
            GROUP BY rp.name ORDER BY revenue DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return [{
            'name': r[0] or 'Unassigned',
            'total': r[1],
            'won': r[2],
            'revenue': fmt(r[3]),
            'win_rate': f"{round(r[2] / r[1] * 100, 1) if r[1] > 0 else 0}%",
        } for r in rows]

    @api.model
    def get_crm_top_salespeople_chart(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        cr.execute("""
            SELECT rp.name AS uname,
                   COALESCE(SUM(cl.expected_revenue) FILTER (WHERE cl.probability = 100), 0) AS revenue
            FROM crm_lead cl
            JOIN res_users ru ON ru.id = cl.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE cl.company_id = %s AND cl.type = 'opportunity'
              AND cl.create_date::date BETWEEN %s AND %s
            GROUP BY rp.name ORDER BY revenue DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {
            'labels': [r[0] or 'Unassigned' for r in rows],
            'values': [float(r[1]) for r in rows],
        }

    @api.model
    def get_crm_leads_by_source(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        cr.execute("""
            SELECT COALESCE(utm_source.name, 'Direct') AS source_name, COUNT(*) AS cnt
            FROM crm_lead cl
            LEFT JOIN utm_source ON utm_source.id = cl.source_id
            WHERE cl.company_id = %s
              AND cl.create_date::date BETWEEN %s AND %s
            GROUP BY COALESCE(utm_source.name, 'Direct')
            ORDER BY cnt DESC LIMIT 10
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return {
            'labels': [r[0] for r in rows],
            'values': [r[1] for r in rows],
        }

    @api.model
    def get_crm_recent_leads(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        currency = self.env.company.currency_id
        fmt = lambda v: f"{currency.symbol}{v:,.0f}" if v else '—'

        cr.execute("""
            SELECT
                cl.id,
                cl.name AS lead_name,
                rp.name AS partner_name,
                cs.name->>'en_US' AS stage_name,
                cl.expected_revenue,
                cl.probability,
                cl.create_date::text AS created,
                sp.name AS salesperson,
                cl.type
            FROM crm_lead cl
            LEFT JOIN res_partner rp ON rp.id = cl.partner_id
            LEFT JOIN crm_stage cs ON cs.id = cl.stage_id
            LEFT JOIN res_users ru ON ru.id = cl.user_id
            LEFT JOIN res_partner sp ON sp.id = ru.partner_id
            WHERE cl.company_id = %s AND cl.active = true
              AND cl.create_date::date BETWEEN %s AND %s
            ORDER BY cl.create_date DESC LIMIT 20
        """, (company_id, d_from, d_to))
        rows = cr.fetchall()
        return [{
            'id': r[0],
            'name': r[1] or '—',
            'partner': r[2] or '—',
            'stage': r[3] or '—',
            'revenue': fmt(r[4]),
            'probability': f"{r[5] or 0}%",
            'created': r[6][:10] if r[6] else '—',
            'salesperson': r[7] or 'Unassigned',
            'type': r[8] or 'lead',
        } for r in rows]

    @api.model
    def get_crm_comparison(self, period='month', date_from='', date_to=''):
        d_from, d_to = _date_range(period, date_from, date_to)
        p_from, p_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr

        def get_daily(df, dt):
            cr.execute("""
                SELECT cl.create_date::date AS d, COUNT(*)
                FROM crm_lead cl
                WHERE cl.company_id = %s
                  AND cl.create_date::date BETWEEN %s AND %s
                  AND cl.active = true
                GROUP BY d ORDER BY d
            """, (company_id, df, dt))
            return {str(r[0]): r[1] for r in cr.fetchall()}

        curr = get_daily(d_from, d_to)
        prev = get_daily(p_from, p_to)
        all_dates = sorted(set(list(curr.keys()) + list(prev.keys())))
        return {
            'labels': all_dates,
            'current_vals': [curr.get(d, 0) for d in all_dates],
            'prev_vals': [prev.get(d, 0) for d in all_dates],
            'current_label': f"Current ({d_from} → {d_to})",
            'prev_label': f"Previous ({p_from} → {p_to})",
        }
