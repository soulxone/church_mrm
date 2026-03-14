/* Church MRM - Desk Integration */

// Register custom SVG icon for the Church MRM module
frappe.provide("frappe.ui");

$(document).ready(function () {
    // Register custom icon in Frappe's icon system
    if (frappe.ui.icon && frappe.ui.icon.register) {
        frappe.ui.icon.register("church_mrm", {
            svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2v4"/>
                <path d="M9 4h6"/>
                <path d="M12 6l-4 6h8l-4-6z"/>
                <path d="M8 12v8"/>
                <path d="M16 12v8"/>
                <path d="M4 14l4-2"/>
                <path d="M20 14l-4-2"/>
                <path d="M4 14v6h4"/>
                <path d="M20 14v6h-4"/>
                <path d="M10 16h4v4h-4z"/>
                <path d="M4 20h16"/>
            </svg>`,
        });
    }

    // Add Church MRM icon to sidebar if workspace exists
    setTimeout(function () {
        const sidebarLinks = document.querySelectorAll(
            '.desk-sidebar a[title="Church MRM"], .sidebar-menu a[href="/app/church-mrm"]'
        );
        sidebarLinks.forEach(function (link) {
            if (!link.querySelector(".church-mrm-sidebar-icon")) {
                const iconEl = document.createElement("img");
                iconEl.src = "/assets/church_mrm/images/church_mrm.svg";
                iconEl.className = "church-mrm-sidebar-icon";
                iconEl.style.cssText =
                    "width:20px;height:20px;border-radius:4px;margin-right:6px;vertical-align:middle;";
                link.prepend(iconEl);
            }
        });
    }, 1000);
});

// Extend Frappe's module_icon helper to recognize church_mrm
if (frappe.boot && frappe.boot.module_icons) {
    frappe.boot.module_icons["Church MRM"] =
        "/assets/church_mrm/images/church_mrm.svg";
}
