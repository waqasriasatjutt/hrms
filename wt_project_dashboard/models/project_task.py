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


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def get_project_kpis(self, period='month', date_from='', date_to='', project_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        today = str(date.today())
        p_filter = " AND pt.project_id = %s" if project_id else ""
        p_args_base = [company_id] + ([project_id] if project_id else [])

        # Active projects
        cr.execute("""
            SELECT COUNT(*) FROM project_project pp
            WHERE pp.active = true AND pp.company_id = %s
        """, (company_id,))
        active_projects = cr.fetchone()[0] or 0

        # Total active tasks
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            WHERE pt.active = true AND pt.company_id = %s
        """ + p_filter, p_args_base)
        total_tasks = cr.fetchone()[0] or 0

        # Completed tasks (in folded stage)
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.active = true AND pt.company_id = %s AND ptt.fold = true
        """ + p_filter, p_args_base)
        done_tasks = cr.fetchone()[0] or 0

        # Overdue tasks
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            LEFT JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.active = true AND pt.company_id = %s
              AND pt.date_deadline IS NOT NULL
              AND pt.date_deadline < %s
              AND (ptt.fold IS NULL OR ptt.fold = false)
        """ + p_filter, p_args_base + [today])
        overdue_tasks = cr.fetchone()[0] or 0

        # Due today
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            WHERE pt.active = true AND pt.company_id = %s
              AND pt.date_deadline::date = %s
        """ + p_filter, p_args_base + [today])
        due_today = cr.fetchone()[0] or 0

        # Team members (users assigned to active tasks)
        cr.execute("""
            SELECT COUNT(DISTINCT ptur.user_id)
            FROM project_task_user_rel ptur
            JOIN project_task pt ON pt.id = ptur.task_id
            WHERE pt.active = true AND pt.company_id = %s
        """ + p_filter, p_args_base)
        team_members = cr.fetchone()[0] or 0

        # Tasks with no deadline
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            LEFT JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.active = true AND pt.company_id = %s
              AND pt.date_deadline IS NULL
              AND (ptt.fold IS NULL OR ptt.fold = false)
        """ + p_filter, p_args_base)
        no_deadline = cr.fetchone()[0] or 0

        # High priority tasks
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            LEFT JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.active = true AND pt.company_id = %s
              AND pt.priority = '1'
              AND (ptt.fold IS NULL OR ptt.fold = false)
        """ + p_filter, p_args_base)
        high_priority = cr.fetchone()[0] or 0

        # Tasks created in period
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            WHERE pt.company_id = %s
              AND pt.create_date::date BETWEEN %s AND %s
        """ + p_filter, p_args_base + [d_from, d_to])
        created_period = cr.fetchone()[0] or 0

        # % change in completed tasks vs prev period
        p_from, p_to = _prev_range(d_from, d_to)
        cr.execute("""
            SELECT COUNT(*) FROM project_task pt
            JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.company_id = %s AND ptt.fold = true
              AND pt.write_date::date BETWEEN %s AND %s
        """, (company_id, p_from, p_to))
        prev_done = cr.fetchone()[0] or 0
        done_change = None
        if prev_done > 0:
            done_change = round((done_tasks - prev_done) / prev_done * 100, 1)

        completion_pct = round(done_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0

        # Period label
        period_label = f"{d_from} → {d_to}"

        return {
            'active_projects': active_projects,
            'total_tasks': total_tasks,
            'done_tasks': done_tasks,
            'overdue_tasks': overdue_tasks,
            'due_today': due_today,
            'team_members': team_members,
            'no_deadline': no_deadline,
            'high_priority': high_priority,
            'created_period': created_period,
            'completion_pct': f"{completion_pct}%",
            'done_change': done_change,
            'period_label': period_label,
        }

    @api.model
    def get_project_task_trend(self, period='month', date_from='', date_to='', project_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        df = date.fromisoformat(d_from)
        dt = date.fromisoformat(d_to)
        days = (dt - df).days
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []

        if days <= 60:
            cr.execute("""
                SELECT pt.create_date::date AS d, COUNT(*)
                FROM project_task pt
                WHERE pt.company_id = %s
                  AND pt.create_date::date BETWEEN %s AND %s
            """ + p_filter + """
                GROUP BY d ORDER BY d
            """, [company_id, d_from, d_to] + extra)
            rows = cr.fetchall()
            all_days = [(df + timedelta(days=i)) for i in range(days + 1)]
            row_map = {r[0]: r[1] for r in rows}
            labels = [str(d) for d in all_days]
            values = [row_map.get(d, 0) for d in all_days]
        else:
            cr.execute("""
                SELECT TO_CHAR(DATE_TRUNC('month', pt.create_date), 'YYYY-MM') AS m, COUNT(*)
                FROM project_task pt
                WHERE pt.company_id = %s
                  AND pt.create_date::date BETWEEN %s AND %s
            """ + p_filter + """
                GROUP BY m ORDER BY m
            """, [company_id, d_from, d_to] + extra)
            rows = cr.fetchall()
            labels = [r[0] for r in rows]
            values = [r[1] for r in rows]

        return {'labels': labels, 'values': values}

    @api.model
    def get_project_tasks_by_stage(self, project_id=None):
        company_id = self.env.company.id
        cr = self._cr
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []
        cr.execute("""
            SELECT ptt.name->>'en_US' AS stage_name, COUNT(*) AS cnt
            FROM project_task pt
            JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.active = true AND pt.company_id = %s
        """ + p_filter + """
            GROUP BY ptt.name->>'en_US', ptt.sequence
            ORDER BY ptt.sequence
        """, [company_id] + extra)
        rows = cr.fetchall()
        return {
            'labels': [r[0] or 'Unknown' for r in rows],
            'values': [r[1] for r in rows],
        }

    @api.model
    def get_project_tasks_by_assignee(self, period='month', date_from='', date_to='', project_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []
        cr.execute("""
            SELECT rp.name AS uname, COUNT(DISTINCT pt.id) AS cnt
            FROM project_task pt
            JOIN project_task_user_rel ptur ON ptur.task_id = pt.id
            JOIN res_users ru ON ru.id = ptur.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE pt.active = true AND pt.company_id = %s
              AND pt.create_date::date BETWEEN %s AND %s
        """ + p_filter + """
            GROUP BY rp.name ORDER BY cnt DESC LIMIT 10
        """, [company_id, d_from, d_to] + extra)
        rows = cr.fetchall()
        return {
            'labels': [r[0] or 'Unassigned' for r in rows],
            'values': [r[1] for r in rows],
        }

    @api.model
    def get_project_completion_rates(self, project_id=None):
        company_id = self.env.company.id
        cr = self._cr
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []
        cr.execute("""
            SELECT
                pp.name->>'en_US' AS proj_name,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE ptt.fold = true) AS done
            FROM project_task pt
            JOIN project_project pp ON pp.id = pt.project_id
            LEFT JOIN project_task_type ptt ON ptt.id = pt.stage_id
            WHERE pt.active = true AND pt.company_id = %s
        """ + p_filter + """
            GROUP BY pp.name->>'en_US'
            ORDER BY total DESC LIMIT 10
        """, [company_id] + extra)
        rows = cr.fetchall()
        labels = [r[0] or 'No Project' for r in rows]
        pcts = [round(r[2] / r[1] * 100, 1) if r[1] > 0 else 0 for r in rows]
        totals = [r[1] for r in rows]
        return {'labels': labels, 'pcts': pcts, 'totals': totals}

    @api.model
    def get_project_overdue_list(self, project_id=None):
        company_id = self.env.company.id
        cr = self._cr
        today = str(date.today())
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []
        cr.execute("""
            SELECT
                pt.id,
                pt.name AS task_name,
                pp.name->>'en_US' AS project_name,
                pt.date_deadline::text AS deadline,
                rp.name AS assignee,
                pt.priority
            FROM project_task pt
            LEFT JOIN project_project pp ON pp.id = pt.project_id
            LEFT JOIN project_task_type ptt ON ptt.id = pt.stage_id
            LEFT JOIN project_task_user_rel ptur ON ptur.task_id = pt.id
            LEFT JOIN res_users ru ON ru.id = ptur.user_id
            LEFT JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE pt.active = true AND pt.company_id = %s
              AND pt.date_deadline IS NOT NULL AND pt.date_deadline < %s
              AND (ptt.fold IS NULL OR ptt.fold = false)
        """ + p_filter + """
            ORDER BY pt.date_deadline LIMIT 20
        """, [company_id, today] + extra)
        rows = cr.fetchall()
        return [{
            'id': r[0],
            'name': r[1],
            'project': r[2] or '—',
            'deadline': r[3] or '—',
            'assignee': r[4] or 'Unassigned',
            'priority': '🔴' if r[5] == '1' else '⚪',
        } for r in rows]

    @api.model
    def get_project_recent_tasks(self, period='month', date_from='', date_to='', project_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        company_id = self.env.company.id
        cr = self._cr
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []
        cr.execute("""
            SELECT
                pt.id,
                pt.name AS task_name,
                pp.name->>'en_US' AS project_name,
                ptt.name->>'en_US' AS stage_name,
                pt.date_deadline::text AS deadline,
                pt.priority,
                pt.create_date::text AS created,
                rp.name AS assignee
            FROM project_task pt
            LEFT JOIN project_project pp ON pp.id = pt.project_id
            LEFT JOIN project_task_type ptt ON ptt.id = pt.stage_id
            LEFT JOIN project_task_user_rel ptur ON ptur.task_id = pt.id
            LEFT JOIN res_users ru ON ru.id = ptur.user_id
            LEFT JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE pt.company_id = %s
              AND pt.create_date::date BETWEEN %s AND %s
        """ + p_filter + """
            ORDER BY pt.create_date DESC LIMIT 20
        """, [company_id, d_from, d_to] + extra)
        rows = cr.fetchall()
        return [{
            'id': r[0],
            'name': r[1],
            'project': r[2] or '—',
            'stage': r[3] or '—',
            'deadline': r[4] or '—',
            'priority': '🔴' if r[5] == '1' else '⚪',
            'created': r[6][:10] if r[6] else '—',
            'assignee': r[7] or 'Unassigned',
        } for r in rows]

    @api.model
    def get_project_list(self):
        company_id = self.env.company.id
        cr = self._cr
        cr.execute("""
            SELECT id, name->>'en_US' AS name
            FROM project_project
            WHERE active = true AND company_id = %s
            ORDER BY name->>'en_US'
        """, (company_id,))
        rows = cr.fetchall()
        return [{'id': r[0], 'name': r[1] or 'Project'} for r in rows]

    @api.model
    def get_project_comparison(self, period='month', date_from='', date_to='', project_id=None):
        d_from, d_to = _date_range(period, date_from, date_to)
        p_from, p_to = _prev_range(d_from, d_to)
        company_id = self.env.company.id
        cr = self._cr
        p_filter = " AND pt.project_id = %s" if project_id else ""
        extra = [project_id] if project_id else []

        def get_daily(df, dt):
            cr.execute("""
                SELECT pt.create_date::date AS d, COUNT(*)
                FROM project_task pt
                WHERE pt.company_id = %s
                  AND pt.create_date::date BETWEEN %s AND %s
            """ + p_filter + """
                GROUP BY d ORDER BY d
            """, [company_id, df, dt] + extra)
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
