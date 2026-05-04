"use client";

import {
	AppShell,
	type BreadcrumbItem,
	ContextualSidebar,
	IconRail,
	type IconRailGroup,
	type SidebarItemModel,
	ThemeToggle,
	ToastProvider,
	TopBar,
} from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	SlidersHorizontal as RulesIcon,
	Settings as SettingsIcon,
	Wrench as WrenchIcon,
} from "lucide-react";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

import type { SessionSnapshot } from "../../auth";

const ICON_GROUPS: readonly IconRailGroup[] = [
	{
		id: "observe",
		label: "观测",
		icon: ActivityIcon,
		href: "/overview",
		matchPrefixes: ["/overview", "/instances"],
	},
	{
		id: "alert",
		label: "告警",
		icon: BellIcon,
		href: "/alerts",
		matchPrefixes: ["/alerts", "/rules"],
	},
	{
		id: "operate",
		label: "运维",
		icon: WrenchIcon,
		href: "/instances",
		matchPrefixes: ["/admin/notify-history", "/admin/channels"],
	},
	{
		id: "admin",
		label: "管理",
		icon: SettingsIcon,
		href: "/settings",
		matchPrefixes: ["/settings", "/admin/audit"],
	},
];

const SIDEBAR_ITEMS: readonly SidebarItemModel[] = [
	{ href: "/alerts", label: "告警", icon: BellIcon },
	{ href: "/rules", label: "规则", icon: RulesIcon },
];

interface AlertsAppShellProps {
	readonly session: SessionSnapshot;
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly children: ReactNode;
}

/**
 * Page-local AppShell wrapper for /alerts and /alerts/[alertId].
 *
 * Replaces the legacy light-theme AppChrome which violated ADR-0012 D2 (dark default).
 * Mirrors InstancesListShell shape: AppShell three-piece chrome + ToastProvider, with
 * children passing through unchanged so AlertsPageShell's CanonicalPageTemplate is not
 * double-wrapped.
 *
 * Slice 1.5b PR α (2026-05-04). #9 (global framework) will absorb AppShell into
 * `app/layout.tsx`; this page-local wrapper is the disjoint-ownership pattern Slice 1.5
 * already established for overview/instances/rules/notify shells.
 */
export function AlertsAppShell(props: AlertsAppShellProps) {
	const { session, breadcrumbs, children } = props;
	const tTopbar = useTranslations("topbar");
	const tNav = useTranslations("nav");

	const initials = resolveInitials(session);

	return (
		<ToastProvider>
			<AppShell
				iconRail={
					<IconRail
						groups={ICON_GROUPS}
						footer={
							<ThemeToggle
								labelDark={tTopbar("themeToggleDark")}
								labelLight={tTopbar("themeToggleLight")}
							/>
						}
					/>
				}
				sidebar={
					<ContextualSidebar activeGroup="alert" groupLabel={tNav("alert")} items={SIDEBAR_ITEMS} />
				}
				topBar={
					<TopBar
						breadcrumbs={breadcrumbs}
						commandLabel={tTopbar("commandPalette")}
						commandShortcut={tTopbar("keyboardShortcut")}
						onCommandOpen={NOOP}
						notificationLabel={tTopbar("notifications")}
						themeToggle={
							<ThemeToggle
								labelDark={tTopbar("themeToggleDark")}
								labelLight={tTopbar("themeToggleLight")}
							/>
						}
						userAvatar={
							<div
								aria-label={session.displayName ?? session.username ?? "user"}
								className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent"
							>
								{initials}
							</div>
						}
					/>
				}
			>
				{children}
			</AppShell>
		</ToastProvider>
	);
}

function resolveInitials(session: SessionSnapshot): string {
	const source = session.displayName ?? session.username ?? "DB";
	const trimmed = source.trim();
	if (trimmed.length === 0) {
		return "DB";
	}
	const parts = trimmed.split(/\s+/).filter((part) => part.length > 0);
	const letters = parts.slice(0, 2).map((part) => part.charAt(0).toUpperCase());
	return letters.join("") || trimmed.charAt(0).toUpperCase();
}

const NOOP = (): void => {};
