"use client";

import type { SidebarItemModel } from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	LifeBuoy as LifeBuoyIcon,
	SlidersHorizontal as RulesIcon,
	ScrollText as ScrollTextIcon,
	Send as SendIcon,
	Settings as SettingsIcon,
	ShieldCheck as ShieldCheckIcon,
} from "lucide-react";

export interface SidebarItemLabels {
	readonly overview: string;
	readonly instances: string;
	readonly alerts: string;
	readonly rules: string;
	readonly notifyHistory: string;
	readonly channels: string;
	readonly audit: string;
	readonly settings: string;
}

/**
 * The single source of truth for sidebar items shared by every page-local shell.
 * Order within each group is meaningful (matches D6 Tier 1 navigation order).
 * No nesting allowed — children routes (e.g. instance/[id]/processes) must
 * surface via in-page TabBar, not the sidebar (ADR-0016 D4').
 */
export function buildSidebarItems(labels: SidebarItemLabels): readonly SidebarItemModel[] {
	return [
		{ group: "observe", href: "/overview", icon: ActivityIcon, label: labels.overview },
		{ group: "observe", href: "/instances", icon: LifeBuoyIcon, label: labels.instances },
		{ group: "alert", href: "/alerts", icon: BellIcon, label: labels.alerts },
		{ group: "alert", href: "/rules", icon: RulesIcon, label: labels.rules },
		{
			group: "operate",
			href: "/admin/notify-history",
			icon: SendIcon,
			label: labels.notifyHistory,
		},
		{ group: "operate", href: "/admin/channels", icon: ShieldCheckIcon, label: labels.channels },
		{ group: "admin", href: "/admin/audit", icon: ScrollTextIcon, label: labels.audit },
		{ group: "admin", href: "/settings", icon: SettingsIcon, label: labels.settings },
	];
}
