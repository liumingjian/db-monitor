"use client";

import { cn } from "@db-monitor/ui";
import type { SettingsGroupId } from "./settings-group-model";

export interface SettingsSideNavEntry {
	readonly id: SettingsGroupId;
	readonly label: string;
	readonly description: string;
	readonly count: number;
}

export interface SettingsSideNavProps {
	readonly entries: readonly SettingsSideNavEntry[];
	readonly activeId: SettingsGroupId;
	readonly onSelect: (id: SettingsGroupId) => void;
}

export function SettingsSideNav(props: SettingsSideNavProps) {
	const { entries, activeId, onSelect } = props;

	return (
		<nav aria-label="Settings" className="flex w-full flex-col gap-1">
			{entries.map((entry) => {
				const isActive = entry.id === activeId;
				return (
					<button
						key={entry.id}
						type="button"
						onClick={() => onSelect(entry.id)}
						aria-current={isActive ? "page" : undefined}
						className={cn(
							"flex w-full flex-col gap-0.5 rounded-md border px-3 py-2 text-left transition-colors",
							"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
							isActive
								? "border-accent/30 bg-accent/10 text-accent"
								: "border-border-hairline bg-bg-elevated text-fg-secondary hover:border-border-subtle hover:text-fg-primary",
						)}
					>
						<div className="flex items-center justify-between gap-2">
							<span className="text-sm font-medium">{entry.label}</span>
							<span
								className={cn(
									"inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 font-mono text-[11px] tabular-nums",
									isActive ? "bg-accent text-on-accent" : "bg-surface-overlay text-fg-muted",
								)}
							>
								{entry.count}
							</span>
						</div>
						<p className="text-xs text-fg-muted">{entry.description}</p>
					</button>
				);
			})}
		</nav>
	);
}
