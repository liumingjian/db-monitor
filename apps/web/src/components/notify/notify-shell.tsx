"use client";

import {
	AppShell,
	type BreadcrumbItem,
	CanonicalPageTemplate,
	PageBreadcrumb,
	ThemeToggle,
	TopBar,
} from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

import { AppSidebar } from "../shell/app-sidebar";

export interface NotifyShellProps {
	readonly children: ReactNode;
	readonly breadcrumbs: readonly BreadcrumbItem[];
}

const NOOP = (): void => {};

/**
 * Shared AppShell wrapper for the two admin/notify pages.
 *
 * Slice 1.5b PR β.0 (2026-05-04): consolidated to single-sidebar chrome
 * (ADR-0016 D4'); previously had a misrouted admin IconRail group and a dead
 * /operate matchPrefix.
 */
export function NotifyShell(props: NotifyShellProps) {
	const { breadcrumbs, children } = props;
	const tTopbar = useTranslations("topbar");

	return (
		<AppShell
			sidebar={<AppSidebar />}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel={tTopbar("commandPalette")}
					commandShortcut={tTopbar("keyboardShortcut")}
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
