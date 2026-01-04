/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";

const UPDATE_INTERVAL = 30000; // Update every 30 seconds

class OnlineUsersSystray extends Component {
    static props = {};

    setup() {
        this.state = useState({
            count: 0,
            isVisible: false,
            error: false,
            showPopup: false,
            users: [],
        });
        
        this.rpc = useService("rpc");
        this.userService = useService("user");
        this.notification = useService("notification");
        
        this.intervalId = null;

        onWillStart(async () => {
            await this.checkVisibility();
            if (this.state.isVisible) {
                await this.updateCount();
            }
        });

        onMounted(() => {
            if (this.state.isVisible) {
                this.startUpdating();
            }
        });

        onWillUnmount(() => {
            this.stopUpdating();
        });
    }

    async checkVisibility() {
        try {
            const result = await this.rpc('/online_users/get_visibility_group');
            if (result.success && result.group_xml_id) {
                this.state.isVisible = await this.userService.hasGroup(result.group_xml_id);
            }
        } catch (error) {
            console.error("Error checking visibility:", error);
            this.state.isVisible = false;
        }
    }

    async updateCount() {
        try {
            const result = await this.rpc("/online_users/get_count");
            if (result.success) {
                this.state.count = result.count;
                this.state.error = false;
            } else {
                this.state.error = true;
                console.error("Failed to get online count:", result.error);
            }
        } catch (error) {
            this.state.error = true;
            console.error("RPC Error getting online count:", error);
        }
    }

    async loadOnlineUsers() {
        try {
            const result = await this.rpc("/online_users/get_online_users");
            if (result.success) {
                this.state.users = result.users;
            } else {
                this.notification.add("Failed to load online users", { type: "warning" });
            }
        } catch (error) {
            this.notification.add("Error loading online users", { type: "danger" });
            console.error("Error loading users:", error);
        }
    }

    startUpdating() {
        this.stopUpdating();
        this.intervalId = setInterval(() => {
            this.updateCount();
            // Also refresh the popup if it's open
            if (this.state.showPopup) {
                this.loadOnlineUsers();
            }
        }, UPDATE_INTERVAL);
    }

    stopUpdating() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    get tooltip() {
        if (this.state.error) {
            return "Error updating online users count";
        }
        const userText = this.state.count === 1 ? 'user' : 'users';
        return `${this.state.count} ${userText} currently active`;
    }

    async onSystrayHover() {
        if (!this.state.showPopup) {
            await this.loadOnlineUsers();
        }
        this.state.showPopup = true;
    }

    onSystrayLeave() {
        this.state.showPopup = false;
    }

    getStatusIcon(status) {
        switch(status) {
            case 'online':
                return 'fa fa-circle text-success';
            case 'away':
                return 'fa fa-circle text-warning';
            case 'idle':
                return 'fa fa-circle text-info';
            case 'offline':
                return 'fa fa-circle text-muted';
            default:
                return 'fa fa-circle text-secondary';
        }
    }

    getTimeAgo(timestamp) {
        if (!timestamp) return 'Unknown';
        
        const now = new Date();
        const time = new Date(timestamp);
        const diffMs = now - time;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'now';
        if (diffMins < 60) return `${diffMins} min ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays < 30) return `${diffDays}d ago`;
        
        const diffMonths = Math.floor(diffDays / 30);
        return `${diffMonths}mo ago`;
    }

    getStatusText(user) {
        if (user.status === 'online') {
            return 'Active now';
        }
        if (user.status === 'away') {
            return 'Away';
        }
        return 'Offline';
    }

}

OnlineUsersSystray.template = "simple_online_users.OnlineUsersSystray";

registry.category("systray").add("OnlineUsersSystray", {
    Component: OnlineUsersSystray,
}, { force: true });