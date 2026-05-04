"use client";

import {
	AppShell,
	type BreadcrumbItem,
	CanonicalPageTemplate,
	ContextualSidebar,
	IconRail,
	type IconRailGroup,
	PageBreadcrumb,
	type SidebarItemModel,
	ThemeToggle,
	TopBar,
} from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	ScrollText as ScrollTextIcon,
	Send as SendIcon,
	Settings as SettingsIcon,
	ShieldCheck as ShieldCheckIcon,
	Wrench as WrenchIcon,
} from "lucide-react";
import type { ReactNode } from "react";

const ICON_GROUPS: readonly IconRailGroup[] = [
	{
		href: "/overview",
		icon: ActivityIcon,
		id: "observe",
		label: "观测",
		matchPrefixes: ["/overview", "/instances"],
	},
	{
		href: "/alerts",
		icon: BellIcon,
		id: "alert",
		label: "告警",
		matchPrefixes: ["/alerts", "/rules"],
	},
	{
		href: "/instances",
		icon: WrenchIcon,
		id: "operate",
		label: "运维",
		matchPrefixes: ["/operate"],
	},
	{
		href: "/admin/notify-history",
		icon: SettingsIcon,
		id: "admin",
		label: "管理",
		matchPrefixes: ["/admin", "/settings"],
	},
];

const ADMIN_SIDEBAR_ITEMS: readonly SidebarItemModel[] = [
	{ href: "/admin/notify-history", icon: SendIcon, label: "通知投递" },
	{ href: "/admin/channels", icon: ShieldCheckIcon, label: "通道配置" },
	{ href: "/admin/audit", icon: ScrollTextIcon, label: "审计" },
	{ href: "/settings", icon: SettingsIcon, label: "设置" },
];

export interface NotifyShellProps {
	readonly children: ReactNode;
	readonly breadcrumbs: readonly BreadcrumbItem[];
}

const NOOP = (): void => {};

/**
 * Shared AppShell wrapper for the two admin/notify pages.
 * Wires IconRail + ContextualSidebar + TopBar + CanonicalPageTemplate per ADR-0012 D4.
 */
export function NotifyShell(props: NotifyShellProps) {
	const { breadcrumbs, children } = props;
	return (
		<AppShell
			iconRail={
				<IconRail
					footer={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
					groups={ICON_GROUPS}
				/>
			}
			sidebar={
				<ContextualSidebar activeGroup="admin" groupLabel="管理" items={ADMIN_SIDEBAR_ITEMS} />
			}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel="搜索或跳转"
					commandShortcut="⌘K"
					notificationCount={0}
					notificationLabel="通知"
					onCommandOpen={NOOP}
					themeToggle={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
					userAvatar={
						<div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
							DB
						</div>
					}
				/>
			}
		>
			<CanonicalPageTemplate>
				<PageBreadcrumb items={breadcrumbs} />
				{children}
			</CanonicalPageTemplate>
		</AppShell>
	);
}
