import { describe, expect, it } from "vitest";

import type {
	InstanceResponse,
	SlowQueryEntryResponse,
	SlowQuerySnapshotResponse,
} from "@db-monitor/api-client";

import { PREVIEW_INSTANCE } from "../src/monitoring-preview";
import {
	EMPTY_SLOW_QUERY_FILTERS,
	PS_DISABLED_HINT_MESSAGE,
	SLOW_QUERY_MAX_LIMIT,
	buildSlowQueryFilterValues,
	buildSlowQueryViewModel,
	detectPsHint,
	toSlowQueryApiFilters,
} from "../src/slow-queries-ui";

const SAMPLE_ENTRY: SlowQueryEntryResponse = {
	digest: "abc123def",
	errors: 0,
	event_id: 1024,
	rows_affected: 0,
	rows_examined: 500,
	rows_sent: 10,
	schema_name: "ordering",
	sql_text: "SELECT * FROM orders WHERE user_id = 42",
	started_at: "2026-04-22T10:00:00+00:00",
	timer_wait_ms: 2500,
	user: "app",
};

function buildSnapshot(
	entries: readonly SlowQueryEntryResponse[],
): SlowQuerySnapshotResponse {
	return {
		entries,
		window: {
			from_at: "2026-04-22T09:45:00+00:00",
			to_at: "2026-04-22T10:00:00+00:00",
		},
	};
}

function buildInstance(
	status: string,
	detail = "ok",
): InstanceResponse {
	return {
		...PREVIEW_INSTANCE,
		validation: { ...PREVIEW_INSTANCE.validation, detail, status },
	};
}

describe("slow query filter normalization", () => {
	it("defaults every filter to empty string", () => {
		expect(buildSlowQueryFilterValues()).toEqual(EMPTY_SLOW_QUERY_FILTERS);
	});

	it("trims whitespace around inputs", () => {
		expect(
			buildSlowQueryFilterValues({
				digestPrefix: " abc ",
				minDurationMs: " 1000 ",
				schema: " ordering ",
				user: " app ",
			}),
		).toEqual({
			...EMPTY_SLOW_QUERY_FILTERS,
			digestPrefix: "abc",
			minDurationMs: "1000",
			schema: "ordering",
			user: "app",
		});
	});

	it("converts filters into typed api filters and clamps limit", () => {
		const filters = buildSlowQueryFilterValues({
			digestPrefix: "abc",
			limit: "99999",
			minDurationMs: "1500",
			schema: "ordering",
			startedAfter: "2026-04-22T09:00:00Z",
			startedBefore: "2026-04-22T10:00:00Z",
			user: "app",
		});
		expect(toSlowQueryApiFilters(filters)).toEqual({
			digest_prefix: "abc",
			limit: SLOW_QUERY_MAX_LIMIT,
			min_duration_ms: 1500,
			schema: "ordering",
			started_after: "2026-04-22T09:00:00Z",
			started_before: "2026-04-22T10:00:00Z",
			user: "app",
		});
	});

	it("drops empty and invalid numeric values instead of coercing to zero", () => {
		const filters = buildSlowQueryFilterValues({
			limit: "not-a-number",
			minDurationMs: "",
		});
		expect(toSlowQueryApiFilters(filters)).toEqual({
			digest_prefix: undefined,
			limit: undefined,
			min_duration_ms: undefined,
			schema: undefined,
			started_after: undefined,
			started_before: undefined,
			user: undefined,
		});
	});
});

describe("slow query view model empty state", () => {
	it("flags validation failure before considering snapshot", () => {
		const model = buildSlowQueryViewModel(
			buildInstance("failed"),
			buildSnapshot([SAMPLE_ENTRY]),
			EMPTY_SLOW_QUERY_FILTERS,
		);
		expect(model.validationPassed).toBe(false);
		expect(model.emptyState?.reason).toBe("validation");
		expect(model.emptyState?.title).toBe("实例校验未通过");
	});

	it("surfaces performance_schema 未启用 when validation detail hints PS disabled", () => {
		const model = buildSlowQueryViewModel(
			buildInstance(
				"passed",
				"连接校验通过；performance_schema=ON 未启用，请开启后重试。",
			),
			buildSnapshot([]),
			EMPTY_SLOW_QUERY_FILTERS,
		);
		expect(model.psHint).toBe(PS_DISABLED_HINT_MESSAGE);
		expect(model.emptyState?.reason).toBe("ps-disabled");
		expect(model.emptyState?.title).toBe("Performance Schema 未启用");
	});

	it("surfaces 窗口内无慢查询 when snapshot empty and no filters applied", () => {
		const model = buildSlowQueryViewModel(
			buildInstance("passed"),
			buildSnapshot([]),
			EMPTY_SLOW_QUERY_FILTERS,
		);
		expect(model.emptyState?.reason).toBe("no-data");
		expect(model.emptyState?.title).toBe("窗口内无慢查询");
	});

	it("surfaces 无匹配结果 when filters active but snapshot empty", () => {
		const model = buildSlowQueryViewModel(
			buildInstance("passed"),
			buildSnapshot([]),
			buildSlowQueryFilterValues({ user: "app" }),
		);
		expect(model.emptyState?.reason).toBe("no-match");
		expect(model.emptyState?.title).toBe("当前窗口无匹配结果");
	});

	it("returns null empty state when entries are present", () => {
		const model = buildSlowQueryViewModel(
			buildInstance("passed"),
			buildSnapshot([SAMPLE_ENTRY]),
			EMPTY_SLOW_QUERY_FILTERS,
		);
		expect(model.emptyState).toBeNull();
		expect(model.entries).toHaveLength(1);
		expect(model.window.fromAt).toBe("2026-04-22T09:45:00+00:00");
		expect(model.window.toAt).toBe("2026-04-22T10:00:00+00:00");
	});
});

describe("performance schema hint detection", () => {
	it("returns canonical Chinese hint when detail mentions performance_schema=ON", () => {
		expect(
			detectPsHint(
				buildInstance("passed", "连接校验通过；performance_schema=ON 未启用。"),
			),
		).toBe(PS_DISABLED_HINT_MESSAGE);
	});

	it("passes through history_long_size hint verbatim", () => {
		const detail =
			"连接校验通过；events_statements_history_long_size=1024 低于建议阈值 10000。";
		expect(detectPsHint(buildInstance("passed", detail))).toBe(detail);
	});

	it("passes through performance_schema 探测失败 detail verbatim", () => {
		const detail =
			"连接校验通过；performance_schema 探测失败：MySQLError(...)";
		expect(detectPsHint(buildInstance("passed", detail))).toBe(detail);
	});

	it("returns null when detail has no PS hint", () => {
		expect(detectPsHint(buildInstance("passed", "ok"))).toBeNull();
	});
});
