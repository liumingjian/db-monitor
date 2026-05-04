"use client";

import { AppShell, SidebarMenuButton, ThemeToggle, ToastProvider, TopBar } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import type { ReactNode } from "react";

import type { SessionSnapshot } from "../../auth";
import { AppSidebar } from "../shell/app-sidebar";

interface InstanceDetailShellProps {
	readonly session: SessionSnapshot;
	readonly instanceName: string;
	readonly children: ReactNode;
}

/**
 * Page-local AppShell for /instances/[instanceId]/**.
 *
 * Slice 1.5b PR β.0 (2026-05-04): consolidated to single-sidebar chrome
 * (ADR-0016 D4'). i18n previously hardcoded — now driven by next-intl, same
 * as the other six shells.
 */
export function InstanceDetailShell(props: InstanceDetailShellProps) {
	const { session, instanceName, children } = props;
	const tNav = useTranslations("nav");
	const tTopbar = useTranslations("topbar");
	const tSidebar = useTranslations("sidebar");
	const initials = resolveInitials(session);

	return (
		<ToastProvider>
			<AppShell
				sidebar={<AppSidebar />}
				topBar={
					<TopBar
						breadcrumbs={[
							{ label: tNav("observe"), href: "/overview" },
							{ label: tNav("instances"), href: "/instances" },
							{ label: instanceName },
						]}
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
