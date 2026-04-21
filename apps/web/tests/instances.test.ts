import { describe, expect, it } from "vitest";

import {
	buildInstanceCapabilityBoundary,
	buildInstancesFlowModel,
	supportsInstanceAnalytics,
} from "../src/monitoring-ui";
import {
	PREVIEW_ORACLE_INSTANCE,
	PREVIEW_ORACLE_INSTANCE_TREND,
} from "../src/monitoring-preview";

describe("instances flow", () => {
	it("exposes onboarding fields plus list and detail data", () => {
		const model = buildInstancesFlowModel();

		expect(model.formFields.map((field) => field.name)).toEqual([
			"name",
			"environment",
			"database",
			"host",
			"port",
			"username",
			"password",
			"labels",
		]);
		expect(model.formValues.engine).toBe("mysql");
		expect(model.tableColumns.map((column) => column.key)).toEqual([
			"name",
			"environment",
			"status",
		]);
		expect(model.selectedInstance.instance_id).toBe("inst-prod-primary");
		expect(model.detailSeries).toContain("mysql_queries_per_second");
		expect(model.detailSeries).toContain("mysql_bytes_sent_per_second");
		expect(model.detailSeries).toContain("mysql_innodb_buffer_pool_reads_per_second");
		expect(model.capacityReadout.map((insight) => insight.title)).toEqual([
			"Workload direction",
			"Engine pressure",
			"Concurrency posture",
		]);
		expect(model.capacityReadout.map((insight) => insight.value)).toEqual([
			"Serving-heavy",
			"Risk visible",
			"Pooled headroom",
		]);
	});

	it("exposes minimal oracle trends without pretending to offer full parity", () => {
		const model = buildInstancesFlowModel({
			selectedInstance: PREVIEW_ORACLE_INSTANCE,
			tableRows: [PREVIEW_ORACLE_INSTANCE],
			trend: PREVIEW_ORACLE_INSTANCE_TREND,
		});

		expect(model.trend).toEqual(PREVIEW_ORACLE_INSTANCE_TREND);
		expect(model.detailSeries).toContain("oracle_user_calls_per_second");
		expect(model.detailSeries).toContain("oracle_physical_reads_per_second");
		expect(model.capacityReadout.map((insight) => insight.title)).toEqual([
			"Workload direction",
			"Engine pressure",
			"Concurrency posture",
		]);
		expect(model.capacityReadout.map((insight) => insight.value)).toEqual([
			"Call-heavy",
			"Watch waits",
			"Pooled headroom",
		]);
		expect(supportsInstanceAnalytics(model.selectedInstance)).toBe(true);
		expect(buildInstanceCapabilityBoundary(model.selectedInstance)).toEqual({
			detail:
				"Oracle instances now expose minimal trend analytics, preset windows, and capacity readouts on the detail page, and they contribute to fleet health and engine coverage on the overview. Cards, charts, and signal leaders still follow the engines listed in overview coverage.",
			label: "Capability boundary",
			value: "Fleet health + trends available",
		});
	});
});
