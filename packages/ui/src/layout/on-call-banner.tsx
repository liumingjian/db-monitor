"use client";

import { BellOff as BellOffIcon, BellRing as BellRingIcon } from "lucide-react";
import { cn } from "./utils";

export interface OnCallBannerStrings {
	readonly labelOn: string;
	readonly labelOff: string;
	readonly hintOn: string;
	readonly hintOff: string;
	readonly remainingTemplate: string;
	readonly permissionDenied: string;
	readonly unsupported: string;
}

export type OnCallPermissionState = "default" | "granted" | "denied" | "unsupported";

export interface OnCallBannerProps {
	readonly enabled: boolean;
	readonly onToggle: () => void;
	readonly remainingMinutes: number | null;
	readonly permission: OnCallPermissionState;
	readonly strings: OnCallBannerStrings;
	readonly className?: string;
}

/**
 * Compact toggle banner shown in TopBar-adjacent area and Alerts page top.
 * Purely presentational; state lives in OnCallProvider.
 */
export function OnCallBanner(props: OnCallBannerProps) {
	const { enabled, onToggle, remainingMinutes, permission, strings, className } = props;
	const Icon = enabled ? BellRingIcon : BellOffIcon;
	const statusText = enabled ? strings.labelOn : strings.labelOff;
	const hint = enabled ? strings.hintOn : strings.hintOff;

	const warning = resolveWarning(enabled, permission, strings);

	return (
		<div
			className={cn(
				"inline-flex items-center gap-3 rounded-md border px-3 py-1.5 text-sm",
				enabled
					? "border-sev-ok-border bg-sev-ok-bg text-fg-primary"
					: "border-border-subtle bg-bg-elevated text-fg-secondary",
				className,
			)}
		>
			<Icon
				className={cn("h-4 w-4", enabled ? "text-sev-ok" : "text-fg-muted")}
				aria-hidden="true"
			/>
			<div className="flex flex-col leading-tight">
				<span className="text-xs font-semibold">{statusText}</span>
				<span className="text-[11px] text-fg-muted">
					{enabled && remainingMinutes !== null
						? strings.remainingTemplate.replace("{minutes}", String(remainingMinutes))
						: hint}
				</span>
				{warning ? <span className="text-[11px] text-sev-warning">{warning}</span> : null}
			</div>
			<button
				type="button"
				onClick={onToggle}
				aria-pressed={enabled}
				className={cn(
					"ml-2 inline-flex h-6 w-10 items-center rounded-full border transition-colors",
					enabled
						? "border-sev-ok-border bg-sev-ok/40 justify-end"
						: "border-border-subtle bg-surface-overlay justify-start",
					"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
				)}
			>
				<span
					className={cn("m-0.5 h-4 w-4 rounded-full", enabled ? "bg-sev-ok" : "bg-fg-muted")}
					aria-hidden="true"
				/>
			</button>
		</div>
	);
}

function resolveWarning(
	enabled: boolean,
	permission: OnCallPermissionState,
	strings: OnCallBannerStrings,
): string | null {
	if (!enabled) {
		return null;
	}
	if (permission === "denied") {
		return strings.permissionDenied;
	}
	if (permission === "unsupported") {
		return strings.unsupported;
	}
	return null;
}
