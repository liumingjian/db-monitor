"use client";

import { X as XIcon } from "lucide-react";
import { useCallback, useEffect } from "react";
import { cn } from "./utils";

export type NotificationTabKey = "alerts" | "notify" | "system";

export interface NotificationEntry {
	readonly id: string;
	readonly title: string;
	readonly body?: string;
	readonly timestampLabel: string;
	readonly tone?: "critical" | "warning" | "info" | "ok";
	readonly href?: string;
}

export interface NotificationTabConfig {
	readonly key: NotificationTabKey;
	readonly label: string;
	readonly entries: readonly NotificationEntry[];
	readonly emptyLabel: string;
}

export interface NotificationDrawerStrings {
	readonly title: string;
	readonly close: string;
	readonly viewAll: string;
}

export interface NotificationDrawerProps {
	readonly open: boolean;
	readonly onOpenChange: (next: boolean) => void;
	readonly activeTab: NotificationTabKey;
	readonly onActiveTabChange: (next: NotificationTabKey) => void;
	readonly tabs: readonly NotificationTabConfig[];
	readonly strings: NotificationDrawerStrings;
}

const SEVERITY_CLASS: Record<NonNullable<NotificationEntry["tone"]>, string> = {
	critical: "bg-sev-critical-bg text-sev-critical border-sev-critical-border",
	warning: "bg-sev-warning-bg text-sev-warning border-sev-warning-border",
	info: "bg-sev-info-bg text-sev-info border-sev-info-border",
	ok: "bg-sev-ok-bg text-sev-ok border-sev-ok-border",
};

export function NotificationDrawer(props: NotificationDrawerProps) {
	const { open, onOpenChange, activeTab, onActiveTabChange, tabs, strings } = props;

	const onClose = useCallback(() => onOpenChange(false), [onOpenChange]);

	useEffect(() => {
		if (!open) {
			return;
		}
		const onKey = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				event.stopPropagation();
				onClose();
			}
		};
		document.addEventListener("keydown", onKey);
		return () => document.removeEventListener("keydown", onKey);
	}, [open, onClose]);

	if (!open) {
		return null;
	}

	const activeConfig = tabs.find((t) => t.key === activeTab) ?? tabs[0];

	return (
		// biome-ignore lint/a11y/useKeyWithClickEvents: Esc already closes via global handler above; click-outside overlay is pointer-only by design.
		<div
			className="fixed inset-0 z-50 flex justify-end bg-bg-deep/60 backdrop-blur-sm"
			role="presentation"
			onClick={(event) => {
				if (event.target === event.currentTarget) {
					onClose();
				}
			}}
		>
			{/* biome-ignore lint/a11y/useSemanticElements: native <dialog> has incompatible open/close semantics; we manage overlay + focus ourselves. */}
			<aside
				role="dialog"
				aria-modal="true"
				aria-label={strings.title}
				className={cn(
					"flex h-full w-full max-w-md flex-col border-l border-border-subtle bg-bg-elevated",
					"text-fg-primary shadow-xl outline-none",
				)}
			>
				<header className="flex items-center justify-between border-b border-border-hairline px-4 py-3">
					<h2 className="text-base font-semibold">{strings.title}</h2>
					<button
						type="button"
						onClick={onClose}
						aria-label={strings.close}
						className={cn(
							"inline-flex h-8 w-8 items-center justify-center rounded-md text-fg-secondary",
							"transition-colors hover:bg-surface-overlay hover:text-fg-primary",
							"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
						)}
					>
						<XIcon className="h-4 w-4" aria-hidden="true" />
					</button>
				</header>
				<nav
					role="tablist"
					aria-label={strings.title}
					className="flex h-11 items-center gap-1 border-b border-border-hairline px-2"
				>
					{tabs.map((tab) => {
						const active = tab.key === activeConfig?.key;
						return (
							<button
								key={tab.key}
								type="button"
								role="tab"
								aria-selected={active}
								tabIndex={active ? 0 : -1}
								onClick={() => onActiveTabChange(tab.key)}
								className={cn(
									"inline-flex h-11 items-center gap-1 border-b-2 px-3 text-sm font-medium transition-colors",
									active
										? "border-accent text-fg-primary"
										: "border-transparent text-fg-muted hover:text-fg-primary",
								)}
							>
								<span>{tab.label}</span>
								{tab.entries.length > 0 ? (
									<span className="ml-1 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-surface-overlay px-1 font-mono text-[10px] text-fg-secondary">
										{tab.entries.length > 99 ? "99+" : tab.entries.length}
									</span>
								) : null}
							</button>
						);
					})}
				</nav>
				<div className="flex-1 overflow-y-auto">
					{activeConfig === undefined || activeConfig.entries.length === 0 ? (
						<EmptyNotifications label={activeConfig?.emptyLabel ?? strings.title} />
					) : (
						<ul className="divide-y divide-border-hairline">
							{activeConfig.entries.map((entry) => (
								<li key={entry.id}>
									<EntryRow entry={entry} />
								</li>
							))}
						</ul>
					)}
				</div>
			</aside>
		</div>
	);
}

function EmptyNotifications(props: { readonly label: string }) {
	return (
		<div className="flex h-full items-center justify-center p-8 text-center text-sm text-fg-muted">
			{props.label}
		</div>
	);
}

function EntryRow(props: { readonly entry: NotificationEntry }) {
	const { entry } = props;
	const toneClass = entry.tone ? SEVERITY_CLASS[entry.tone] : "bg-surface-overlay text-fg-muted";
	const Wrapper: "a" | "div" = entry.href ? "a" : "div";
	const wrapperProps = entry.href ? { href: entry.href } : {};
	return (
		<Wrapper
			{...wrapperProps}
			className={cn(
				"flex items-start gap-3 px-4 py-3 transition-colors",
				entry.href ? "hover:bg-surface-overlay" : undefined,
			)}
		>
			<span
				className={cn("mt-1 inline-flex h-2 w-2 flex-shrink-0 rounded-full border", toneClass)}
				aria-hidden="true"
			/>
			<div className="min-w-0 flex-1">
				<p className="truncate text-sm text-fg-primary">{entry.title}</p>
				{entry.body ? <p className="mt-0.5 text-xs text-fg-muted">{entry.body}</p> : null}
			</div>
			<span className="flex-shrink-0 font-mono text-[11px] text-fg-muted tabular-nums">
				{entry.timestampLabel}
			</span>
		</Wrapper>
	);
}
