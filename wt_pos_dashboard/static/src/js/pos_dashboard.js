/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const P = ["#7C3AED","#2563EB","#059669","#D97706","#DC2626",
           "#0891B2","#DB2777","#65A30D","#EA580C","#6366F1",
           "#14B8A6","#F59E0B","#8B5CF6","#EF4444","#06B6D4"];

function grad(ctx, color, a1 = "CC", a2 = "08") {
    const g = ctx.createLinearGradient(0, 0, 0, 350);
    g.addColorStop(0, color + a1);
    g.addColorStop(1, color + a2);
    return g;
}

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

export class PosDashboard extends Component {
    setup() {
        this.orm           = useService("orm");
        this.actionService = useService("action");
        this._charts       = {};

        this.state = useState({
            period: "today", date_from: "", date_to: "",
            config_id: "", cashier_id: "",
            show_custom: false, configs: [], cashiers: [],
            period_options: PERIOD_OPTIONS,

            // KPIs
            revenue: "—", orders: 0, refunds: 0, refund_amt: "—",
            avg_order: "—", items_sold: 0, open_sessions: 0,
            gross_margin: "—", total_discount: "—", tax_collected: "—",
            rev_change: null, ord_change: null, period_label: "",

            // Tables
            salesperson: [], recent_orders: [], session_status: [],

            // Extra data
            new_vs_returning: null,
            financial_data: null,
            comparison_data: null,

            loading: true,
            active_tab: "overview",
        });

        onWillStart(async () => {
            const [cfgs, cashiers] = await Promise.all([
                this.orm.call("pos.order", "get_pos_configs", []),
                this.orm.call("pos.order", "get_cashiers",    []),
            ]);
            this.state.configs  = cfgs;
            this.state.cashiers = cashiers;
            await this._loadAll();
        });

        onMounted(async () => {
            this.state.loading = false;
            await this._renderTabCharts("overview");
        });
    }

    // ── Filter helpers ────────────────────────────────────────────────────────

    get filterArgs() {
        return [
            this.state.period,
            this.state.date_from  || null,
            this.state.date_to    || null,
            this.state.config_id  || null,
            this.state.cashier_id || null,
        ];
    }

    async onPeriodChange(ev) {
        this.state.period = ev.target.value;
        this.state.show_custom = this.state.period === "custom";
        if (this.state.period !== "custom") await this._applyFilters();
    }
    async onConfigChange(ev)  { this.state.config_id  = ev.target.value; await this._applyFilters(); }
    async onCashierChange(ev) { this.state.cashier_id = ev.target.value; await this._applyFilters(); }
    async onCustomDateChange() {
        if (this.state.date_from && this.state.date_to) await this._applyFilters();
    }

    async _applyFilters() {
        this.state.loading = true;
        this.state.financial_data  = null;
        this.state.comparison_data = null;
        await this._loadAll();
        this.state.loading = false;
        await this._renderTabCharts(this.state.active_tab);
    }

    async refresh() { await this._applyFilters(); }

    // ── Data loading ──────────────────────────────────────────────────────────

    async _loadAll() {
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const [kpis, salesperson, recent, sessions, nvr] = await Promise.all([
            this.orm.call("pos.order", "get_dashboard_kpis",    [period, df, dt, cfg, cashier]),
            this.orm.call("pos.order", "get_salesperson_stats", [period, df, dt, cfg, cashier]),
            this.orm.call("pos.order", "get_recent_orders",     [20, period, df, dt, cfg, cashier]),
            this.orm.call("pos.order", "get_session_status",    []),
            this.orm.call("pos.order", "get_new_vs_returning",  [period, df, dt, cfg, cashier]),
        ]);
        Object.assign(this.state, kpis);
        this.state.salesperson      = salesperson;
        this.state.recent_orders    = recent;
        this.state.session_status   = sessions;
        this.state.new_vs_returning = nvr;
    }

    // ── Tab management ────────────────────────────────────────────────────────

    setTab(tab) {
        this.state.active_tab = tab;
        requestAnimationFrame(() => this._renderTabCharts(tab));
    }

    async _renderTabCharts(tab) {
        if (tab === "overview") {
            await Promise.all([
                this._renderTrend(), this._renderRevVsRefund(),
                this._renderPayment(), this._renderHeatmap(),
            ]);
        } else if (tab === "products") {
            await Promise.all([
                this._renderProducts(), this._renderProductsByRevenue(), this._renderCategories(),
            ]);
        } else if (tab === "customers") {
            await Promise.all([this._renderCustomers(), this._renderNewVsReturning()]);
        } else if (tab === "financial") {
            if (!this.state.financial_data) {
                const [period, df, dt, cfg, cashier] = this.filterArgs;
                this.state.financial_data = await this.orm.call(
                    "pos.order", "get_financial_analytics", [period, df, dt, cfg, cashier]);
            }
            await Promise.all([
                this._renderDiscountsByCashier(),
                this._renderMarginByCategory(),
                this._renderAvgRevByHour(),
            ]);
        } else if (tab === "comparison") {
            const [period, df, dt, cfg, cashier] = this.filterArgs;
            this.state.comparison_data = await this.orm.call(
                "pos.order", "get_comparison_data", [period, df, dt, cfg, cashier]);
            await this._renderComparison();
        }
    }

    // ── Chart helpers ─────────────────────────────────────────────────────────

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    // ── Overview charts ───────────────────────────────────────────────────────

    async _renderTrend() {
        this._destroy("trend");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_sales_trend", [period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_trend");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.trend = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    { label: _t("Revenue"), data: data.values, borderColor: "#7C3AED",
                      backgroundColor: grad(ctx, "#7C3AED"), borderWidth: 2.5,
                      pointRadius: data.labels.length > 60 ? 0 : 3,
                      pointBackgroundColor: "#7C3AED", fill: true, tension: 0.4, yAxisID: "y" },
                    { label: _t("Orders"), data: data.counts, borderColor: "#2563EB",
                      backgroundColor: "transparent", borderWidth: 1.5,
                      borderDash: [4, 3], pointRadius: 0, fill: false, tension: 0.4, yAxisID: "y2" },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } },
                    tooltip: { callbacks: { label: (c) => c.dataset.yAxisID === "y2"
                        ? ` ${c.parsed.y} orders`
                        : ` ${c.parsed.y.toLocaleString(undefined,{minimumFractionDigits:2})}` } },
                },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, position: "left", beginAtZero: true,
                         ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    y2: { grid: { display: false }, position: "right", beginAtZero: true,
                          ticks: { color: "#2563EB", font: { size: 10 } } },
                },
            },
        });
    }

    async _renderRevVsRefund() {
        this._destroy("rvr");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_revenue_vs_refunds", [period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_rvr");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.rvr = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: _t("Revenue"), data: data.revenue, backgroundColor: "#05966944", borderColor: "#059669", borderWidth: 2, borderRadius: 4, stack: "s" },
                    { label: _t("Refunds"),  data: data.refunds,  backgroundColor: "#DC262644", borderColor: "#DC2626", borderWidth: 2, borderRadius: 4, stack: "s2" },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } }, tooltip: { mode: "index", intersect: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                },
            },
        });
    }

    async _renderPayment() {
        this._destroy("payment");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_payment_breakdown", [period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_payment");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.payment = new Chart(ctx, {
            type: "doughnut",
            data: { labels: data.labels, datasets: [{ data: data.values, backgroundColor: P.slice(0, data.labels.length), borderWidth: 2, borderColor: "#fff", hoverOffset: 8 }] },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: "68%",
                plugins: {
                    legend: { position: "bottom", labels: { color: "#64748B", font: { size: 11 }, padding: 10, boxWidth: 12 } },
                    tooltip: { callbacks: { label: (c) => {
                        const total = c.dataset.data.reduce((a, b) => a + b, 0);
                        const pct = total ? ((c.parsed / total) * 100).toFixed(1) : 0;
                        return ` ${c.label}: ${c.parsed.toLocaleString(undefined,{minimumFractionDigits:2})} (${pct}%)`;
                    }}},
                },
            },
        });
    }

    async _renderHeatmap() {
        this._destroy("heatmap");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_hourly_heatmap", [period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_heatmap");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const hours = Array.from({length: 24}, (_, i) => `${i.toString().padStart(2,'0')}:00`);
        const datasets = data.days.map((day, di) => ({
            label: day,
            data: data.matrix[di].map((cnt, h) => ({ x: h, y: di, r: Math.min(Math.sqrt(cnt) * 4 + 2, 20), cnt })),
            backgroundColor: "#7C3AED99", borderColor: "#7C3AED", borderWidth: 1,
        }));
        this._charts.heatmap = new Chart(ctx, {
            type: "bubble", data: { datasets },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${data.days[c.parsed.y]} ${hours[c.parsed.x]}: ${c.raw.cnt} orders` } } },
                scales: {
                    x: { min: -0.5, max: 23.5, grid: { color: "#F8FAFC" }, ticks: { color: "#94A3B8", font: { size: 10 }, callback: (v) => `${v.toString().padStart(2,'0')}h`, stepSize: 1 } },
                    y: { min: -0.5, max: 6.5, grid: { color: "#F8FAFC" }, reverse: true, ticks: { color: "#64748B", font: { size: 11 }, callback: (v) => data.days[Math.round(v)] || "", stepSize: 1 } },
                },
            },
        });
    }

    // ── Products charts ───────────────────────────────────────────────────────

    async _renderProducts() {
        this._destroy("products");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_top_products", [10, period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_products");
        if (!canvas || !data.names.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.products = new Chart(ctx, {
            type: "bar",
            data: { labels: data.names, datasets: [{ label: _t("Qty"), data: data.qty, backgroundColor: P.slice(0, data.names.length).map(c => c + "BB"), borderColor: P.slice(0, data.names.length), borderWidth: 1, borderRadius: 4 }] },
            options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${c.parsed.x} units` } } },
                scales: { x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 } } }, y: { ticks: { color: "#475569", font: { size: 11 } }, grid: { display: false } } } },
        });
    }

    async _renderProductsByRevenue() {
        this._destroy("products_rev");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_top_products_by_revenue", [10, period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_products_revenue");
        if (!canvas || !data.names.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.products_rev = new Chart(ctx, {
            type: "bar",
            data: { labels: data.names, datasets: [{ label: _t("Revenue"), data: data.revenue, backgroundColor: "#2563EB44", borderColor: "#2563EB", borderWidth: 1, borderRadius: 4 }] },
            options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${c.parsed.x.toLocaleString(undefined,{minimumFractionDigits:2})}` } } },
                scales: { x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } }, y: { ticks: { color: "#475569", font: { size: 11 } }, grid: { display: false } } } },
        });
    }

    async _renderCategories() {
        this._destroy("categories");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_top_categories", [10, period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_categories");
        if (!canvas || !data.names.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.categories = new Chart(ctx, {
            type: "bar",
            data: { labels: data.names, datasets: [{ label: _t("Qty"), data: data.qty, backgroundColor: "#14B8A644", borderColor: "#14B8A6", borderWidth: 2, borderRadius: 4 }] },
            options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${c.parsed.x} units` } } },
                scales: { x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 } } }, y: { ticks: { color: "#475569", font: { size: 11 } }, grid: { display: false } } } },
        });
    }

    // ── Customers charts ──────────────────────────────────────────────────────

    async _renderCustomers() {
        this._destroy("customers");
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        const data = await this.orm.call("pos.order", "get_top_customers", [10, period, df, dt, cfg, cashier]);
        const canvas = document.getElementById("chart_customers");
        if (!canvas || !data.names.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.customers = new Chart(ctx, {
            type: "bar",
            data: { labels: data.names, datasets: [{ label: _t("Revenue"), data: data.totals, backgroundColor: "#05966944", borderColor: "#059669", borderWidth: 2, borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${c.parsed.y.toLocaleString(undefined,{minimumFractionDigits:2})}` } } },
                scales: { x: { ticks: { color: "#475569", font: { size: 11 }, maxRotation: 35 }, grid: { display: false } }, y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } } } },
        });
    }

    async _renderNewVsReturning() {
        this._destroy("nvr");
        const nvr = this.state.new_vs_returning;
        const canvas = document.getElementById("chart_new_vs_returning");
        if (!canvas || !nvr) return;
        const total = nvr.new + nvr.returning + nvr.walk_ins;
        if (!total) return;
        const ctx = canvas.getContext("2d");
        this._charts.nvr = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: [_t("New Customers"), _t("Returning"), _t("Walk-ins")],
                datasets: [{ data: [nvr.new, nvr.returning, nvr.walk_ins], backgroundColor: ["#7C3AED","#059669","#94A3B8"], borderWidth: 2, borderColor: "#fff", hoverOffset: 8 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: "62%",
                plugins: {
                    legend: { position: "bottom", labels: { color: "#64748B", font: { size: 11 }, padding: 10, boxWidth: 12 } },
                    tooltip: { callbacks: { label: (c) => { const pct = total ? ((c.parsed/total)*100).toFixed(1) : 0; return ` ${c.label}: ${c.parsed} (${pct}%)`; } } },
                },
            },
        });
    }

    // ── Financial charts ──────────────────────────────────────────────────────

    async _renderDiscountsByCashier() {
        this._destroy("disc_cashier");
        const fd = this.state.financial_data;
        const canvas = document.getElementById("chart_discounts_cashier");
        if (!canvas || !fd || !fd.discounts_by_cashier.names.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.disc_cashier = new Chart(ctx, {
            type: "bar",
            data: { labels: fd.discounts_by_cashier.names, datasets: [{ label: _t("Discount Given"), data: fd.discounts_by_cashier.values, backgroundColor: "#F59E0B44", borderColor: "#F59E0B", borderWidth: 2, borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${c.parsed.y.toLocaleString(undefined,{minimumFractionDigits:2})}` } } },
                scales: { x: { ticks: { color: "#475569", font: { size: 11 }, maxRotation: 35 }, grid: { display: false } }, y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } } } },
        });
    }

    async _renderMarginByCategory() {
        this._destroy("margin_cat");
        const fd = this.state.financial_data;
        const canvas = document.getElementById("chart_margin_category");
        if (!canvas || !fd || !fd.margin_by_category.names.length) return;
        const ctx = canvas.getContext("2d");
        const margins = fd.margin_by_category.margins;
        this._charts.margin_cat = new Chart(ctx, {
            type: "bar",
            data: {
                labels: fd.margin_by_category.names,
                datasets: [{ label: _t("Gross Margin %"), data: margins,
                    backgroundColor: margins.map(m => m >= 0 ? "#05966944" : "#DC262644"),
                    borderColor: margins.map(m => m >= 0 ? "#059669" : "#DC2626"),
                    borderWidth: 2, borderRadius: 4 }],
            },
            options: { indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` ${c.parsed.x.toFixed(1)}%` } } },
                scales: { x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => `${v}%` } }, y: { ticks: { color: "#475569", font: { size: 11 } }, grid: { display: false } } } },
        });
    }

    async _renderAvgRevByHour() {
        this._destroy("avg_rev_hr");
        const fd = this.state.financial_data;
        const canvas = document.getElementById("chart_avg_rev_hour");
        if (!canvas || !fd) return;
        const ctx = canvas.getContext("2d");
        const data = fd.avg_rev_by_hour;
        this._charts.avg_rev_hr = new Chart(ctx, {
            type: "bar",
            data: { labels: data.labels, datasets: [{ label: _t("Avg Order Value"), data: data.values, backgroundColor: grad(ctx, "#6366F1", "88", "11"), borderColor: "#6366F1", borderWidth: 1.5, borderRadius: 4 }] },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => ` Avg: ${c.parsed.y.toLocaleString(undefined,{minimumFractionDigits:2})}  |  ${data.counts[c.dataIndex]} orders` } } },
                scales: { x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 9 }, maxRotation: 0 } }, y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } } } },
        });
    }

    // ── Comparison chart ──────────────────────────────────────────────────────

    async _renderComparison() {
        this._destroy("comparison");
        const cd = this.state.comparison_data;
        const canvas = document.getElementById("chart_comparison");
        if (!canvas || !cd) return;
        const ctx = canvas.getContext("2d");
        this._charts.comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: cd.labels,
                datasets: [
                    { label: this.state.period_label || _t("Current Period"), data: cd.current, backgroundColor: "#7C3AED55", borderColor: "#7C3AED", borderWidth: 2, borderRadius: 3 },
                    { label: cd.prev_label || _t("Previous Period"),           data: cd.previous, backgroundColor: "#94A3B855", borderColor: "#94A3B8", borderWidth: 2, borderRadius: 3 },
                ],
            },
            options: { responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } }, tooltip: { callbacks: { label: (c) => ` ${c.dataset.label}: ${c.parsed.y.toLocaleString(undefined,{minimumFractionDigits:2})}` } } },
                scales: { x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } }, y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } } } },
        });
    }

    // ── Navigation ────────────────────────────────────────────────────────────

    _nav(model, name, domain = []) {
        this.actionService.doAction({ name: _t(name), type: "ir.actions.act_window",
            res_model: model, view_mode: "list,form",
            views: [[false,"list"],[false,"form"]], domain, target: "current" });
    }
    onClickRevenue()     { this._nav("pos.order",      "Orders",           [["amount_total",">",0]]); }
    onClickOrders()      { this._nav("pos.order",      "Orders",           [["amount_total",">",0]]); }
    onClickRefunds()     { this._nav("pos.order",      "Refunds",          [["amount_total","<",0]]); }
    onClickSessions()    { this._nav("pos.session",    "Sessions",         []); }
    onClickItems()       { this._nav("pos.order",      "Orders",           []); }
    onClickAvg()         { this._nav("pos.order",      "Orders",           []); }
    onClickGrossMargin() { this._nav("pos.order.line", "Order Lines",      []); }
    onClickDiscounts()   { this._nav("pos.order.line", "Discounted Lines", [["discount",">",0]]); }
    onClickTax()         { this._nav("pos.order",      "Orders",           [["amount_tax",">",0]]); }

    // ── Export CSV ────────────────────────────────────────────────────────────

    async onExportCSV() {
        const [period, df, dt, cfg, cashier] = this.filterArgs;
        this.state.loading = true;
        try {
            const result = await this.orm.call("pos.order", "get_export_data", [period, df, dt, cfg, cashier]);
            if (!result.rows.length) return;
            const headers = Object.keys(result.rows[0]);
            const lines = [headers.join(",")];
            result.rows.forEach(r => {
                lines.push(headers.map(h => JSON.stringify(r[h] ?? "")).join(","));
            });
            const blob = new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv;charset=utf-8;" });
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement("a");
            a.href = url;
            a.download = `pos_export_${this.state.period}_${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
            if (result.truncated) alert(_t("Export limited to 50,000 rows. Use a smaller date range for full data."));
        } finally {
            this.state.loading = false;
        }
    }

    // ── Change indicators ─────────────────────────────────────────────────────

    changeClass(val) { return (val === null || val === undefined) ? "" : val >= 0 ? "wt-change-up" : "wt-change-down"; }
    changeIcon(val)  { return (val === null || val === undefined) ? "" : val >= 0 ? "fa-arrow-up" : "fa-arrow-down"; }
    changeLabel(val) {
        if (val === null || val === undefined) return "";
        return `${val >= 0 ? "+" : ""}${val}% vs prev`;
    }
}

PosDashboard.template = "PosDashboard";
registry.category("actions").add("pos_order_menu", PosDashboard);
