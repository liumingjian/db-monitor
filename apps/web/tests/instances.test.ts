import { describe, expect, it } from "vitest";

import { PREVIEW_ORACLE_INSTANCE, PREVIEW_ORACLE_INSTANCE_TREND } from "../src/monitoring-preview";
import {
	buildInstanceCapabilityBoundary,
	buildInstanceListFilterValues,
	buildInstancesFlowModel,
	supportsInstanceAnalytics,
} from "../src/monitoring-ui";

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
		expect(model.filters).toEqual({
			environment: "",
			label: "",
			name: "",
			status: "",
		});
		expect(model.tableColumns.map((column) => column.key)).toEqual([
			"name",
			"environment",
			"status",
		]);
		expect(model.selectedInstance.instance_id).toBe("inst-prod-primary");
		expect(
			model.trend?.cards.some((card) => card.metric_name === "mysql_transactions_per_second"),
		).toBe(true);
		expect(model.detailReadouts).toEqual([
			{ title: "Validation status", value: "passed" },
			{ title: "Server role", value: "primary" },
			{ title: "Server version", value: "8.4.0" },
		]);
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

	it("exposes oracle trends with mixed-engine fleet parity on the overview", () => {
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
		expect(model.detailReadouts).toEqual([
			{ title: "Validation status", value: "passed" },
			{ title: "Server role", value: "primary" },
			{ title: "Server version", value: "19.21.0.0.0" },
		]);
		expect(supportsInstanceAnalytics(model.selectedInstance)).toBe(true);
		expect(buildInstanceCapabilityBoundary(model.selectedInstance)).toEqual({
			detail:
				"Oracle instances now expose mixed-engine fleet cards, charts, and signal leaders on the overview while retaining engine-specific trend analytics, preset windows, and capacity readouts on the detail page.",
			label: "Capability boundary",
			value: "Fleet + detail analytics",
		});
	});

	it("normalizes instance filter defaults and overrides", () => {
		expect(buildInstanceListFilterValues()).toEqual({
			environment: "",
			label: "",
			name: "",
			status: "",
		});
		expect(
			buildInstanceListFilterValues({
				environment: " prod ",
				label: " primary ",
				name: " analytics ",
				status: "failed",
			}),
		).toEqual({
			environment: "prod",
			label: "primary",
			name: "analytics",
			status: "failed",
		});
	});
});
