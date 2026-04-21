import { describe, expect, it } from "vitest";

import { buildOperationsModel } from "../src/monitoring-ui";

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
});
