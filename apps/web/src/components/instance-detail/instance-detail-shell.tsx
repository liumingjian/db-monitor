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

interface InstanceDetailShellProps {
	readonly session: SessionSnapshot;
	readonly instanceName: string;
	readonly children: ReactNode;
}

/**
 * Page-local AppShell for /instances/[instanceId]/**.
 *
 * Mirrors InstancesListShell (#3) so the later #9 migration stays a drop-in
 * swap. Breadcrumb and TopBar carry the instance name; tabs live below inside
 * CanonicalPageTemplate rendered by the layout.
 */
export function InstanceDetailShell(props: InstanceDetailShellProps) {
	const { session, instanceName, children } = props;
	const initials = resolveInitials(session);

	return (
		<ToastProvider>
			<AppShell
				iconRail={
					<IconRail
						groups={ICON_GROUPS}
						footer={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
					/>
				}
				sidebar={
					<ContextualSidebar activeGroup="observe" groupLabel="观测" items={SIDEBAR_ITEMS} />
				}
				topBar={
					<TopBar
						breadcrumbs={[
							{ label: "观测", href: "/overview" },
							{ label: "实例", href: "/instances" },
							{ label: instanceName },
						]}
						commandLabel="搜索或跳转"
						commandShortcut="⌘K"
						onCommandOpen={() => {
							/* 归 #9 的全局 command palette；此处保留触发器外观但不挂载面板 */
						}}
						notificationLabel="通知"
						themeToggle={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
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
