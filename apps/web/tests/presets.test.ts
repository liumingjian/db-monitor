import { describe, expect, it } from "vitest";

import { OVERVIEW_PRESETS, buildInstancePresets } from "../src/analytics-presets";

describe("analytics presets", () => {
	it("keeps overview presets route-backed and tied to stable windows", () => {
		expect(OVERVIEW_PRESETS.map((preset) => preset.label)).toEqual([
			"Live Load",
			"Shift Capacity",
			"Daily Capacity",
		]);
		expect(OVERVIEW_PRESETS.map((preset) => preset.href)).toEqual([
			"/overview?window=15m",
			"/overview?window=6h",
			"/overview?window=24h",
		]);
		expect(OVERVIEW_PRESETS.map((preset) => preset.description)).toEqual([
			"15m fleet pulse for live health shifts, active metric coverage, and workload direction on supported engines.",
			"6h fleet readout for shift handoff, sustained pressure, and coverage changes across observed engines.",
			"24h fleet baseline for growth, recurring health movement, and long-window workload pressure across covered engines.",
		]);
	});

	it("builds instance presets from the canonical detail route", () => {
		expect(buildInstancePresets("inst-prod-primary")).toEqual([
			{
				description: "15m instance pulse for hot-path triage and immediate workload direction.",
				href: "/instances/inst-prod-primary?window=15m",
				label: "Hot Path",
				window: "15m",
			},
			{
				description: "6h balance check for concurrency, wait pressure, and engine stability.",
				href: "/instances/inst-prod-primary?window=6h",
				label: "Stability Sweep",
				window: "6h",
			},
			{
				description: "24h drift view for slow saturation and recurring workload pressure.",
				href: "/instances/inst-prod-primary?window=24h",
				label: "Daily Drift",
				window: "24h",
			},
		]);
	});
});
