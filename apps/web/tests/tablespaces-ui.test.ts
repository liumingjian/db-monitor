import { describe, expect, it } from "vitest";

import type {
	TablespaceEntryResponse,
	TablespaceHistoryEntryResponse,
	TablespaceSnapshotResponse,
} from "@db-monitor/api-client";

import {
	USED_RATE_CRITICAL_THRESHOLD,
	USED_RATE_WARNING_THRESHOLD,
	buildSparklinePoints,
	buildTablespaceViewModel,
	classifyUsedRate,
	formatBytes,
	formatPercent,
	sparklineSvgPath,
} from "../src/tablespaces-ui";

function buildEntry(overrides: Partial<TablespaceEntryResponse> = {}): TablespaceEntryResponse {
	return {
		autoextensible: false,
		status: "ONLINE",
		tablespace_name: "SYSAUX",
		total_bytes: 4_000_000,
		used_bytes: 1_000_000,
		used_rate_percent: 25,
		...overrides,
	};
}

function buildSnapshot(
	entries: readonly TablespaceEntryResponse[],
	snapshotAt: string | null = "2026-04-22T12:00:00+00:00",
): TablespaceSnapshotResponse {
	return { entries, snapshot_at: snapshotAt };
}

describe("classifyUsedRate", () => {
	it("classifies below warning threshold as normal", () => {
		expect(classifyUsedRate(USED_RATE_WARNING_THRESHOLD - 1)).toBe("normal");
	});

	it("classifies between warning and critical as warning", () => {
		expect(classifyUsedRate(USED_RATE_WARNING_THRESHOLD)).toBe("warning");
		expect(classifyUsedRate(USED_RATE_CRITICAL_THRESHOLD - 0.1)).toBe("warning");
	});

	it("classifies equal-or-above critical threshold as critical", () => {
		expect(classifyUsedRate(USED_RATE_CRITICAL_THRESHOLD)).toBe("critical");
		expect(classifyUsedRate(99)).toBe("critical");
	});
});

describe("buildTablespaceViewModel", () => {
	it("sorts entries by used_rate_percent descending and tags each with a band", () => {
		const snapshot = buildSnapshot([
			buildEntry({ tablespace_name: "SYSAUX", used_rate_percent: 25 }),
			buildEntry({ tablespace_name: "USERS", used_rate_percent: 97 }),
			buildEntry({ tablespace_name: "UNDOTBS", used_rate_percent: 90 }),
		]);

		const model = buildTablespaceViewModel(snapshot);

		expect(model.rows.map((row) => row.tablespace_name)).toEqual(["USERS", "UNDOTBS", "SYSAUX"]);
		expect(model.rows[0].band).toBe("critical");
		expect(model.rows[1].band).toBe("warning");
		expect(model.rows[2].band).toBe("normal");
		expect(model.hasSnapshot).toBe(true);
	});

	it("marks empty snapshots via hasSnapshot flag", () => {
		const snapshot = buildSnapshot([], null);
		const model = buildTablespaceViewModel(snapshot);
		expect(model.rows).toHaveLength(0);
		expect(model.hasSnapshot).toBe(false);
		expect(model.snapshotLabel).toBe("尚无快照");
	});
});

describe("formatters", () => {
	it("formats bytes with the largest sensible unit", () => {
		expect(formatBytes(512)).toBe("512 B");
		expect(formatBytes(2048)).toBe("2.00 KB");
		expect(formatBytes(5 * 1024 * 1024)).toBe("5.00 MB");
	});

	it("formats percent to one decimal", () => {
		expect(formatPercent(12.345)).toBe("12.3%");
	});
});

describe("sparkline helpers", () => {
	function makeHistory(values: readonly number[]): readonly TablespaceHistoryEntryResponse[] {
		return values.map((percent, index) => ({
			collected_at: new Date(Date.UTC(2026, 3, 22, 0, index)).toISOString(),
			total_bytes: 1_000,
			used_bytes: 1_000 * percent,
			used_rate_percent: percent,
		}));
	}

	it("maps history entries to sorted sparkline points", () => {
		const points = buildSparklinePoints(makeHistory([10, 20, 30]));
		expect(points).toHaveLength(3);
		expect(points[0].percent).toBe(10);
		expect(points[2].percent).toBe(30);
	});

	it("renders a non-empty SVG path when multiple points are present", () => {
		const points = buildSparklinePoints(makeHistory([0, 50, 100]));
		const path = sparklineSvgPath(points);
		expect(path.startsWith("M")).toBe(true);
		expect(path.split("L")).toHaveLength(3);
	});

	it("returns empty string for empty history and flat line for a single point", () => {
		expect(sparklineSvgPath([])).toBe("");
		expect(sparklineSvgPath(buildSparklinePoints(makeHistory([50])))).toContain("M 0 50");
	});
});
