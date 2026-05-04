"use client";

import {
	AppShell,
	type BreadcrumbItem,
	SidebarMenuButton,
	ThemeToggle,
	TopBar,
} from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

import { AppSidebar } from "../shell/app-sidebar";

export interface AdminShellProps {
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly userInitials: string;
	readonly children: ReactNode;
}

/**
 * Page-local AppShell for /settings and /admin/audit.
 *
 * Slice 1.5b PR β.0 (2026-05-04): consolidated to single-sidebar chrome
 * (ADR-0016 D4'); i18n driven by next-intl.
 */
export function AdminShell(props: AdminShellProps) {
	const { breadcrumbs, userInitials, children } = props;
	const tTopbar = useTranslations("topbar");
	const tSidebar = useTranslations("sidebar");

	return (
		<AppShell
			sidebar={<AppSidebar />}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel={tTopbar("commandPalette")}
					commandShortcut={tTopbar("keyboardShortcut")}
					leadingSlot={<SidebarMenuButton label={tSidebar("openMenu")} />}
					notificationCount={0}
					notificationLabel={tTopbar("notifications")}
					onCommandOpen={NOOP}
					themeToggle={
						<ThemeToggle
							labelDark={tTopbar("themeToggleDark")}
							labelLight={tTopbar("themeToggleLight")}
						/>
					}
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

const NOOP = (): void => {};
