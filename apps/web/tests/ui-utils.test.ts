import {
	formatBytes,
	formatDuration,
	formatNumber,
	formatPercent,
	formatRelativeTime,
	formatValue,
} from "@db-monitor/ui";
import { describe, expect, it } from "vitest";

describe("formatNumber", () => {
	it("adds thousand separators for large integers", () => {
		expect(formatNumber(12_345_678)).toBe("12,345,678");
	});

	it("respects fixed decimals", () => {
		expect(formatNumber(Math.PI, { decimals: 2 })).toBe("3.14");
	});

	it("handles very large numbers without scientific notation", () => {
		expect(formatNumber(1_234_567_890_123)).toBe("1,234,567,890,123");
	});

	it("returns em-dash for NaN", () => {
		expect(formatNumber(Number.NaN)).toBe("—");
	});
});

describe("formatPercent", () => {
	it("formats fractional values to one decimal", () => {
		expect(formatPercent(0.853)).toBe("85.3%");
	});

	it("keeps 0 as 0.0%", () => {
		expect(formatPercent(0)).toBe("0.0%");
	});

	it("falls back for NaN", () => {
		expect(formatPercent(Number.NaN)).toBe("—");
	});

	it("falls back for null and undefined", () => {
		expect(formatPercent(null)).toBe("—");
		expect(formatPercent(undefined)).toBe("—");
	});

	it("respects custom decimals", () => {
		expect(formatPercent(0.12345, { decimals: 3 })).toBe("12.345%");
	});
});

describe("formatBytes", () => {
	it("renders 0 bytes", () => {
		expect(formatBytes(0)).toBe("0 B");
	});

	it("uses SI (base10) by default for GB", () => {
		expect(formatBytes(1_200_000_000)).toBe("1.2 GB");
	});

	it("scales KB/MB/TB under SI", () => {
		expect(formatBytes(2_500)).toBe("2.5 KB");
		expect(formatBytes(5_000_000)).toBe("5.0 MB");
		expect(formatBytes(3_000_000_000_000)).toBe("3.0 TB");
	});

	it("supports IEC base2 units", () => {
		expect(formatBytes(1_073_741_824, { base: 2 })).toBe("1.0 GiB");
	});

	it("prefixes negatives with -", () => {
		expect(formatBytes(-2_000_000)).toBe("-2.0 MB");
	});
});

describe("formatDuration", () => {
	it("renders sub-second as ms", () => {
		expect(formatDuration(12.3)).toBe("12.3 ms");
	});

	it("renders seconds", () => {
		expect(formatDuration(2_400)).toBe("2.4 s");
	});

	it("renders minutes", () => {
		expect(formatDuration(180_000)).toBe("3 min");
	});

	it("renders hours and minutes", () => {
		expect(formatDuration(3_660_000)).toBe("1h 1m");
	});

	it("renders days and hours", () => {
		expect(formatDuration(86_400_000)).toBe("1d 0h");
	});

	it("falls back for negatives", () => {
		expect(formatDuration(-100)).toBe("—");
	});
});

describe("formatRelativeTime", () => {
	const now = new Date("2026-04-22T12:00:00Z");

	it("returns 刚刚 within the last minute", () => {
		const target = new Date(now.getTime() - 10_000);
		expect(formatRelativeTime(target, now)).toBe("刚刚");
	});

	it("returns 分钟前 within the hour", () => {
		const target = new Date(now.getTime() - 3 * 60_000);
		expect(formatRelativeTime(target, now)).toBe("3 分钟前");
	});

	it("returns 小时前 within the day", () => {
		const target = new Date(now.getTime() - 2 * 60 * 60_000);
		expect(formatRelativeTime(target, now)).toBe("2 小时前");
	});

	it("switches to absolute timestamp at or beyond 24h", () => {
		const target = new Date("2026-04-20T14:32:18Z");
		// Uses local timezone getters; just assert shape/length and separators.
		const result = formatRelativeTime(target, now);
		expect(result).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/);
	});

	it("handles future timestamps with 再过", () => {
		const target = new Date(now.getTime() + 5 * 60_000);
		expect(formatRelativeTime(target, now)).toBe("再过 5 分钟");
	});

	it("falls back for null / undefined / invalid", () => {
		expect(formatRelativeTime(null, now)).toBe("—");
		expect(formatRelativeTime(undefined, now)).toBe("—");
		expect(formatRelativeTime("not-a-date", now)).toBe("—");
	});
});

describe("formatValue", () => {
	it("keeps 0 as '0' (distinct from fallback)", () => {
		expect(formatValue(0)).toBe("0");
	});

	it("falls back for null", () => {
		expect(formatValue(null)).toBe("—");
	});

	it("falls back for undefined", () => {
		expect(formatValue(undefined)).toBe("—");
	});

	it("falls back for NaN", () => {
		expect(formatValue(Number.NaN)).toBe("—");
	});

	it("serialises normal numbers", () => {
		expect(formatValue(42)).toBe("42");
	});

	it("honors custom fallback", () => {
		expect(formatValue(null, "n/a")).toBe("n/a");
	});
});
