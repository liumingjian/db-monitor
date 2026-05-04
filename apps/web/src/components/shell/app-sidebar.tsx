"use client";

import { Sidebar, type SidebarStrings } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { buildSidebarItems } from "./sidebar-items";

/**
 * Application sidebar wired to the project's i18n messages.
 *
 * Source of truth for sidebar items lives in `./sidebar-items.tsx`. Every
 * page-local shell mounts this component on `AppShell.sidebar`. There is no
 * page-level customization of items by design — ADR-0016 D4' requires a
 * single sidebar shape across the app.
 */
export function AppSidebar() {
	const tNav = useTranslations("nav");
	const tSidebar = useTranslations("sidebar");

	const items = buildSidebarItems({
		overview: tNav("overview"),
		instances: tNav("instances"),
		alerts: tNav("alerts"),
		rules: tNav("rules"),
		notifyHistory: tNav("notifyHistory"),
		channels: tNav("channels"),
		audit: tNav("audit"),
		settings: tNav("settings"),
	});

	const strings: SidebarStrings = {
		navigationLabel: tSidebar("navigationLabel"),
		toggleCollapse: tSidebar("toggleCollapse"),
		toggleExpand: tSidebar("toggleExpand"),
		sectionLabels: {
			observe: tNav("observe"),
			alert: tNav("alert"),
			operate: tNav("operate"),
			admin: tNav("admin"),
		},
	};

	return <Sidebar items={items} strings={strings} />;
}
