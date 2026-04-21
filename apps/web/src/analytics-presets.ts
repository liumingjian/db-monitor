import type { TimeWindow } from "@db-monitor/api-client";

export interface AnalyticsPreset {
	readonly description: string;
	readonly href: string;
	readonly label: string;
	readonly window: TimeWindow;
}

export const OVERVIEW_PRESETS: readonly AnalyticsPreset[] = [
	{
		description:
			"15m fleet pulse for live health shifts, active metric coverage, and workload direction on supported engines.",
		href: buildPresetHref("/overview", "15m"),
		label: "Live Load",
		window: "15m",
	},
	{
		description:
			"6h fleet readout for shift handoff, sustained pressure, and coverage changes across observed engines.",
		href: buildPresetHref("/overview", "6h"),
		label: "Shift Capacity",
		window: "6h",
	},
	{
		description:
			"24h fleet baseline for growth, recurring health movement, and long-window workload pressure across covered engines.",
		href: buildPresetHref("/overview", "24h"),
		label: "Daily Capacity",
		window: "24h",
	},
];

export function buildInstancePresets(instanceId: string): readonly AnalyticsPreset[] {
	return [
		{
			description: "15m instance pulse for hot-path triage and immediate workload direction.",
			href: buildPresetHref(`/instances/${instanceId}`, "15m"),
			label: "Hot Path",
			window: "15m",
		},
		{
			description: "6h balance check for concurrency, wait pressure, and engine stability.",
			href: buildPresetHref(`/instances/${instanceId}`, "6h"),
			label: "Stability Sweep",
			window: "6h",
		},
		{
			description: "24h drift view for slow saturation and recurring workload pressure.",
			href: buildPresetHref(`/instances/${instanceId}`, "24h"),
			label: "Daily Drift",
			window: "24h",
		},
	];
}

function buildPresetHref(pathname: string, window: TimeWindow): string {
	return `${pathname}?window=${window}`;
}
