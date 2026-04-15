/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const P = ["#0D9488","#0284C7","#14B8A6","#06B6D4","#0891B2","#0E7490","#0F766E","#115E59","#5EEAD4","#2DD4BF"];

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

export class InventoryDashboard extends Component {
    static template = "InventoryDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this._charts = {};
        this.state = useState({
            period: "month", date_from: "", date_to: "",
            show_custom: false, loading: true, active_tab: "overview",
            period_options: PERIOD_OPTIONS, period_label: "",
            products_in_stock: 0, stock_value: "—", low_stock_alerts: 0,
            out_of_stock: 0, pending_receipts: 0, pending_deliveries: 0,
            stock_moves: 0, avg_product_value: "—", locations_with_stock: 0,
            low_stock_items: [],
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
        const [kpis, lowStock] = await Promise.all([
            this.orm.call("stock.quant", "get_inventory_kpis", [period, df, dt]),
            this.orm.call("stock.quant", "get_inventory_low_stock_items", [period, df, dt]),
        ]);
        Object.assign(this.state, kpis);
        this.state.low_stock_items = lowStock;
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
            await Promise.all([this._renderTrend(), this._renderCategory("inv_chart_category")]);
        } else if (tab === "levels") {
            await Promise.all([this._renderTopByValue("inv_chart_top_value"), this._renderCategory("inv_chart_category2")]);
        } else if (tab === "movements") {
            await this._renderMovements();
        } else if (tab === "valuation") {
            await this._renderValuation();
        } else if (tab === "comparison") {
            this.state.comparison_data = await this.orm.call(
                "stock.quant", "get_inventory_comparison", [period, df, dt]);
            await this._renderComparison();
        }
    }

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    async _renderTrend() {
        this._destroy("inv_trend");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("stock.quant", "get_inventory_movement_trend", [period, df, dt]);
        const canvas = document.getElementById("inv_chart_trend");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.inv_trend = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Incoming", data: data.incoming, borderColor: "#0D9488",
                      backgroundColor: "#0D948822", borderWidth: 2.5, pointRadius: data.labels.length > 60 ? 0 : 3,
                      fill: true, tension: 0.4 },
                    { label: "Outgoing", data: data.outgoing, borderColor: "#EF4444",
                      backgroundColor: "#EF444422", borderWidth: 2.5, pointRadius: data.labels.length > 60 ? 0 : 3,
                      fill: true, tension: 0.4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 } } },
                },
            },
        });
    }

    async _renderCategory(canvasId) {
        this._destroy(canvasId);
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("stock.quant", "get_inventory_by_category", [period, df, dt]);
        const canvas = document.getElementById(canvasId);
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts[canvasId] = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: data.labels,
                datasets: [{ data: data.values, backgroundColor: P.map(c => c + "CC"), borderColor: P, borderWidth: 2 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { color: "#64748B", font: { size: 11 }, boxWidth: 12 } },
                },
            },
        });
    }

    async _renderMovements() {
        this._destroy("inv_movements");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("stock.quant", "get_inventory_movement_trend", [period, df, dt]);
        const canvas = document.getElementById("inv_chart_movements");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.inv_movements = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Incoming", data: data.incoming, backgroundColor: "#0D948844", borderColor: "#0D9488", borderWidth: 2, borderRadius: 4 },
                    { label: "Outgoing", data: data.outgoing, backgroundColor: "#EF444444", borderColor: "#EF4444", borderWidth: 2, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8" } },
                },
            },
        });
    }

    async _renderTopByValue(canvasId) {
        this._destroy(canvasId);
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("stock.quant", "get_inventory_top_by_value", [period, df, dt]);
        const canvas = document.getElementById(canvasId);
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts[canvasId] = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Stock Value", data: data.values,
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

    async _renderValuation() {
        this._destroy("inv_valuation");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("stock.quant", "get_inventory_top_by_value", [period, df, dt]);
        const canvas = document.getElementById("inv_chart_valuation");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.inv_valuation = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "Stock Value", data: data.values,
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

    onClickProducts()    { this._nav("stock.quant", "Stock", [["location_id.usage","=","internal"],["quantity",">",0]]); }
    onClickStockValue()  { this._nav("stock.quant", "Stock", []); }
    onClickLowStock()    { this._nav("stock.warehouse.orderpoint", "Reorder Rules", []); }
    onClickOutOfStock()  { this._nav("stock.quant", "Out of Stock", [["location_id.usage","=","internal"],["quantity","<=",0]]); }
    onClickReceipts()    { this._nav("stock.picking", "Pending Receipts", [["picking_type_code","=","incoming"],["state","not in",["done","cancel"]]]); }
    onClickDeliveries()  { this._nav("stock.picking", "Pending Deliveries", [["picking_type_code","=","outgoing"],["state","not in",["done","cancel"]]]); }
    onClickMoves()       { this._nav("stock.move", "Stock Moves", [["state","=","done"]]); }
    onClickAvgValue()    { this._nav("stock.quant", "Stock", []); }
    onClickLocations()   { this._nav("stock.location", "Locations", [["usage","=","internal"]]); }
    onRowClick(id)       { this._navRecord("stock.warehouse.orderpoint", id); }

    async _renderComparison() {
        this._destroy("inv_comparison");
        const data = this.state.comparison_data;
        if (!data) return;
        const canvas = document.getElementById("inv_chart_comparison");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.inv_comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: data.current_label, data: data.current_vals, backgroundColor: "#0D948866", borderColor: "#0D9488", borderWidth: 2, borderRadius: 4 },
                    { label: data.prev_label, data: data.prev_vals, backgroundColor: "#94A3B844", borderColor: "#94A3B8", borderWidth: 2, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8" } },
                },
            },
        });
    }

    exportLowStock() {
        const rows = this.state.low_stock_items;
        if (!rows.length) return;
        const headers = ["Product","On Hand","Min Qty","Max Qty","Shortage"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.on_hand, r.min_qty, r.max_qty, r.shortage].map(v => `"${v||0}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "low_stock.csv");
    }

    _downloadCsv(csv, filename) {
        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
    }
}

registry.category("actions").add("InventoryDashboard", InventoryDashboard);
