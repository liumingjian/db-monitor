"use client";

import {
	AppShell,
	type BreadcrumbItem,
	SidebarMenuButton,
	ThemeToggle,
	ToastProvider,
	TopBar,
} from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

import type { SessionSnapshot } from "../../auth";
import { AppSidebar } from "../shell/app-sidebar";

interface AlertsAppShellProps {
	readonly session: SessionSnapshot;
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly children: ReactNode;
}

/**
 * Page-local AppShell wrapper for /alerts and /alerts/[alertId].
 *
 * Slice 1.5b PR β.0 (2026-05-04): chrome topology consolidated to a single
 * sidebar (ADR-0016 D4' supersedes ADR-0012 D4). Children pass through
 * unchanged so AlertsPageShell's CanonicalPageTemplate is not double-wrapped.
 */
export function AlertsAppShell(props: AlertsAppShellProps) {
	const { session, breadcrumbs, children } = props;
	const tTopbar = useTranslations("topbar");
	const tSidebar = useTranslations("sidebar");

	const initials = resolveInitials(session);

	return (
		<ToastProvider>
			<AppShell
				sidebar={<AppSidebar />}
				topBar={
					<TopBar
						breadcrumbs={breadcrumbs}
						commandLabel={tTopbar("commandPalette")}
						commandShortcut={tTopbar("keyboardShortcut")}
						leadingSlot={<SidebarMenuButton label={tSidebar("openMenu")} />}
						notificationLabel={tTopbar("notifications")}
						onCommandOpen={NOOP}
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
