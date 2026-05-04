"use client";

import {
	AppShell,
	CanonicalPageTemplate,
	ContextualSidebar,
	IconRail,
	PageBreadcrumb,
	TabBar,
	ThemeToggle,
	TopBar,
} from "@db-monitor/ui";
import type { BreadcrumbItem, IconRailGroup, SidebarItemModel, TabItem } from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	LifeBuoy as LifeBuoyIcon,
	Settings as SettingsIcon,
	Wrench as WrenchIcon,
} from "lucide-react";
import type { ReactNode } from "react";

interface OverviewShellProps {
	readonly entitySummary: ReactNode;
	readonly quickMetrics: ReactNode;
	readonly children: ReactNode;
	readonly username: string;
	readonly labels: OverviewShellLabels;
}

export interface OverviewShellLabels {
	readonly observe: string;
	readonly alert: string;
	readonly operate: string;
	readonly admin: string;
	readonly sidebarOverview: string;
	readonly sidebarInstances: string;
	readonly sidebarAlerts: string;
	readonly sidebarRules: string;
	readonly sidebarSettings: string;
	readonly breadcrumbObserve: string;
	readonly breadcrumbOverview: string;
	readonly commandLabel: string;
	readonly notificationLabel: string;
	readonly themeToggleDark: string;
	readonly themeToggleLight: string;
	readonly tabSummary: string;
}

const OBSERVE_PREFIXES = ["/overview", "/instances", "/design-demo"];
const ALERT_PREFIXES = ["/alerts", "/rules"];
const OPERATE_PREFIXES = ["/instances/:id/processes", "/instances/:id/slow-queries"];
const ADMIN_PREFIXES = ["/admin", "/settings"];

/**
 * Page-local AppShell for Overview.
 *
 * Dedicated to child #2; #9 (global framework) will absorb AppShell into `app/layout.tsx`.
 * Kept inside the overview scope so Slice 1.5 disjoint ownership holds.
 */
export function OverviewShell(props: OverviewShellProps) {
	const { entitySummary, quickMetrics, children, username, labels } = props;

	const iconGroups = buildIconGroups(labels);
	const sidebarItems = buildSidebarItems(labels);
	const breadcrumbs = buildBreadcrumbs(labels);
	const tabs = buildTabs(labels);

	return (
		<AppShell
			iconRail={
				<IconRail
					groups={iconGroups}
					footer={
						<ThemeToggle labelDark={labels.themeToggleDark} labelLight={labels.themeToggleLight} />
					}
				/>
			}
			sidebar={
				<ContextualSidebar activeGroup="observe" groupLabel={labels.observe} items={sidebarItems} />
			}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel={labels.commandLabel}
					commandShortcut="⌘K"
					onCommandOpen={NOOP}
					notificationLabel={labels.notificationLabel}
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
				{quickMetrics}
				<TabBar tabs={tabs} activeKey="summary" />
				{children}
			</CanonicalPageTemplate>
		</AppShell>
	);
}

function buildIconGroups(labels: OverviewShellLabels): readonly IconRailGroup[] {
	return [
		{
			id: "observe",
			label: labels.observe,
			icon: ActivityIcon,
			href: "/overview",
			matchPrefixes: OBSERVE_PREFIXES,
		},
		{
			id: "alert",
			label: labels.alert,
			icon: BellIcon,
			href: "/alerts",
			matchPrefixes: ALERT_PREFIXES,
		},
		{
			id: "operate",
			label: labels.operate,
			icon: WrenchIcon,
			href: "/instances",
			matchPrefixes: OPERATE_PREFIXES,
		},
		{
			id: "admin",
			label: labels.admin,
			icon: SettingsIcon,
			href: "/settings",
			matchPrefixes: ADMIN_PREFIXES,
		},
	];
}

function buildSidebarItems(labels: OverviewShellLabels): readonly SidebarItemModel[] {
	return [
		{ href: "/overview", label: labels.sidebarOverview, icon: ActivityIcon },
		{ href: "/instances", label: labels.sidebarInstances, icon: LifeBuoyIcon },
		{ href: "/alerts", label: labels.sidebarAlerts, icon: BellIcon },
		{ href: "/rules", label: labels.sidebarRules },
		{ href: "/settings", label: labels.sidebarSettings, icon: SettingsIcon },
	];
}

function buildBreadcrumbs(labels: OverviewShellLabels): readonly BreadcrumbItem[] {
	return [
		{ label: labels.breadcrumbObserve, href: "/overview" },
		{ label: labels.breadcrumbOverview },
	];
}

function buildTabs(labels: OverviewShellLabels): readonly TabItem[] {
	return [{ key: "summary", label: labels.tabSummary }];
}

function UserAvatar({ username }: { readonly username: string }) {
	const initials = toInitials(username);
	return (
		<div
			className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent"
			aria-label={username}
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
