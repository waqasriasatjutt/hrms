/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const P = ["#7C3AED","#2563EB","#EC4899","#A855F7","#3B82F6","#8B5CF6","#6366F1","#C026D3","#4F46E5","#7C3AED"];

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

export class PurchaseDashboard extends Component {
    static template = "PurchaseDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this._charts = {};
        this.state = useState({
            period: "month", date_from: "", date_to: "",
            show_custom: false, loading: true, active_tab: "overview",
            period_options: PERIOD_OPTIONS, period_label: "",
            total_spend: "—", purchase_orders: 0, avg_po_value: "—",
            rfqs: 0, vendors: 0, items_ordered: 0,
            bills_to_process: 0, overdue_bills: 0, tax_amount: "—",
            recent_pos: [], vendor_stats: [],
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
        const [kpis, recent, vendorStats] = await Promise.all([
            this.orm.call("purchase.order", "get_purchase_kpis", [period, df, dt]),
            this.orm.call("purchase.order", "get_purchase_recent_pos", [period, df, dt]),
            this.orm.call("purchase.order", "get_purchase_vendor_stats", [period, df, dt]),
        ]);
        Object.assign(this.state, kpis);
        this.state.recent_pos = recent;
        this.state.vendor_stats = vendorStats;
        const now = new Date();
        this.state.last_updated = now.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    }

    setTab(tab) {
        this.state.active_tab = tab;
        requestAnimationFrame(() => this._renderTabCharts(tab));
    }

    async _renderTabCharts(tab) {
        const [period, df, dt] = this.filterArgs;
        if (tab === "overview") {
            await this._renderTrend("pur_chart_trend");
        } else if (tab === "vendors") {
            await this._renderTopVendors();
        } else if (tab === "products") {
            await Promise.all([this._renderTopProducts(), this._renderSpendCategory()]);
        } else if (tab === "payables") {
            await this._renderRfqVsOrders();
        } else if (tab === "performance") {
            await this._renderTrend("pur_chart_perf_trend");
        } else if (tab === "comparison") {
            this.state.comparison_data = await this.orm.call(
                "purchase.order", "get_purchase_comparison", [period, df, dt]);
            await this._renderComparison();
        }
    }

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    async _renderTrend(canvasId) {
        this._destroy(canvasId);
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("purchase.order", "get_purchase_trend", [period, df, dt]);
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const g = ctx.createLinearGradient(0, 0, 0, 350);
        g.addColorStop(0, "#8B5CF6CC");
        g.addColorStop(1, "#8B5CF608");
        this._charts[canvasId] = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Spend", data: data.values, borderColor: "#8B5CF6",
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

    async _renderTopVendors() {
        this._destroy("pur_top_vendors");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("purchase.order", "get_purchase_top_vendors", [period, df, dt]);
        const canvas = document.getElementById("pur_chart_top_vendors");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.pur_top_vendors = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Spend", data: data.values,
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

    async _renderTopProducts() {
        this._destroy("pur_top_products");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("purchase.order", "get_purchase_top_products", [period, df, dt]);
        const canvas = document.getElementById("pur_chart_top_products");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.pur_top_products = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Qty Ordered", data: data.values,
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

    async _renderSpendCategory() {
        this._destroy("pur_spend_cat");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("purchase.order", "get_purchase_spend_by_category", [period, df, dt]);
        const canvas = document.getElementById("pur_chart_spend_category");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.pur_spend_cat = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: data.labels,
                datasets: [{ data: data.values, backgroundColor: P.map(c => c + "CC"), borderColor: P, borderWidth: 2 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "right", labels: { color: "#64748B", font: { size: 11 }, boxWidth: 12 } } },
            },
        });
    }

    async _renderRfqVsOrders() {
        this._destroy("pur_rfq_orders");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("purchase.order", "get_purchase_rfq_vs_orders", [period, df, dt]);
        const canvas = document.getElementById("pur_chart_rfq_orders");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.pur_rfq_orders = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "RFQs", data: data.rfqs, backgroundColor: "#F59E0B44", borderColor: "#F59E0B", borderWidth: 2, borderRadius: 4 },
                    { label: "Orders", data: data.orders, backgroundColor: "#7C3AED44", borderColor: "#7C3AED", borderWidth: 2, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8" } },
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

    onClickSpend()       { this._nav("purchase.order", "Purchase Orders", [["state","in",["purchase","done"]]]); }
    onClickOrders()      { this._nav("purchase.order", "Purchase Orders", [["state","in",["purchase","done"]]]); }
    onClickAvgPO()       { this._nav("purchase.order", "Purchase Orders", [["state","in",["purchase","done"]]]); }
    onClickRFQs()        { this._nav("purchase.order", "RFQs", [["state","in",["draft","sent"]]]); }
    onClickVendors()     { this._nav("res.partner", "Vendors", [["supplier_rank",">",0]]); }
    onClickItems()       { this._nav("purchase.order.line", "Order Lines", []); }
    onClickBills()       { this._nav("account.move", "Vendor Bills", [["move_type","=","in_invoice"],["state","=","draft"]]); }
    onClickOverdue()     { this._nav("account.move", "Overdue Bills", [["move_type","=","in_invoice"],["payment_state","not in",["paid","reversed"]]]); }
    onClickTax()         { this._nav("purchase.order", "Purchase Orders", [["state","in",["purchase","done"]]]); }
    onRowClick(id)       { this._navRecord("purchase.order", id); }

    async _renderComparison() {
        this._destroy("pur_comparison");
        const data = this.state.comparison_data;
        if (!data) return;
        const canvas = document.getElementById("pur_chart_comparison");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.pur_comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: data.current_label, data: data.current_vals, backgroundColor: "#7C3AED66", borderColor: "#7C3AED", borderWidth: 2, borderRadius: 4 },
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

    exportPOs() {
        const rows = this.state.recent_pos;
        if (!rows.length) return;
        const headers = ["PO Number","Vendor","Date","Amount","Status"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.vendor, r.date, r.amount, r.state].map(v => `"${v||''}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "purchase_orders.csv");
    }

    exportVendors() {
        const rows = this.state.vendor_stats;
        if (!rows.length) return;
        const headers = ["Vendor","Orders","Amount","Avg Order"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.orders, r.amount, r.avg].map(v => `"${v||''}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "purchase_vendors.csv");
    }

    _downloadCsv(csv, filename) {
        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
    }
}

registry.category("actions").add("PurchaseDashboard", PurchaseDashboard);
