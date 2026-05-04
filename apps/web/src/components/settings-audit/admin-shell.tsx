"use client";

import { AppShell, ContextualSidebar, IconRail, ThemeToggle, TopBar } from "@db-monitor/ui";
import type {
	BreadcrumbItem,
	IconRailGroup,
	IconRailGroupId,
	SidebarItemModel,
} from "@db-monitor/ui";
import {
	Activity as ActivityIcon,
	Bell as BellIcon,
	FileText as FileTextIcon,
	Settings as SettingsIcon,
	ShieldCheck as ShieldCheckIcon,
	Wrench as WrenchIcon,
} from "lucide-react";
import type { ReactNode } from "react";

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
		matchPrefixes: ["/instances"],
	},
	{
		id: "admin",
		label: "管理",
		icon: SettingsIcon,
		href: "/settings",
		matchPrefixes: ["/admin", "/settings"],
	},
];

const ADMIN_SIDEBAR_ITEMS: readonly SidebarItemModel[] = [
	{ href: "/settings", label: "设置", icon: SettingsIcon },
	{ href: "/admin/notify-history", label: "通知投递", icon: FileTextIcon },
	{ href: "/admin/audit", label: "审计日志", icon: ShieldCheckIcon },
];

export interface AdminShellProps {
	readonly activeGroup?: IconRailGroupId;
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly userInitials: string;
	readonly children: ReactNode;
}

export function AdminShell(props: AdminShellProps) {
	const { activeGroup = "admin", breadcrumbs, userInitials, children } = props;

	return (
		<AppShell
			iconRail={
				<IconRail
					groups={ICON_GROUPS}
					footer={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
				/>
			}
			sidebar={
				<ContextualSidebar
					activeGroup={activeGroup}
					groupLabel="管理"
					items={ADMIN_SIDEBAR_ITEMS}
				/>
			}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel="搜索或跳转"
					commandShortcut="⌘K"
					onCommandOpen={() => {
						/* 预留 Slice 1.5 子 #9 ⌘K 命令面板接入 */
					}}
					notificationCount={0}
					notificationLabel="通知"
					themeToggle={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
					userAvatar={
						<div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
							{userInitials}
						</div>
					}
				/>
			}
		>
			{children}
		</AppShell>
	);
}
