import { describe, expect, it } from "vitest";

import { buildSmokeRouteSet } from "../src/monitoring-ui";

describe("smoke flow", () => {
	it("covers the approved phase-one route set", () => {
		expect(buildSmokeRouteSet()).toEqual([
			"/login",
			"/overview",
			"/instances",
			"/instances/inst-prod-primary",
			"/instances/inst-prod-primary/processes",
			"/alerts",
			"/alerts/alert-lag",
			"/rules",
			"/settings",
		]);
	});
});
