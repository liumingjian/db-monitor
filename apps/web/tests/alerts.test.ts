import { describe, expect, it } from "vitest";

import { buildAlertListFilterValues, buildOperationsModel } from "../src/monitoring-ui";

describe("alerts rules and settings flows", () => {
	it("exposes alert detail, rule management, and settings sections", () => {
		const model = buildOperationsModel();

		expect(model.alertColumns.map((column) => column.key)).toEqual([
			"rule_name",
			"status",
			"instance_id",
		]);
		expect(model.alertDetail.record.alert_id).toBe("alert-lag");
		expect(model.alertDetail.record.engine).toBe("mysql");
		expect(model.alertDetail.record.owner_user_id).toBe("user-ops");
		expect(model.alertDetail.record.acknowledged_by_user_id).toBe("user-ops");
		expect(model.alertFilters).toEqual({
			instance: "",
			opened_after: "",
			opened_before: "",
			severity: "",
			status: "",
		});
		expect(model.alertDetail.history.at(-1)?.event_type).toBe("note_added");
		expect(model.ruleCatalog.map((catalog) => catalog.engine)).toEqual(["mysql", "oracle"]);
		expect(model.ruleColumns.map((column) => column.key)).toEqual([
			"name",
			"metric_name",
			"severity",
		]);
		expect(model.ruleFormValues.engine).toBe("mysql");
		expect(model.ruleFields.map((field) => field.name)).toEqual([
			"name",
			"metric_name",
			"threshold",
			"instance_ids",
		]);
		expect(model.settingFields[0].name).toBe("notification.channel");
	});

	it("normalizes alert filter defaults and overrides", () => {
		expect(buildAlertListFilterValues()).toEqual({
			instance: "",
			opened_after: "",
			opened_before: "",
			severity: "",
			status: "",
		});
		expect(
			buildAlertListFilterValues({
				instance: " replica ",
				opened_after: "2026-04-21T08:00",
				opened_before: "2026-04-21T10:00",
				severity: "warning",
				status: "acknowledged",
			}),
		).toEqual({
			instance: "replica",
			opened_after: "2026-04-21T08:00",
			opened_before: "2026-04-21T10:00",
			severity: "warning",
			status: "acknowledged",
		});
	});
});
