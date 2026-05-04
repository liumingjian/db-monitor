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

interface RulesShellProps {
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly children: ReactNode;
	readonly entitySummary: ReactNode;
	readonly username: string;
}

/**
 * Page-local AppShell for /rules and /rules/[ruleId].
 *
 * Slice 1.5b PR β.0 (2026-05-04): consolidated to single-sidebar chrome
 * (ADR-0016 D4'). All sidebar/iconRail labels now resolved by AppSidebar via
 * next-intl, so callers only pass breadcrumbs + content + username.
 */
export function RulesShell({ breadcrumbs, children, entitySummary, username }: RulesShellProps) {
	const tTopbar = useTranslations("topbar");

	return (
		<AppShell
			sidebar={<AppSidebar />}
			topBar={
				<TopBar
					breadcrumbs={breadcrumbs}
					commandLabel={tTopbar("commandPalette")}
					commandShortcut={tTopbar("keyboardShortcut")}
					notificationLabel={tTopbar("notifications")}
					onCommandOpen={NOOP}
					themeToggle={
						<ThemeToggle
							labelDark={tTopbar("themeToggleDark")}
							labelLight={tTopbar("themeToggleLight")}
						/>
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
