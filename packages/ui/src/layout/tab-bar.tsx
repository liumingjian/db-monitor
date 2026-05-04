"use client";

import Link from "next/link";
import type { TabItem } from "./types";
import { cn } from "./utils";

export interface TabBarProps {
	readonly tabs: readonly TabItem[];
	readonly activeKey: string;
	readonly onChange?: (key: string) => void;
	readonly className?: string;
}

/**
 * 44px tab strip. When a tab has `href`, it renders as a Link (for SSR nav);
 * otherwise it renders as a button that calls `onChange`.
 */
export function TabBar(props: TabBarProps) {
	const { tabs, activeKey, onChange, className } = props;

	return (
		<div
			role="tablist"
			className={cn(
				"flex h-11 shrink-0 items-stretch gap-1 border-b border-border-hairline px-4",
				className,
			)}
		>
			{tabs.map((tab) => {
				const active = tab.key === activeKey;
				const content = (
					<span className="flex items-center gap-2">
						<span>{tab.label}</span>
						{tab.badge !== undefined ? (
							<span
								className={cn(
									"inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5",
									"text-[11px] font-medium",
									active ? "bg-accent/20 text-accent" : "bg-surface-overlay text-fg-muted",
								)}
							>
								{tab.badge}
							</span>
						) : null}
					</span>
				);
				const commonClass = cn(
					"relative inline-flex items-center px-3 text-sm transition-colors",
					"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
					tab.disabled
						? "cursor-not-allowed text-fg-disabled"
						: active
							? "text-fg-primary"
							: "text-fg-muted hover:text-fg-primary",
				);
				const indicator = (
					<span
						aria-hidden="true"
						className={cn(
							"absolute inset-x-0 -bottom-px h-0.5 bg-accent transition-opacity",
							active ? "opacity-100" : "opacity-0",
						)}
					/>
				);

				if (tab.href && !tab.disabled) {
					return (
						<Link
							key={tab.key}
							href={tab.href}
							role="tab"
							aria-selected={active}
							aria-current={active ? "page" : undefined}
							className={commonClass}
						>
							{content}
							{indicator}
						</Link>
					);
				}
				return (
					<button
						key={tab.key}
						type="button"
						role="tab"
						aria-selected={active}
						disabled={tab.disabled}
						onClick={() => {
							if (!tab.disabled) {
								onChange?.(tab.key);
							}
						}}
						className={commonClass}
					>
						{content}
						{indicator}
					</button>
				);
			})}
		</div>
	);
}
