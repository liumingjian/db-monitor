import { describe, expect, it } from "vitest";

import type {
	InstanceResponse,
	ProcesslistEntryResponse,
	ProcesslistSnapshotResponse,
} from "@db-monitor/api-client";

import { PREVIEW_INSTANCE } from "../src/monitoring-preview";
import {
	EMPTY_PROCESSLIST_FILTERS,
	KILL_BLOCK_MONITOR_USER_MESSAGE,
	KILL_BLOCK_VALIDATION_MESSAGE,
	KILL_ERROR_FALLBACK,
	KILL_PERMISSION,
	PROCESSLIST_MAX_LIMIT,
	buildProcesslistFilterValues,
	buildProcesslistViewModel,
	hasKillPermission,
	mapKillStatusToCode,
	resolveKillRowState,
	toProcesslistApiFilters,
} from "../src/processlist-ui";

const SAMPLE_ENTRY: ProcesslistEntryResponse = {
	command: "Query",
	db: "mysql",
	host: "10.0.0.12:34512",
	info: "SELECT 1",
	process_id: 42,
	state: "executing",
	time_seconds: 12,
	trx_started_at: null,
	user: "root",
};

function buildSnapshot(
	entries: readonly ProcesslistEntryResponse[],
	snapshotAt: string | null,
): ProcesslistSnapshotResponse {
	return { entries, snapshot_at: snapshotAt };
}

function buildInstance(status: string): InstanceResponse {
	return {
		...PREVIEW_INSTANCE,
		validation: { ...PREVIEW_INSTANCE.validation, status },
	};
}

describe("processlist filter normalization", () => {
	it("defaults every filter to empty string", () => {
		expect(buildProcesslistFilterValues()).toEqual(EMPTY_PROCESSLIST_FILTERS);
	});

	it("trims whitespace around inputs", () => {
		expect(
			buildProcesslistFilterValues({
				command: " Query ",
				host: " 10.0.0.1 ",
				user: " root ",
			}),
		).toEqual({
			...EMPTY_PROCESSLIST_FILTERS,
			command: "Query",
			host: "10.0.0.1",
			user: "root",
		});
	});

	it("converts text filters into typed api filters and clamps limit", () => {
		const filters = buildProcesslistFilterValues({
			host: " 10.0.0.2 ",
			limit: "99999",
			minTimeSeconds: "10",
			user: "root",
		});
		expect(toProcesslistApiFilters(filters)).toEqual({
			collected_after: undefined,
			collected_before: undefined,
			command: undefined,
			host: "10.0.0.2",
			limit: PROCESSLIST_MAX_LIMIT,
			min_time_seconds: 10,
			user: "root",
		});
	});

	it("drops empty and invalid numeric values instead of coercing to zero", () => {
		const filters = buildProcesslistFilterValues({
			limit: "not-a-number",
			minTimeSeconds: "",
		});
		expect(toProcesslistApiFilters(filters)).toEqual({
			collected_after: undefined,
			collected_before: undefined,
			command: undefined,
			host: undefined,
			limit: undefined,
			min_time_seconds: undefined,
			user: undefined,
		});
	});
});

describe("processlist view model empty state", () => {
	it("flags validation failure before considering snapshot", () => {
		const model = buildProcesslistViewModel(
			buildInstance("failed"),
			buildSnapshot([SAMPLE_ENTRY], "2026-04-22T10:00:00+00:00"),
			EMPTY_PROCESSLIST_FILTERS,
		);
		expect(model.validationPassed).toBe(false);
		expect(model.emptyState?.reason).toBe("validation");
		expect(model.emptyState?.title).toBe("实例校验未通过");
	});

	it("surfaces 尚未采集 when snapshot has never been produced", () => {
		const model = buildProcesslistViewModel(
			buildInstance("passed"),
			buildSnapshot([], null),
			EMPTY_PROCESSLIST_FILTERS,
		);
		expect(model.emptyState?.reason).toBe("no-snapshot");
		expect(model.emptyState?.title).toBe("尚未采集");
	});

	it("surfaces 无匹配结果 when snapshot exists but filters exclude everything", () => {
		const model = buildProcesslistViewModel(
			buildInstance("passed"),
			buildSnapshot([], "2026-04-22T10:00:00+00:00"),
			buildProcesslistFilterValues({ user: "root" }),
		);
		expect(model.emptyState?.reason).toBe("no-match");
		expect(model.emptyState?.title).toBe("当前快照无匹配结果");
	});

	it("returns null empty state when entries are present", () => {
		const model = buildProcesslistViewModel(
			buildInstance("passed"),
			buildSnapshot([SAMPLE_ENTRY], "2026-04-22T10:00:00+00:00"),
			EMPTY_PROCESSLIST_FILTERS,
		);
		expect(model.emptyState).toBeNull();
		expect(model.entries).toHaveLength(1);
		expect(model.snapshotLabel).toBe("2026-04-22T10:00:00+00:00");
	});
});

describe("kill row safety net", () => {
	it("disables with validation message when validation has not passed", () => {
		expect(
			resolveKillRowState({
				entryUser: "app",
				monitorUsername: "db_monitor",
				validationPassed: false,
			}),
		).toEqual({ disabled: true, reason: KILL_BLOCK_VALIDATION_MESSAGE });
	});

	it("disables monitor-user target with dedicated tooltip", () => {
		expect(
			resolveKillRowState({
				entryUser: "db_monitor",
				monitorUsername: "db_monitor",
				validationPassed: true,
			}),
		).toEqual({ disabled: true, reason: KILL_BLOCK_MONITOR_USER_MESSAGE });
	});

	it("enables Kill when validation passed and target differs from monitor user", () => {
		expect(
			resolveKillRowState({
				entryUser: "app",
				monitorUsername: "db_monitor",
				validationPassed: true,
			}),
		).toEqual({ disabled: false, reason: null });
	});

	it("prefers validation failure over monitor-user match", () => {
		expect(
			resolveKillRowState({
				entryUser: "db_monitor",
				monitorUsername: "db_monitor",
				validationPassed: false,
			}).reason,
		).toBe(KILL_BLOCK_VALIDATION_MESSAGE);
	});
});

describe("kill permission gating", () => {
	it("flags instances:action holders as able to kill", () => {
		expect(hasKillPermission([KILL_PERMISSION, "instances:read"])).toBe(true);
	});

	it("hides Kill when permission is absent", () => {
		expect(hasKillPermission(["instances:read"])).toBe(false);
		expect(hasKillPermission([])).toBe(false);
	});
});

describe("kill error code mapping", () => {
	it("maps every documented HTTP status to the expected UX code", () => {
		expect(mapKillStatusToCode(401)).toBe("unauthorized");
		expect(mapKillStatusToCode(403)).toBe("forbidden");
		expect(mapKillStatusToCode(404)).toBe("not_found");
		expect(mapKillStatusToCode(409)).toBe("blocked");
		expect(mapKillStatusToCode(502)).toBe("driver_failure");
	});

	it("falls back to unknown for unmapped status codes", () => {
		expect(mapKillStatusToCode(500)).toBe("unknown");
		expect(mapKillStatusToCode(418)).toBe("unknown");
	});

	it("ships human-readable Chinese fallback for every error code", () => {
		expect(KILL_ERROR_FALLBACK.blocked).toContain("安全网");
		expect(KILL_ERROR_FALLBACK.unauthorized).toContain("会话");
		expect(KILL_ERROR_FALLBACK.forbidden).toContain("instances:action");
		expect(KILL_ERROR_FALLBACK.driver_failure).toContain("驱动");
		expect(KILL_ERROR_FALLBACK.not_found).toContain("实例");
		expect(KILL_ERROR_FALLBACK.invalid_input).toContain("原因");
		expect(KILL_ERROR_FALLBACK.unknown).toContain("未知");
	});
});
