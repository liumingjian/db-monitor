import { describe, expect, it } from "vitest";

import { ON_CALL_AUTO_OFF_MS, computeOnCallRemaining } from "../src/components/shell/on-call-math";

describe("computeOnCallRemaining", () => {
	it("returns null minutes when disabled", () => {
		const r = computeOnCallRemaining(false, 0, 0);
		expect(r.expired).toBe(false);
		expect(r.remainingMinutes).toBeNull();
	});

	it("returns null minutes when enabledAt is null", () => {
		const r = computeOnCallRemaining(true, null, 0);
		expect(r.remainingMinutes).toBeNull();
	});

	it("reports full window just after enabling", () => {
		const now = 1_000_000;
		const r = computeOnCallRemaining(true, now, now);
		expect(r.expired).toBe(false);
		expect(r.remainingMinutes).toBe(120);
		expect(r.remainingMs).toBe(ON_CALL_AUTO_OFF_MS);
	});

	it("counts down by minutes as time passes", () => {
		const start = 1_000_000;
		const later = start + 30 * 60_000; // 30 min
		const r = computeOnCallRemaining(true, start, later);
		expect(r.expired).toBe(false);
		expect(r.remainingMinutes).toBe(90);
	});

	it("expires exactly at 2h boundary", () => {
		const start = 5_000_000;
		const r = computeOnCallRemaining(true, start, start + ON_CALL_AUTO_OFF_MS);
		expect(r.expired).toBe(true);
		expect(r.remainingMinutes).toBe(0);
	});

	it("stays expired beyond 2h", () => {
		const start = 5_000_000;
		const r = computeOnCallRemaining(true, start, start + ON_CALL_AUTO_OFF_MS + 60_000);
		expect(r.expired).toBe(true);
	});

	it("respects custom autoOffMs window", () => {
		const start = 0;
		const r = computeOnCallRemaining(true, start, 30_000, 60_000);
		expect(r.expired).toBe(false);
		expect(r.remainingMinutes).toBe(1);
	});
});
