import type { NotifyHistoryResponse } from "@db-monitor/api-client";
import type { SeverityTone } from "@db-monitor/ui";

/**
 * Map a notifier delivery status to the ADR-0012 four-color severity axis.
 * Source of truth for tone mapping; UI must not invent other tones.
 */
export function toStatusTone(status: string): SeverityTone {
	const normalized = status.toLowerCase();
	if (normalized === "delivered") {
		return "ok";
	}
	if (normalized === "failed") {
		return "critical";
	}
	if (normalized === "pending" || normalized === "queued") {
		return "info";
	}
	// skipped / muted / unknown fall back to muted info tone.
	return "info";
}

/**
 * i18n key suffix for a delivery status. Unknown statuses fall back to "unknown".
 */
export function toStatusKey(status: string): string {
	const normalized = status.toLowerCase();
	if (
		normalized === "delivered" ||
		normalized === "failed" ||
		normalized === "skipped" ||
		normalized === "pending"
	) {
		return normalized;
	}
	return "unknown";
}

export interface NotifyRowKey {
	readonly ruleId: string;
	readonly channel: string;
	readonly attempt: number;
	readonly attemptedAt: string;
}

export function buildRowKey(entry: NotifyHistoryResponse): string {
	return `${entry.rule_id}|${entry.channel}|${entry.attempt}|${entry.attempted_at}`;
}

export function matchesRow(entry: NotifyHistoryResponse, key: string): boolean {
	return buildRowKey(entry) === key;
}

/**
 * Apply client-side filters the API cannot yet express (instance_id, limit client-cap).
 * Server-side filters channel/status/rule_id are already applied upstream.
 */
export function applyClientFilters(
	entries: readonly NotifyHistoryResponse[],
	filters: {
		readonly instanceId: string;
	},
): readonly NotifyHistoryResponse[] {
	if (filters.instanceId.length === 0) {
		return entries;
	}
	return entries.filter((entry) => entry.instance_id === filters.instanceId);
}

/**
 * Derive attempts timeline for the currently-viewed row by aggregating rows that
 * share rule_id + channel. Sorted ascending by attempted_at so the timeline reads
 * oldest → newest.
 */
export function deriveAttemptsTimeline(
	entries: readonly NotifyHistoryResponse[],
	focus: NotifyHistoryResponse,
): readonly NotifyHistoryResponse[] {
	const matches = entries.filter(
		(entry) => entry.rule_id === focus.rule_id && entry.channel === focus.channel,
	);
	return [...matches].sort((left, right) => left.attempted_at.localeCompare(right.attempted_at));
}

export interface ChannelSummaryRow {
	readonly channel: string;
	readonly totalAttempts: number;
	readonly delivered: number;
	readonly failed: number;
	readonly skipped: number;
	readonly lastAttemptedAt: string | null;
	readonly lastStatus: string | null;
}

export interface ChannelSummary {
	readonly rows: readonly ChannelSummaryRow[];
	readonly activeCount: number;
	readonly healthyCount: number;
	readonly degradedCount: number;
}

/**
 * Aggregate /admin/notify-history snapshot into per-channel status summary for
 * the read-only Channels page. Never mutates input.
 */
export function summarizeChannels(entries: readonly NotifyHistoryResponse[]): ChannelSummary {
	const byChannel = new Map<
		string,
		{
			totalAttempts: number;
			delivered: number;
			failed: number;
			skipped: number;
			lastAttemptedAt: string | null;
			lastStatus: string | null;
		}
	>();

	for (const entry of entries) {
		const bucket = byChannel.get(entry.channel) ?? {
			delivered: 0,
			failed: 0,
			lastAttemptedAt: null,
			lastStatus: null,
			skipped: 0,
			totalAttempts: 0,
		};
		bucket.totalAttempts += 1;
		const status = entry.status.toLowerCase();
		if (status === "delivered") {
			bucket.delivered += 1;
		} else if (status === "failed") {
			bucket.failed += 1;
		} else if (status === "skipped") {
			bucket.skipped += 1;
		}
		if (bucket.lastAttemptedAt === null || entry.attempted_at > bucket.lastAttemptedAt) {
			bucket.lastAttemptedAt = entry.attempted_at;
			bucket.lastStatus = entry.status;
		}
		byChannel.set(entry.channel, bucket);
	}

	const rows: ChannelSummaryRow[] = Array.from(byChannel.entries())
		.map(([channel, bucket]) => ({
			channel,
			delivered: bucket.delivered,
			failed: bucket.failed,
			lastAttemptedAt: bucket.lastAttemptedAt,
			lastStatus: bucket.lastStatus,
			skipped: bucket.skipped,
			totalAttempts: bucket.totalAttempts,
		}))
		.sort((left, right) => left.channel.localeCompare(right.channel));

	const healthyCount = rows.filter((row) => row.failed === 0 && row.delivered > 0).length;
	const degradedCount = rows.filter((row) => row.failed > 0).length;
	const activeCount = rows.filter((row) => row.totalAttempts > 0).length;

	return {
		activeCount,
		degradedCount,
		healthyCount,
		rows,
	};
}

export function toChannelHealthTone(row: ChannelSummaryRow): SeverityTone {
	if (row.totalAttempts === 0 || (row.delivered === 0 && row.failed === 0)) {
		return "info";
	}
	if (row.failed === 0) {
		return "ok";
	}
	if (row.delivered > 0) {
		return "warning";
	}
	return "critical";
}

export function toChannelHealthKey(row: ChannelSummaryRow): string {
	if (row.totalAttempts === 0 || (row.delivered === 0 && row.failed === 0)) {
		return "idle";
	}
	if (row.failed === 0) {
		return "healthy";
	}
	if (row.delivered > 0) {
		return "degraded";
	}
	return "down";
}

export type { NotifyHistoryResponse };
