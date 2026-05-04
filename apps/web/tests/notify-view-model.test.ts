import type { NotifyHistoryResponse } from "@db-monitor/api-client";
import { describe, expect, it } from "vitest";

import {
	applyClientFilters,
	buildRowKey,
	deriveAttemptsTimeline,
	summarizeChannels,
	toChannelHealthKey,
	toChannelHealthTone,
	toStatusKey,
	toStatusTone,
} from "../src/components/notify/notify-view-model";

function makeEntry(overrides: Partial<NotifyHistoryResponse> = {}): NotifyHistoryResponse {
	return {
		attempt: 1,
		attempted_at: "2026-04-23T08:00:00Z",
		channel: "feishu",
		delivered_at: null,
		error: null,
		instance_id: null,
		organization_id: "org-1",
		rule_id: "rule-1",
		status: "delivered",
		...overrides,
	};
}

describe("notify-view-model", () => {
	it("maps notifier status to the four-color severity axis", () => {
		expect(toStatusTone("delivered")).toBe("ok");
		expect(toStatusTone("failed")).toBe("critical");
		expect(toStatusTone("pending")).toBe("info");
		expect(toStatusTone("skipped")).toBe("info");
		expect(toStatusTone("WEIRD")).toBe("info");
	});

	it("canonicalizes unknown statuses to the unknown i18n key", () => {
		expect(toStatusKey("delivered")).toBe("delivered");
		expect(toStatusKey("FAILED")).toBe("failed");
		expect(toStatusKey("mystery-status")).toBe("unknown");
	});

	it("builds a deterministic row key from rule + channel + attempt + attempted_at", () => {
		const entry = makeEntry({ attempt: 3, channel: "smtp", rule_id: "rule-x" });
		expect(buildRowKey(entry)).toBe("rule-x|smtp|3|2026-04-23T08:00:00Z");
	});

	it("post-filters entries by instance_id client-side", () => {
		const entries = [
			makeEntry({ instance_id: "inst-a" }),
			makeEntry({ instance_id: "inst-b" }),
			makeEntry({ instance_id: null }),
		];
		expect(applyClientFilters(entries, { instanceId: "" })).toHaveLength(3);
		expect(applyClientFilters(entries, { instanceId: "inst-a" })).toHaveLength(1);
		expect(applyClientFilters(entries, { instanceId: "inst-missing" })).toHaveLength(0);
	});

	it("derives attempts timeline sorted by attempted_at ascending", () => {
		const focus = makeEntry({ attempt: 2, attempted_at: "2026-04-23T08:00:02Z" });
		const entries = [
			focus,
			makeEntry({ attempt: 1, attempted_at: "2026-04-23T08:00:01Z" }),
			makeEntry({ attempt: 3, attempted_at: "2026-04-23T08:00:03Z", channel: "smtp" }),
		];
		const timeline = deriveAttemptsTimeline(entries, focus);
		expect(timeline.map((entry) => entry.attempt)).toEqual([1, 2]);
	});

	it("summarizes channels with healthy / degraded classification", () => {
		const entries = [
			makeEntry({ channel: "feishu", status: "delivered" }),
			makeEntry({ channel: "feishu", status: "delivered", attempt: 2 }),
			makeEntry({ channel: "smtp", status: "failed" }),
			makeEntry({ channel: "smtp", status: "delivered", attempt: 2 }),
			makeEntry({ channel: "sms", status: "skipped" }),
		];
		const summary = summarizeChannels(entries);
		expect(summary.rows.map((row) => row.channel)).toEqual(["feishu", "sms", "smtp"]);
		expect(summary.healthyCount).toBe(1);
		expect(summary.degradedCount).toBe(1);
		expect(summary.activeCount).toBe(3);

		const feishu = summary.rows.find((row) => row.channel === "feishu");
		expect(feishu).toBeDefined();
		if (feishu) {
			expect(toChannelHealthTone(feishu)).toBe("ok");
			expect(toChannelHealthKey(feishu)).toBe("healthy");
		}

		const smtp = summary.rows.find((row) => row.channel === "smtp");
		expect(smtp).toBeDefined();
		if (smtp) {
			expect(toChannelHealthTone(smtp)).toBe("warning");
			expect(toChannelHealthKey(smtp)).toBe("degraded");
		}

		const sms = summary.rows.find((row) => row.channel === "sms");
		expect(sms).toBeDefined();
		if (sms) {
			expect(toChannelHealthTone(sms)).toBe("info");
			expect(toChannelHealthKey(sms)).toBe("idle");
		}
	});
});
