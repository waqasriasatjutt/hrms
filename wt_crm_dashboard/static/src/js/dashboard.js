/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const P = ["#E11D48","#F97316","#FBBF24","#FB7185","#F43F5E","#E879A3","#FF6B6B","#FCA5A5","#FDA4AF","#FECDD3"];

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

export class CrmDashboard extends Component {
    static template = "CrmDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this._charts = {};
        this.state = useState({
            period: "month", date_from: "", date_to: "",
            show_custom: false, loading: true, active_tab: "overview",
            period_options: PERIOD_OPTIONS, period_label: "",
            new_leads: 0, new_opportunities: 0, won_count: 0,
            won_revenue: "—", lost_count: 0, pipeline_count: 0,
            pipeline_value: "—", total_expected: "—",
            win_rate: "0%", avg_deal: "—", team_members: 0,
            overdue_activities: 0, won_change: null,
            recent_leads: [], salesperson_stats: [],
            comparison_data: null,
            last_updated: "",
        });

        onWillStart(async () => { await this._loadAll(); });
        onMounted(async () => {
            this.state.loading = false;
            await this._renderTabCharts("overview");
            this._autoRefreshTimer = setInterval(() => this._applyFilters(), 5 * 60 * 1000);
        });
        onWillUnmount(() => {
            clearInterval(this._autoRefreshTimer);
            Object.values(this._charts).forEach(c => c.destroy());
            this._charts = {};
        });
    }

    get filterArgs() {
        return [this.state.period, this.state.date_from || '', this.state.date_to || ''];
    }

    async onPeriodChange(ev) {
        this.state.period = ev.target.value;
        this.state.show_custom = this.state.period === "custom";
        if (this.state.period !== "custom") await this._applyFilters();
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
        const [period, df, dt] = this.filterArgs;
        const [kpis, recent, salesperson] = await Promise.all([
            this.orm.call("crm.lead", "get_crm_kpis", [period, df, dt]),
            this.orm.call("crm.lead", "get_crm_recent_leads", [period, df, dt]),
            this.orm.call("crm.lead", "get_crm_top_salespeople", [period, df, dt]),
        ]);
        Object.assign(this.state, kpis);
        this.state.recent_leads = recent;
        this.state.salesperson_stats = salesperson;
        const now = new Date(); this.state.last_updated = now.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    }

    setTab(tab) {
        this.state.active_tab = tab;
        requestAnimationFrame(() => this._renderTabCharts(tab));
    }

    async _renderTabCharts(tab) {
        const [period, df, dt] = this.filterArgs;
        if (tab === "overview") {
            await this._renderTrend();
        } else if (tab === "pipeline") {
            await this._renderPipeline();
        } else if (tab === "salespeople") {
            await this._renderSalespeople();
        } else if (tab === "sources") {
            await this._renderSources();
        } else if (tab === "comparison") {
            this.state.comparison_data = await this.orm.call(
                "crm.lead", "get_crm_comparison", [period, df, dt]);
            await this._renderComparisonChart();
        }
    }

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    async _renderTrend() {
        this._destroy("crm_trend");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("crm.lead", "get_crm_lead_trend", [period, df, dt]);
        const canvas = document.getElementById("crm_chart_trend");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const g1 = ctx.createLinearGradient(0, 0, 0, 300);
        g1.addColorStop(0, "#10B981CC");
        g1.addColorStop(1, "#10B98108");
        this._charts.crm_trend = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Leads", data: data.lead_vals, borderColor: "#10B981",
                      backgroundColor: g1, borderWidth: 2.5, fill: true, tension: 0.4,
                      pointRadius: data.labels.length > 60 ? 0 : 3 },
                    { label: "Opportunities", data: data.opp_vals, borderColor: "#3B82F6",
                      backgroundColor: "transparent", borderWidth: 2, borderDash: [4,3],
                      pointRadius: 0, fill: false, tension: 0.4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", precision: 0 } },
                },
            },
        });
    }

    async _renderPipeline() {
        this._destroy("crm_pipeline_count");
        this._destroy("crm_pipeline_revenue");
        const data = await this.orm.call("crm.lead", "get_crm_pipeline_by_stage", []);

        const canvasCount = document.getElementById("crm_chart_pipeline_count");
        if (canvasCount && data.labels.length) {
            const ctx = canvasCount.getContext("2d");
            this._charts.crm_pipeline_count = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{ label: "Opportunities", data: data.counts,
                        backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                        y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", precision: 0 } },
                    },
                },
            });
        }

        const canvasRev = document.getElementById("crm_chart_pipeline_revenue");
        if (canvasRev && data.labels.length) {
            const ctx2 = canvasRev.getContext("2d");
            this._charts.crm_pipeline_revenue = new Chart(ctx2, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [{ label: "Expected Revenue", data: data.revenues,
                        backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                        y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: v => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    },
                },
            });
        }
    }

    async _renderSalespeople() {
        this._destroy("crm_salespeople");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("crm.lead", "get_crm_top_salespeople_chart", [period, df, dt]);
        const canvas = document.getElementById("crm_chart_salespeople");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.crm_salespeople = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Won Revenue", data: data.values,
                    backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: v => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    y: { grid: { display: false }, ticks: { color: "#64748B", font: { size: 11 } } },
                },
            },
        });
    }

    async _renderSources() {
        this._destroy("crm_sources");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("crm.lead", "get_crm_leads_by_source", [period, df, dt]);
        const canvas = document.getElementById("crm_chart_sources");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.crm_sources = new Chart(ctx, {
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

    onClickLeads()       { this._nav("crm.lead", "Leads", [["type","=","lead"]]); }
    onClickOpps()        { this._nav("crm.lead", "Opportunities", [["type","=","opportunity"],["active","=",true]]); }
    onClickWon()         { this._nav("crm.lead", "Won Deals", [["probability","=",100]]); }
    onClickLost()        { this._nav("crm.lead", "Lost Deals", [["active","=",false]]); }
    onClickWinRate()     { this._nav("crm.lead", "Opportunities", [["type","=","opportunity"]]); }
    onClickAvgDeal()     { this._nav("crm.lead", "Won Deals", [["probability","=",100]]); }
    onClickPipeline()    { this._nav("crm.lead", "Pipeline", [["active","=",true],["probability","<",100]]); }
    onClickTeam()        { this._nav("res.users", "Sales Team", [["active","=",true]]); }
    onClickActivities()  { this._nav("crm.lead", "Overdue Activities", [["activity_date_deadline","<", new Date().toISOString().slice(0,10)]]); }
    onRowClick(id)       { this._navRecord("crm.lead", id); }

    exportLeads() {
        const rows = this.state.recent_leads;
        if (!rows.length) return;
        const headers = ["Lead/Opp","Partner","Stage","Revenue","Probability","Created","Salesperson","Type"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.partner, r.stage, r.revenue, r.probability, r.created, r.salesperson, r.type].map(v => `"${v||''}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "crm_leads.csv");
    }
    _downloadCsv(csv, filename) {
        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
    }

    async _renderComparisonChart() {
        this._destroy("crm_comparison");
        const data = this.state.comparison_data;
        if (!data) return;
        const canvas = document.getElementById("crm_chart_comparison");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.crm_comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: data.current_label, data: data.current_vals, backgroundColor: "#10B98166", borderColor: "#10B981", borderWidth: 2, borderRadius: 4 },
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

registry.category("actions").add("CrmDashboard", CrmDashboard);
