import { describe, expect, it } from "vitest";

import type { AlertRuleResponse, RuleOverrideResponse } from "@db-monitor/api-client";

import {
	OverrideValidationError,
	buildEmptyDraftRow,
	buildUpdateRulePayload,
	fromEnabledTriState,
	parseEnabledTriState,
	parseThresholdInput,
	toDraftRows,
	toEnabledTriState,
	toOverrideRequests,
} from "../src/rule-overrides-ui";

const BASE_RULE: AlertRuleResponse = {
	created_at: "2026-04-22T00:00:00+00:00",
	enabled: true,
	engine: "mysql",
	instance_ids: ["inst-a", "inst-b"],
	metric_name: "mysql_threads_connected",
	name: "Connections High",
	operator: "gte",
	overrides: [],
	rule_id: "rule-123",
	severity: "warning",
	threshold: 900,
};

describe("three-state enabled toggle mapping", () => {
	it("maps backend boolean|null to the tri-state enum", () => {
		expect(toEnabledTriState(true)).toBe("on");
		expect(toEnabledTriState(false)).toBe("off");
		expect(toEnabledTriState(null)).toBe("inherit");
		expect(toEnabledTriState(undefined)).toBe("inherit");
	});

	it("maps the tri-state enum back to boolean|null for payload", () => {
		expect(fromEnabledTriState("on")).toBe(true);
		expect(fromEnabledTriState("off")).toBe(false);
		expect(fromEnabledTriState("inherit")).toBeNull();
	});

	it("parses user tri-state form input and rejects garbage", () => {
		expect(parseEnabledTriState("on")).toBe("on");
		expect(parseEnabledTriState("off")).toBe("off");
		expect(parseEnabledTriState("inherit")).toBe("inherit");
		expect(() => parseEnabledTriState("weird")).toThrow(OverrideValidationError);
	});
});

describe("threshold input parsing", () => {
	it("returns null for empty input (inherit default threshold)", () => {
		expect(parseThresholdInput("")).toBeNull();
		expect(parseThresholdInput("   ")).toBeNull();
	});

	it("parses numeric strings", () => {
		expect(parseThresholdInput("900")).toBe(900);
		expect(parseThresholdInput(" 12.5 ")).toBe(12.5);
	});

	it("throws validation error on non-numeric", () => {
		expect(() => parseThresholdInput("abc")).toThrow(OverrideValidationError);
	});
});

describe("draft row hydration", () => {
	it("hydrates existing overrides into draft rows", () => {
		const overrides: readonly RuleOverrideResponse[] = [
			{
				enabled: false,
				instance_id: "inst-a",
				threshold: null,
				updated_at: "2026-04-22T00:00:00+00:00",
			},
			{
				enabled: null,
				instance_id: "inst-b",
				threshold: 950,
				updated_at: "2026-04-22T00:00:00+00:00",
			},
		];
		const rows = toDraftRows(overrides);
		expect(rows[0]).toMatchObject({ enabled: "off", instanceId: "inst-a", threshold: "" });
		expect(rows[1]).toMatchObject({ enabled: "inherit", instanceId: "inst-b", threshold: "950" });
	});

	it("builds an empty draft row for the + Add override button", () => {
		expect(buildEmptyDraftRow("abc")).toEqual({
			clientId: "abc",
			enabled: "inherit",
			instanceId: "",
			threshold: "",
		});
	});
});

describe("payload shape", () => {
	it("serializes rows into the replacement override payload", () => {
		const payload = buildUpdateRulePayload({
			rows: [
				{ clientId: "c1", enabled: "off", instanceId: "inst-a", threshold: "" },
				{ clientId: "c2", enabled: "on", instanceId: "inst-b", threshold: "950" },
				{ clientId: "c3", enabled: "inherit", instanceId: "inst-c", threshold: "120.5" },
			],
			rule: BASE_RULE,
		});
		expect(payload.overrides).toEqual([
			{ enabled: false, instance_id: "inst-a", threshold: null },
			{ enabled: true, instance_id: "inst-b", threshold: 950 },
			{ enabled: null, instance_id: "inst-c", threshold: 120.5 },
		]);
		expect(payload.name).toBe(BASE_RULE.name);
		expect(payload.threshold).toBe(BASE_RULE.threshold);
		expect(payload.engine).toBe(BASE_RULE.engine);
	});

	it("emits an empty overrides array when the user removed all rows", () => {
		const payload = buildUpdateRulePayload({ rows: [], rule: BASE_RULE });
		expect(payload.overrides).toEqual([]);
	});

	it("rejects duplicate instance_id entries", () => {
		expect(() =>
			toOverrideRequests([
				{ clientId: "c1", enabled: "on", instanceId: "inst-a", threshold: "900" },
				{ clientId: "c2", enabled: "off", instanceId: "inst-a", threshold: "" },
			]),
		).toThrow(OverrideValidationError);
	});

	it("rejects rows that do not select an instance", () => {
		expect(() =>
			toOverrideRequests([{ clientId: "c1", enabled: "inherit", instanceId: "", threshold: "" }]),
		).toThrow(OverrideValidationError);
	});
});
