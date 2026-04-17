/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const P = ["#F59E0B","#DC2626","#F97316","#FBBF24","#EF4444",
           "#D97706","#B45309","#92400E","#78350F","#FCD34D"];

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

export class SaleDashboard extends Component {
    static template = "SaleDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this._charts = {};
        this.state = useState({
            period: "month", date_from: "", date_to: "",
            show_custom: false, loading: true, active_tab: "overview",
            period_options: PERIOD_OPTIONS, period_label: "",
            total_revenue: "—", confirmed_orders: 0, avg_order_value: "—",
            quotations: 0, customers: 0, items_sold: 0,
            conversion_rate: "—", tax_collected: "—", pending_delivery: 0,
            recent_orders: [], salesperson_stats: [],
            comparison_data: null,
            last_updated: "",
        });

        onWillStart(async () => { await this._loadAll(); });
        onMounted(async () => {
            this.state.loading = false;
            await this._renderTabCharts("overview");
            this._autoRefreshTimer = setInterval(async () => {
                if (!this.state.loading) await this._applyFilters();
            }, 5 * 60 * 1000);
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
            this.orm.call("sale.order", "get_sale_kpis", [period, df, dt]),
            this.orm.call("sale.order", "get_sale_recent_orders", [period, df, dt]),
            this.orm.call("sale.order", "get_sale_salesperson_stats", [period, df, dt]),
        ]);
        Object.assign(this.state, kpis);
        this.state.recent_orders = recent;
        this.state.salesperson_stats = salesperson;
        const now = new Date();
        this.state.last_updated = now.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    }

    setTab(tab) {
        this.state.active_tab = tab;
        requestAnimationFrame(() => this._renderTabCharts(tab));
    }

    async _renderTabCharts(tab) {
        const [period, df, dt] = this.filterArgs;
        if (tab === "overview") {
            await this._renderTrend("sale_chart_trend");
        } else if (tab === "products") {
            await Promise.all([this._renderTopProductsQty(), this._renderTopProductsRevenue()]);
        } else if (tab === "customers") {
            await this._renderTopCustomers();
        } else if (tab === "salespersons") {
            await this._renderSalesperson();
        } else if (tab === "performance") {
            await this._renderTrend("sale_chart_perf_trend");
        } else if (tab === "comparison") {
            this.state.comparison_data = await this.orm.call(
                "sale.order", "get_sale_comparison", [period, df, dt]);
            await this._renderComparison();
        }
    }

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    async _renderTrend(canvasId) {
        this._destroy(canvasId);
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("sale.order", "get_sale_trend", [period, df, dt]);
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const g = ctx.createLinearGradient(0, 0, 0, 350);
        g.addColorStop(0, "#F59E0BCC");
        g.addColorStop(1, "#F59E0B08");
        this._charts[canvasId] = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Revenue", data: data.values, borderColor: "#F59E0B",
                      backgroundColor: g, borderWidth: 2.5,
                      pointRadius: data.labels.length > 60 ? 0 : 3, fill: true, tension: 0.4, yAxisID: "y" },
                    { label: "Orders", data: data.counts, borderColor: "#10B981",
                      backgroundColor: "transparent", borderWidth: 1.5, borderDash: [4,3],
                      pointRadius: 0, fill: false, tension: 0.4, yAxisID: "y2" },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, position: "left", beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    y2: { grid: { display: false }, position: "right", beginAtZero: true, ticks: { color: "#10B981", font: { size: 10 } } },
                },
            },
        });
    }

    async _renderTopProductsQty() {
        this._destroy("sale_prod_qty");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("sale.order", "get_sale_top_products_qty", [period, df, dt]);
        const canvas = document.getElementById("sale_chart_prod_qty");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.sale_prod_qty = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Qty Sold", data: data.values,
                    backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8" } },
                    y: { grid: { display: false }, ticks: { color: "#64748B", font: { size: 11 } } },
                },
            },
        });
    }

    async _renderTopProductsRevenue() {
        this._destroy("sale_prod_rev");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("sale.order", "get_sale_top_products_revenue", [period, df, dt]);
        const canvas = document.getElementById("sale_chart_prod_rev");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.sale_prod_rev = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Revenue", data: data.values,
                    backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    y: { grid: { display: false }, ticks: { color: "#64748B", font: { size: 11 } } },
                },
            },
        });
    }

    async _renderTopCustomers() {
        this._destroy("sale_customers");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("sale.order", "get_sale_top_customers", [period, df, dt]);
        const canvas = document.getElementById("sale_chart_customers");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.sale_customers = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Revenue", data: data.values,
                    backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    y: { grid: { display: false }, ticks: { color: "#64748B", font: { size: 11 } } },
                },
            },
        });
    }

    async _renderSalesperson() {
        this._destroy("sale_salesperson");
        const data = this.state.salesperson_stats;
        const canvas = document.getElementById("sale_chart_salesperson");
        if (!canvas || !data.length) return;
        const ctx = canvas.getContext("2d");
        const rawVals = data.map(s => {
            const m = s.revenue.match(/[\d,.]+/);
            return m ? parseFloat(m[0].replace(/,/g, '')) : 0;
        });
        this._charts.sale_salesperson = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.map(s => s.name),
                datasets: [{ label: "Revenue", data: rawVals,
                    backgroundColor: P.map(c => c + "55"), borderColor: P, borderWidth: 2, borderRadius: 4 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 11 } } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
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

    onClickRevenue()    { this._nav("sale.order", "Confirmed Orders", [["state","in",["sale","done"]]]); }
    onClickOrders()     { this._nav("sale.order", "Confirmed Orders", [["state","in",["sale","done"]]]); }
    onClickAvgOrder()   { this._nav("sale.order", "Orders", [["state","in",["sale","done"]]]); }
    onClickQuotations() { this._nav("sale.order", "Quotations", [["state","in",["draft","sent"]]]); }
    onClickCustomers()  { this._nav("res.partner", "Customers", [["customer_rank",">",0]]); }
    onClickItems()      { this._nav("sale.order.line", "Order Lines", []); }
    onClickConversion() { this._nav("sale.order", "Orders", []); }
    onClickTax()        { this._nav("sale.order", "Orders", [["state","in",["sale","done"]]]); }
    onClickDelivery()   { this._nav("stock.picking", "Pending Deliveries", [["state","not in",["done","cancel"]]]); }
    onRowClick(id)      { this._navRecord("sale.order", id); }

    async _renderComparison() {
        this._destroy("sale_comparison");
        const data = this.state.comparison_data;
        if (!data) return;
        const canvas = document.getElementById("sale_chart_comparison");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.sale_comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: data.current_label, data: data.current_vals, backgroundColor: "#F59E0B66", borderColor: "#F59E0B", borderWidth: 2, borderRadius: 4 },
                    { label: data.prev_label, data: data.prev_vals, backgroundColor: "#94A3B844", borderColor: "#94A3B8", borderWidth: 2, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                },
            },
        });
    }

    exportOrders() {
        const rows = this.state.recent_orders;
        if (!rows.length) return;
        const headers = ["Order","Customer","Date","Subtotal","Total","Status"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.customer, r.date, r.subtotal, r.total, r.state].map(v => `"${v}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "sale_orders.csv");
    }

    exportSalespersons() {
        const rows = this.state.salesperson_stats;
        if (!rows.length) return;
        const headers = ["Name","Orders","Revenue","Avg Order"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.orders, r.revenue, r.avg].map(v => `"${v}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "sale_salespersons.csv");
    }

    _downloadCsv(csv, filename) {
        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
    }
}

registry.category("actions").add("SaleDashboard", SaleDashboard);
