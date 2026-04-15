/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const P = ["#1D4ED8","#0EA5E9","#0F172A","#3B82F6","#7C3AED",
           "#06B6D4","#1E40AF","#2563EB","#60A5FA","#93C5FD"];

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

export class AccountingDashboard extends Component {
    static template = "AccountingDashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this._charts = {};
        this.state = useState({
            period: "month", date_from: "", date_to: "",
            show_custom: false, loading: true, active_tab: "overview",
            period_options: PERIOD_OPTIONS, period_label: "",
            total_revenue: "—", total_expenses: "—", net_profit: "—",
            accounts_receivable: "—", accounts_payable: "—",
            outstanding_invoices: 0, overdue_invoices: 0,
            avg_invoice_value: "—", tax_collected: "—",
            recent_invoices: [],
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
        const [kpis, recent] = await Promise.all([
            this.orm.call("account.move", "get_accounting_kpis", [period, df, dt]),
            this.orm.call("account.move", "get_accounting_recent_invoices", [period, df, dt]),
        ]);
        Object.assign(this.state, kpis);
        this.state.recent_invoices = recent;
        const now = new Date();
        this.state.last_updated = now.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    }

    setTab(tab) {
        this.state.active_tab = tab;
        requestAnimationFrame(() => this._renderTabCharts(tab));
    }

    async _renderTabCharts(tab) {
        if (tab === "overview") {
            await Promise.all([this._renderTrend(), this._renderPL()]);
        } else if (tab === "receivables") {
            await Promise.all([this._renderArAging(), this._renderTopCustomers()]);
        } else if (tab === "payables") {
            await Promise.all([this._renderApAging(), this._renderTopVendors()]);
        } else if (tab === "cashflow") {
            await this._renderCashflow();
        } else if (tab === "expenses") {
            await Promise.all([this._renderVendorsExp(), this._renderApAging2()]);
        } else if (tab === "comparison") {
            const [period, df, dt] = this.filterArgs;
            this.state.comparison_data = await this.orm.call(
                "account.move", "get_accounting_comparison", [period, df, dt]);
            await this._renderComparison();
        }
    }

    _destroy(key) {
        if (this._charts[key]) { this._charts[key].destroy(); delete this._charts[key]; }
    }

    async _renderTrend() {
        this._destroy("acc_trend");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_income_expense_trend", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_trend");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_trend = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Income", data: data.income, borderColor: "#1D4ED8",
                      backgroundColor: grad(ctx, "#1D4ED8"), borderWidth: 2.5,
                      pointRadius: 3, pointBackgroundColor: "#1D4ED8", fill: true, tension: 0.4 },
                    { label: "Expenses", data: data.expenses, borderColor: "#EF4444",
                      backgroundColor: grad(ctx, "#EF4444", "44", "08"), borderWidth: 2.5,
                      pointRadius: 3, pointBackgroundColor: "#EF4444", fill: true, tension: 0.4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, ticks: { color: "#94A3B8", font: { size: 10 }, maxTicksLimit: 20 } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 11 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                },
            },
        });
    }

    async _renderPL() {
        this._destroy("acc_pl");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_monthly_pl", ["year", df, dt]);
        const canvas = document.getElementById("acc_chart_pl");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_pl = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Income", data: data.income, backgroundColor: "#1D4ED844", borderColor: "#1D4ED8", borderWidth: 2, borderRadius: 4 },
                    { label: "Expenses", data: data.expenses, backgroundColor: "#EF444444", borderColor: "#EF4444", borderWidth: 2, borderRadius: 4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 11 }, boxWidth: 12 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", font: { size: 10 }, callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                },
            },
        });
    }

    async _renderArAging() {
        this._destroy("acc_ar_aging");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_ar_aging", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_ar_aging");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_ar_aging = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "AR Amount", data: data.values,
                    backgroundColor: ["#10B98144","#1D4ED844","#F59E0B44","#F9731644","#EF444444"],
                    borderColor:      ["#10B981",  "#1D4ED8",  "#F59E0B",  "#F97316",  "#EF4444"],
                    borderWidth: 2, borderRadius: 6 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                },
            },
        });
    }

    async _renderApAging() {
        this._destroy("acc_ap_aging");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_ap_aging", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_ap_aging");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_ap_aging = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "AP Amount", data: data.values,
                    backgroundColor: ["#10B98144","#8B5CF644","#F59E0B44","#F9731644","#EF444444"],
                    borderColor:      ["#10B981",  "#8B5CF6",  "#F59E0B",  "#F97316",  "#EF4444"],
                    borderWidth: 2, borderRadius: 6 }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                    y: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                },
            },
        });
    }

    async _renderApAging2() {
        this._destroy("acc_ap_aging2");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_ap_aging", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_ap_aging2");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_ap_aging2 = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [{ label: "AP Amount", data: data.values,
                    backgroundColor: ["#10B98144","#8B5CF644","#F59E0B44","#F9731644","#EF444444"],
                    borderColor:      ["#10B981",  "#8B5CF6",  "#F59E0B",  "#F97316",  "#EF4444"],
                    borderWidth: 2, borderRadius: 6 }],
            },
            options: {
                indexAxis: "y", responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: "#F1F5F9" }, beginAtZero: true, ticks: { color: "#94A3B8", callback: (v) => v >= 1000 ? (v/1000).toFixed(1)+"K" : v } },
                    y: { grid: { display: false }, ticks: { color: "#94A3B8" } },
                },
            },
        });
    }

    async _renderTopCustomers() {
        this._destroy("acc_top_cust");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_top_customers", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_top_customers");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_top_cust = new Chart(ctx, {
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

    async _renderTopVendors() {
        this._destroy("acc_top_vend");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_top_vendors", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_top_vendors");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_top_vend = new Chart(ctx, {
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

    async _renderVendorsExp() {
        this._destroy("acc_vend_exp");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_top_vendors", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_vendors_exp");
        if (!canvas || !data.labels.length) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_vend_exp = new Chart(ctx, {
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

    async _renderCashflow() {
        this._destroy("acc_cashflow");
        const [period, df, dt] = this.filterArgs;
        const data = await this.orm.call("account.move", "get_accounting_income_expense_trend", [period, df, dt]);
        const canvas = document.getElementById("acc_chart_cashflow");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const netData = data.income.map((v, i) => v - (data.expenses[i] || 0));
        this._charts.acc_cashflow = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: "Income", data: data.income, backgroundColor: "#1D4ED844", borderColor: "#1D4ED8", borderWidth: 2, borderRadius: 4 },
                    { label: "Expenses", data: data.expenses, backgroundColor: "#EF444444", borderColor: "#EF4444", borderWidth: 2, borderRadius: 4 },
                    { label: "Net", data: netData, type: "line", borderColor: "#10B981", borderWidth: 2.5, pointRadius: 3, fill: false, tension: 0.4 },
                ],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { position: "top", labels: { color: "#64748B", font: { size: 12 }, boxWidth: 14 } } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#94A3B8", font: { size: 10 } } },
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

    onClickRevenue()     { this._nav("account.move", "Customer Invoices", [["move_type","=","out_invoice"],["state","=","posted"]]); }
    onClickExpenses()    { this._nav("account.move", "Vendor Bills", [["move_type","=","in_invoice"],["state","=","posted"]]); }
    onClickPending()     { this._nav("account.move", "Draft Invoices", [["state","=","draft"]]); }
    onClickOverdue()     { this._nav("account.move", "Overdue Invoices", [["move_type","=","out_invoice"],["payment_state","not in",["paid","reversed"]],["invoice_date_due","<", new Date().toISOString().slice(0,10)]]); }
    onClickInvoices()    { this._nav("account.move", "Invoices", [["move_type","=","out_invoice"]]); }
    onClickBills()       { this._nav("account.move", "Bills", [["move_type","=","in_invoice"]]); }
    onRowClick(id)       { this._navRecord("account.move", id); }

    async _renderComparison() {
        this._destroy("acc_comparison");
        const data = this.state.comparison_data;
        if (!data) return;
        const canvas = document.getElementById("acc_chart_comparison");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        this._charts.acc_comparison = new Chart(ctx, {
            type: "bar",
            data: {
                labels: data.labels,
                datasets: [
                    { label: data.current_label, data: data.current_vals, backgroundColor: "#1D4ED866", borderColor: "#1D4ED8", borderWidth: 2, borderRadius: 4 },
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

    exportInvoices() {
        const rows = this.state.recent_invoices;
        if (!rows.length) return;
        const headers = ["Invoice","Partner","Date","Due Date","Amount","Status","Type"];
        const csv = [headers.join(","), ...rows.map(r =>
            [r.name, r.partner, r.invoice_date, r.due_date, r.amount, r.state, r.type].map(v => `"${v}"`).join(",")
        )].join("\n");
        this._downloadCsv(csv, "accounting_invoices.csv");
    }

    _downloadCsv(csv, filename) {
        const blob = new Blob([csv], {type: "text/csv;charset=utf-8;"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = filename; a.click();
        URL.revokeObjectURL(url);
    }
}

registry.category("actions").add("AccountingDashboard", AccountingDashboard);
