import { describe, expect, it } from "vitest";

import { API_CONTRACT_VERSION } from "@db-monitor/api-client";

import { createWebDataLayer } from "../src/data-layer";

describe("data-layer contract", () => {
	it("binds typed client, query keys, and shared primitives once", () => {
		const layer = createWebDataLayer({
			baseUrl: "http://127.0.0.1:8000",
			fetchImpl: async () => ({
				json: async () => ({}),
				ok: true,
				status: 200,
				text: async () => "",
			}),
		});

		expect(layer.contractVersion).toBe(API_CONTRACT_VERSION);
		expect(layer.queryKeys.authSession()).toEqual(["auth", "session"]);
		expect(layer.queryKeys.overview("1h")).toEqual(["analytics", "overview", "1h"]);
		expect(layer.queryKeys.instanceTrends("inst-1", "1h")).toEqual([
			"analytics",
			"instance-trends",
			"inst-1",
			"1h",
		]);
		expect(layer.tableColumns.map((column) => column.key)).toEqual([
			"rule_name",
			"status",
			"instance_id",
		]);
	});
});
