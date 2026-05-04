import type { SidebarGroup } from "@db-monitor/ui";

/**
 * Route → top-level sidebar group. The single source of truth for breadcrumb
 * roots so /admin/notify-history reads "运维" (operate), not "管理" (admin).
 *
 * Must stay in sync with `buildSidebarItems` in ./sidebar-items.tsx.
 */
const SIDEBAR_GROUP_BY_HREF: Readonly<Record<string, SidebarGroup>> = {
	"/overview": "observe",
	"/instances": "observe",
	"/alerts": "alert",
	"/rules": "alert",
	"/admin/notify-history": "operate",
	"/admin/channels": "operate",
	"/admin/audit": "admin",
	"/settings": "admin",
};

/**
 * Resolve the top-level sidebar group for an app route. Falls back to
 * `observe` so an unmapped path still gets a sensible breadcrumb root.
 */
export function groupForHref(href: string): SidebarGroup {
	return SIDEBAR_GROUP_BY_HREF[href] ?? "observe";
}

/**
 * Pick the canonical landing route for a given sidebar group. Used by
 * breadcrumb roots so clicking the root takes the user to that group's
 * primary page (e.g. operate → /admin/notify-history).
 */
export function rootHrefForGroup(group: SidebarGroup): string {
	switch (group) {
		case "observe":
			return "/overview";
		case "alert":
			return "/alerts";
		case "operate":
			return "/admin/notify-history";
		case "admin":
			return "/settings";
	}
}
