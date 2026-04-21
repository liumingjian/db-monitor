import { describe, expect, it } from "vitest";

import { DEFAULT_TIME_WINDOW, parseTimeWindow } from "../src/server-api";

describe("analytics time window parsing", () => {
	it("accepts approved windows", () => {
		expect(parseTimeWindow("15m")).toBe("15m");
		expect(parseTimeWindow("1h")).toBe("1h");
		expect(parseTimeWindow("6h")).toBe("6h");
		expect(parseTimeWindow("24h")).toBe("24h");
	});

	it("falls back to the default window for unsupported values", () => {
		expect(parseTimeWindow(undefined)).toBe(DEFAULT_TIME_WINDOW);
		expect(parseTimeWindow("7d")).toBe(DEFAULT_TIME_WINDOW);
	});
});
