"use client";

import {
	AppShell,
	ContextualSidebar,
	IconRail,
	ThemeToggle,
	ToastProvider,
	TopBar,
} from "@db-monitor/ui";
import type { IconRailGroup, SidebarItemModel } from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	LifeBuoy as LifeBuoyIcon,
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
	{ href: "/overview", label: "总览", icon: ActivityIcon },
	{ href: "/instances", label: "实例", icon: LifeBuoyIcon },
];

interface InstancesListShellProps {
	readonly session: SessionSnapshot;
	readonly instanceCount: number;
	readonly children: ReactNode;
}

/**
 * Page-local AppShell assembly for /instances.
 *
 * Temporary until child #9 absorbs the shell into `app/layout.tsx`. Keep API
 * surface narrow so the later migration is a drop-in swap.
 */
export function InstancesListShell(props: InstancesListShellProps) {
	const { session, instanceCount, children } = props;
	const t = useTranslations("instancesPage");
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
					<ContextualSidebar
						activeGroup="observe"
						groupLabel={tNav("observe")}
						items={SIDEBAR_ITEMS.map((item) =>
							item.href === "/instances"
								? { ...item, badge: instanceCount > 0 ? String(instanceCount) : undefined }
								: item,
						)}
					/>
				}
				topBar={
					<TopBar
						breadcrumbs={[
							{ label: tNav("observe"), href: "/overview" },
							{ label: t("breadcrumbInstances") },
						]}
						commandLabel={tTopbar("commandPalette")}
						commandShortcut={tTopbar("keyboardShortcut")}
						onCommandOpen={() => {
							/* 归 #9 的全局 command palette；此处保留触发器外观但不挂载面板 */
						}}
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
