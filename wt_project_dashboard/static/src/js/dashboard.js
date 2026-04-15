/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const P = ["#4F46E5","#7C3AED","#06B6D4","#3B82F6","#8B5CF6","#6366F1","#4338CA","#2563EB","#818CF8","#A5B4FC"];

const PERIOD_OPTIONS = [
    { key: "today",      label: "Today" },
    { key: "yesterday",  label: "Yesterday" },
    { key: "week",       label: "Last 7 Days" },
    { key: "last_week",  label: "Last Week" },
    { key: "month",      label: "This Month" },
    { key: "last_month", label: "Last Month" },
    { key: "quarter",    label: "This Quarter" },
    { key: "year",       label: "This Year" },
    { key: "custom",     label: "Custom Range" },
];

export class ProjectDashboard extends Component {
    static template = "ProjectDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this._charts = {};
        this.state = useState({
            period: "month", date_from: "", date_to: "",
            show_custom: false, loading: true, active_tab: "overview",
            period_options: PERIOD_OPTIONS, period_label: "",
            project_options: [], selected_project: "",
            active_projects: 0, total_tasks: 0, done_tasks: 0,
            overdue_tasks: 0, due_today: 0, team_members: 0,
            no_deadline: 0, high_priority: 0, created_period: 0,
            completion_pct: "0%", done_change: null,
            overdue_list: [], recent_tasks: [],
            comparison_data: null,
            last_updated: "",
        });

        onWillStart(async () => {
            const projects = await this.orm.call("project.task", "get_project_list", []);
            this.state.project_options = projects;
            await this._loadAll();
        });
        onMounted(async () => {
            this.state.loading = false;
            await this._renderTabCharts("overview");
            this._autoRefreshTimer = setInterval(() => this._applyFilters(), 5 * 60 * 1000);
        });
    }

    get filterArgs() {
        const pid = this.state.selected_project ? parseInt(this.state.selected_project) : null;
        return [this.state.period, this.state.date_from || '', this.state.date_to || '', pid];
    }

    async onPeriodChange(ev) {
        this.state.period = ev.target.value;
        this.state.show_custom = this.state.period === "custom";
        if (this.state.period !== "custom") await this._applyFilters();
    }

    async onProjectChange(ev) {
        this.state.selected_project = ev.target.value;
        await this._applyFilters();
    }

    async onCustomDateChange() {
        if (this.state.date_from && this.state.date_to) await this._applyFilters();
    }

    async _applyFilters() {
        this.state.loading = true;
        this.state.comparison_data = null;
        await this._loadAll();
        this.state.loading = false;
        await this._renderTabCharts(this.state.active_tab);
    }

    async refresh() { await this._applyFilters(); }

    async _loadAll() {
        const [period, df, dt, pid] = this.filterArgs;
        const [kpis, overdue, recent] = await Promise.all([
            this.orm.call("project.task", "get_project_kpis", [period, df, dt, pid]),
            this.orm.call("project.task", "get_project_overdue_list", [pid]),
            this.orm.call("project.task", "get_project_recent_tasks", [period, df, dt, pid]),
        ]);
        Object.assign(this.state, kpis);
        this.state.overdue_list = overdue;
        this.state.recent_tasks = recent;
        const now = new Date(); this.state.last_updated = now.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    }

    setTab(tab) {
        this.state.active_tab = tab;
        requestAnimationFrame(() => this._renderTabCharts(tab));
    }

    async _renderTabCharts(tab) {
        const [period, df, dt, pid] = this.filterArgs;
        if (tab === "overview") {
            await this._renderTrend();
        } else if (tab === "stages") {
            await this._renderStages();
        } else if (tab === "assignees") {
            await this._renderAssignees();
        } else if (tab === "completion") {
            await this._renderCompletion();
        } else if (tab === "comparison") {
            this.state.comparison_data = await this.orm.call(
                "project.task", "get_project_comparison", [period, df, dt, pid]);
            await this._renderComparisonChart();
        }
    }

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    async _renderTrend() {
        this._destroy("proj_trend");
        const [period, df, dt, pid] = this.filterArgs;
        const data = await this.orm.call("project.task", "get_project_task_trend", [period, df, dt, pid]);
        const canvas = document.getElementById("proj_chart_trend");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const g = ctx.createLinearGradient(0, 0, 0, 300);
        g.addColorStop(0, "#3B82F6CC");
        g.addColorStop(1, "#3B82F608");
        this._charts.proj_trend = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Tasks Created", data: data.values,
                    borderColor: "#3B82F6", backgroundColor: g,
                    borderWidth: 2.5, fill: true, tension: 0.4,
                    pointRadius: data.labels.length > 60 ? 0 : 3,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", precision: 0 } },
                },
            },
        });
    }

    async _renderStages() {
        this._destroy("proj_stages");
        const [,,,pid] = this.filterArgs;
        const data = await this.orm.call("project.task", "get_project_tasks_by_stage", [pid]);
        const canvas = document.getElementById("proj_chart_stages");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.proj_stages = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: data.labels,
                datasets: [{ data: data.values, backgroundColor: P, borderColor: "#fff", borderWidth: 2 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 12, padding: 14 } },
                },
                cutout: "55%",
            },
        });
    }

    async _renderAssignees() {
        this._destroy("proj_assignees");
        const [period, df, dt, pid] = this.filterArgs;
        const data = await this.orm.call("project.task", "get_project_tasks_by_assignee", [period, df, dt, pid]);
        const canvas = document.getElementById("proj_chart_assignees");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.proj_assignees = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Tasks", data: data.values,
                    backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", precision: 0 } },
                    y: { grid: { display: false }, ticks: { color: "#64748B", font: { size: 11 } } },
                },
            },
        });
    }

    async _renderCompletion() {
        this._destroy("proj_completion");
        const [,,,pid] = this.filterArgs;
        const data = await this.orm.call("project.task", "get_project_completion_rates", [pid]);
        const canvas = document.getElementById("proj_chart_completion");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.proj_completion = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Completion %", data: data.pcts,
                    backgroundColor: P.map(c => c + "66"), borderColor: P, borderWidth: 2, borderRadius: 4,
                }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, min: 0, max: 100, ticks: { color: "#94A3B8", callback: v => v + "%" } },
                    y: { grid: { display: false }, ticks: { color: "#64748B", font: { size: 11 } } },
                },
            },
        });
    }

    _nav(model, name, domain = []) {
        this.actionService.doAction({
            name: name, type: "ir.actions.act_window",
            res_model: model, view_mode: "list,form",
            views: [[false, "list"], [false, "form"]], domain, target: "current"
        });
    }
    _navRecord(model, id) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: model, res_id: id,
            view_mode: "form", views: [[false, "form"]], target: "current"
        });
    }

    onClickProjects()    { this._nav("project.project", "Projects", [["active","=",true]]); }
    onClickTasks()       { this._nav("project.task", "Tasks", [["active","=",true]]); }
    onClickDone()        { this._nav("project.task", "Done Tasks", [["active","=",true],["stage_id.fold","=",true]]); }
    onClickOverdue()     { this._nav("project.task", "Overdue Tasks", [["active","=",true],["date_deadline","<", new Date().toISOString().slice(0,10)]]); }
    onClickDueToday()    { this._nav("project.task", "Due Today", [["date_deadline","=", new Date().toISOString().slice(0,10)]]); }
    onClickTeam()        { this._nav("res.users", "Users", [["active","=",true]]); }
    onClickNoDeadline()  { this._nav("project.task", "Tasks Without Deadline", [["active","=",true],["date_deadline","=",false]]); }
    onClickPriority()    { this._nav("project.task", "High Priority", [["active","=",true],["priority","=","1"]]); }
    onClickCreated()     { this._nav("project.task", "Tasks", [["active","=",true]]); }
    onRowClick(id)       { this._navRecord("project.task", id); }

    exportTasks() {
        const rows = this.state.recent_tasks;
        if (!rows.length) return;
        const headers = ["Task","Project","Stage","Assignee","Deadline","Priority"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.project, r.stage, r.assignee, r.deadline||'', r.priority].map(v => `"${v||''}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "project_tasks.csv");
    }
    exportOverdue() {
        const rows = this.state.overdue_list;
        if (!rows.length) return;
        const headers = ["Task","Project","Stage","Assignee","Deadline"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.project, r.stage, r.assignee, r.deadline||''].map(v => `"${v||''}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "overdue_tasks.csv");
    }
    _downloadCsv(csv, filename) {
        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
    }

    async _renderComparisonChart() {
        this._destroy("proj_comparison");
        const data = this.state.comparison_data;
        if (!data) return;
        const canvas = document.getElementById("proj_chart_comparison");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.proj_comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: data.current_label, data: data.current_vals, backgroundColor: "#3B82F666", borderColor: "#3B82F6", borderWidth: 2, borderRadius: 4 },
                    { label: data.prev_label,    data: data.prev_vals,    backgroundColor: "#94A3B844", borderColor: "#94A3B8", borderWidth: 2, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", precision: 0 } },
                },
            },
        });
    }
}

registry.category("actions").add("ProjectDashboard", ProjectDashboard);
