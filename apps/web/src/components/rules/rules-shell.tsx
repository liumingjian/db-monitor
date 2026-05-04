"use client";

import {
	AppShell,
	CanonicalPageTemplate,
	ContextualSidebar,
	IconRail,
	PageBreadcrumb,
	ThemeToggle,
	TopBar,
} from "@db-monitor/ui";
import type { BreadcrumbItem, IconRailGroup, SidebarItemModel } from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	LifeBuoy as LifeBuoyIcon,
	SlidersHorizontal as RulesIcon,
	Settings as SettingsIcon,
	Wrench as WrenchIcon,
} from "lucide-react";
import type { ReactNode } from "react";

export interface RulesShellLabels {
	readonly observe: string;
	readonly alert: string;
	readonly operate: string;
	readonly admin: string;
	readonly sidebarOverview: string;
	readonly sidebarInstances: string;
	readonly sidebarAlerts: string;
	readonly sidebarRules: string;
	readonly sidebarSettings: string;
	readonly commandLabel: string;
	readonly notificationLabel: string;
	readonly themeToggleDark: string;
	readonly themeToggleLight: string;
}

interface RulesShellProps {
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly children: ReactNode;
	readonly entitySummary: ReactNode;
	readonly labels: RulesShellLabels;
	readonly username: string;
}

const OBSERVE_PREFIXES = ["/overview", "/instances"];
const ALERT_PREFIXES = ["/alerts", "/rules"];
const OPERATE_PREFIXES = ["/instances/:id/processes", "/instances/:id/slow-queries"];
const ADMIN_PREFIXES = ["/admin", "/settings"];

/**
 * Page-local AppShell for Rules + Overrides (child #6).
 * Follows the same disjoint pattern Overview uses; #9 will absorb AppShell into layout.tsx.
 */
export function RulesShell({
	breadcrumbs,
	children,
	entitySummary,
	labels,
	username,
}: RulesShellProps) {
	return (
		<AppShell
			iconRail={
				<IconRail
					footer={
						<ThemeToggle labelDark={labels.themeToggleDark} labelLight={labels.themeToggleLight} />
					}
					groups={buildIconGroups(labels)}
				/>
			}
			sidebar={
				<ContextualSidebar
					activeGroup="alert"
					groupLabel={labels.alert}
					items={buildSidebarItems(labels)}
				/>
			}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel={labels.commandLabel}
					commandShortcut="⌘K"
					notificationLabel={labels.notificationLabel}
					onCommandOpen={NOOP}
					themeToggle={
						<ThemeToggle labelDark={labels.themeToggleDark} labelLight={labels.themeToggleLight} />
					}
					userAvatar={<UserAvatar username={username} />}
				/>
			}
		>
			<CanonicalPageTemplate>
				<PageBreadcrumb items={breadcrumbs} />
				{entitySummary}
				{children}
			</CanonicalPageTemplate>
		</AppShell>
	);
}

function buildIconGroups(labels: RulesShellLabels): readonly IconRailGroup[] {
	return [
		{
			href: "/overview",
			icon: ActivityIcon,
			id: "observe",
			label: labels.observe,
			matchPrefixes: OBSERVE_PREFIXES,
		},
		{
			href: "/alerts",
			icon: BellIcon,
			id: "alert",
			label: labels.alert,
			matchPrefixes: ALERT_PREFIXES,
		},
		{
			href: "/instances",
			icon: WrenchIcon,
			id: "operate",
			label: labels.operate,
			matchPrefixes: OPERATE_PREFIXES,
		},
		{
			href: "/settings",
			icon: SettingsIcon,
			id: "admin",
			label: labels.admin,
			matchPrefixes: ADMIN_PREFIXES,
		},
	];
}

function buildSidebarItems(labels: RulesShellLabels): readonly SidebarItemModel[] {
	return [
		{ href: "/overview", icon: ActivityIcon, label: labels.sidebarOverview },
		{ href: "/instances", icon: LifeBuoyIcon, label: labels.sidebarInstances },
		{ href: "/alerts", icon: BellIcon, label: labels.sidebarAlerts },
		{ href: "/rules", icon: RulesIcon, label: labels.sidebarRules },
		{ href: "/settings", icon: SettingsIcon, label: labels.sidebarSettings },
	];
}

function UserAvatar({ username }: { readonly username: string }) {
	const initials = toInitials(username);
	return (
		<div
			aria-label={username}
			className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent"
			title={username}
		>
			{initials}
		</div>
	);
}

function toInitials(username: string): string {
	const trimmed = username.trim();
	if (trimmed.length === 0) {
		return "DB";
	}
	return trimmed.slice(0, 2).toUpperCase();
}

const NOOP = (): void => {};
