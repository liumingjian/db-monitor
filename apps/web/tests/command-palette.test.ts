import { describe, expect, it } from "vitest";

import { fuzzyScore, rankItems } from "@db-monitor/ui";

describe("fuzzyScore", () => {
	it("returns 0 indexes for empty query", () => {
		const result = fuzzyScore("anything", "");
		expect(result?.indexes).toEqual([]);
		expect(result?.score).toBe(0);
	});

	it("returns null when haystack does not contain all chars", () => {
		expect(fuzzyScore("instance", "xyz")).toBeNull();
	});

	it("boosts exact match to the highest bracket", () => {
		const exact = fuzzyScore("overview", "overview");
		const sub = fuzzyScore("overview", "over");
		expect(exact).not.toBeNull();
		expect(sub).not.toBeNull();
		expect((exact as { score: number }).score).toBeGreaterThan((sub as { score: number }).score);
	});

	it("prefers prefix over scattered subsequence", () => {
		const prefix = fuzzyScore("instances-prod", "inst");
		const scattered = fuzzyScore("inbound-custom-test", "inst");
		expect(prefix).not.toBeNull();
		expect(scattered).not.toBeNull();
		expect((prefix as { score: number }).score).toBeGreaterThan(
			(scattered as { score: number }).score,
		);
	});

	it("is case insensitive", () => {
		expect(fuzzyScore("Overview", "OVER")).not.toBeNull();
		expect(fuzzyScore("Overview", "over")).not.toBeNull();
	});

	it("supports multi-token queries requiring each token to match", () => {
		const both = fuzzyScore("prod-mysql-primary", "prod primary");
		expect(both).not.toBeNull();
		const missing = fuzzyScore("prod-mysql-primary", "prod zzz");
		expect(missing).toBeNull();
	});
});

describe("rankItems", () => {
	const items = [
		{ id: "a", searchText: "overview" },
		{ id: "b", searchText: "instances" },
		{ id: "c", searchText: "prod-primary mysql" },
		{ id: "d", searchText: "rules alerts" },
	];

	it("returns all items on empty query in original order", () => {
		const ranked = rankItems(items, "  ");
		expect(ranked.map((r) => r.item.id)).toEqual(["a", "b", "c", "d"]);
	});

	it("ranks more relevant items first", () => {
		const ranked = rankItems(items, "inst");
		expect(ranked[0]?.item.id).toBe("b");
	});

	it("drops non-matching items", () => {
		const ranked = rankItems(items, "oracle");
		expect(ranked).toHaveLength(0);
	});

	it("ranks multi-token match across fields", () => {
		const ranked = rankItems(items, "prod mysql");
		expect(ranked[0]?.item.id).toBe("c");
	});
});
