"use client";

import { BellRing as BellRingIcon } from "lucide-react";
import type { ReactNode } from "react";
import { Breadcrumb } from "./breadcrumb";
import type { BreadcrumbItem } from "./types";
import { cn } from "./utils";

export interface TopBarProps {
	readonly breadcrumbs: readonly BreadcrumbItem[];
	readonly commandLabel: string;
	readonly commandShortcut: string;
	readonly onCommandOpen: () => void;
	readonly notificationCount?: number;
	readonly notificationLabel: string;
	readonly onNotificationsOpen?: () => void;
	readonly themeToggle: ReactNode;
	readonly userAvatar: ReactNode;
	/** Optional slot rendered before the breadcrumb (e.g. mobile sidebar trigger). */
	readonly leadingSlot?: ReactNode;
}

/**
 * 56px top bar. Left = breadcrumb, center = command palette trigger,
 * right = theme toggle + notifications + user avatar.
 */
export function TopBar(props: TopBarProps) {
	const {
		breadcrumbs,
		commandLabel,
		commandShortcut,
		onCommandOpen,
		notificationCount,
		notificationLabel,
		onNotificationsOpen,
		themeToggle,
		userAvatar,
		leadingSlot,
	} = props;

	const badge =
		typeof notificationCount === "number" && notificationCount > 0
			? notificationCount > 99
				? "99+"
				: String(notificationCount)
			: null;

	return (
		<div className="flex w-full items-center gap-2 px-4 md:gap-4">
			{leadingSlot ? <div className="flex flex-initial items-center">{leadingSlot}</div> : null}
			<div className="min-w-0 flex-1">
				<Breadcrumb items={breadcrumbs} />
			</div>
			<div className="hidden flex-initial md:block">
				<button
					type="button"
					onClick={onCommandOpen}
					className={cn(
						"inline-flex h-8 items-center gap-2 rounded-md border border-border-strong bg-bg-elevated px-3 shadow-sm",
						"text-sm text-fg-secondary transition-colors",
						"hover:text-fg-primary hover:border-border-strong hover:shadow",
						"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
					)}
				>
					<span>{commandLabel}</span>
					<kbd className="rounded border border-border-strong bg-bg-base px-1.5 py-0.5 font-mono text-[11px] text-fg-secondary">
						{commandShortcut}
					</kbd>
				</button>
			</div>
			<div className="flex flex-initial items-center gap-1">
				{themeToggle}
				<button
					type="button"
					onClick={onNotificationsOpen}
					aria-label={notificationLabel}
					title={notificationLabel}
					className={cn(
						"relative inline-flex h-8 w-8 items-center justify-center rounded-md",
						"text-fg-secondary transition-colors hover:text-fg-primary hover:bg-surface-overlay",
						"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
					)}
				>
					<BellRingIcon className="h-4 w-4" aria-hidden="true" />
					{badge ? (
						<span
							className={cn(
								"absolute -right-0.5 -top-0.5 inline-flex h-4 min-w-4 items-center justify-center",
								"rounded-full bg-sev-critical px-1 font-mono text-[10px] leading-none text-fg-primary",
							)}
						>
							{badge}
						</span>
					) : null}
				</button>
				<div className="ml-1 flex items-center">{userAvatar}</div>
			</div>
		</div>
	);
}
