import type {
	TablespaceEntryResponse,
	TablespaceHistoryEntryResponse,
	TablespaceSnapshotResponse,
} from "@db-monitor/api-client";

export const USED_RATE_WARNING_THRESHOLD = 85;
export const USED_RATE_CRITICAL_THRESHOLD = 95;
export const HISTORY_ALERT_LINE_PERCENT = USED_RATE_CRITICAL_THRESHOLD;
export const DEFAULT_HISTORY_DAYS = 30;

export type UsedRateBand = "normal" | "warning" | "critical";

export interface TablespaceRow {
	readonly tablespace_name: string;
	readonly status: string;
	readonly used_bytes: number;
	readonly total_bytes: number;
	readonly used_rate_percent: number;
	readonly autoextensible: boolean;
	readonly band: UsedRateBand;
}

export interface TablespaceViewModel {
	readonly rows: readonly TablespaceRow[];
	readonly snapshotLabel: string;
	readonly hasSnapshot: boolean;
}

export function classifyUsedRate(percent: number): UsedRateBand {
	if (percent >= USED_RATE_CRITICAL_THRESHOLD) {
		return "critical";
	}
	if (percent >= USED_RATE_WARNING_THRESHOLD) {
		return "warning";
	}
	return "normal";
}

export function buildTablespaceViewModel(
	snapshot: TablespaceSnapshotResponse,
): TablespaceViewModel {
	const sortedEntries = [...snapshot.entries].sort(
		(a, b) => b.used_rate_percent - a.used_rate_percent,
	);
	const rows = sortedEntries.map(toRow);
	return {
		rows,
		snapshotLabel: snapshot.snapshot_at ?? "尚无快照",
		hasSnapshot: snapshot.snapshot_at !== null,
	};
}

function toRow(entry: TablespaceEntryResponse): TablespaceRow {
	return {
		...entry,
		band: classifyUsedRate(entry.used_rate_percent),
	};
}

export function formatBytes(value: number): string {
	if (value < 1024) {
		return `${value} B`;
	}
	const units = ["KB", "MB", "GB", "TB", "PB"];
	let amount = value / 1024;
	let unitIndex = 0;
	while (amount >= 1024 && unitIndex < units.length - 1) {
		amount = amount / 1024;
		unitIndex += 1;
	}
	return `${amount.toFixed(2)} ${units[unitIndex]}`;
}

export function formatPercent(value: number): string {
	return `${value.toFixed(1)}%`;
}

export interface SparklinePoint {
	readonly timestamp: number;
	readonly percent: number;
}

export function buildSparklinePoints(
	history: readonly TablespaceHistoryEntryResponse[],
): readonly SparklinePoint[] {
	return history.map((entry) => ({
		percent: entry.used_rate_percent,
		timestamp: Date.parse(entry.collected_at),
	}));
}

export function sparklineSvgPath(points: readonly SparklinePoint[]): string {
	if (points.length === 0) {
		return "";
	}
	if (points.length === 1) {
		return `M 0 50 L 100 50`;
	}
	const firstTs = points[0].timestamp;
	const lastTs = points[points.length - 1].timestamp;
	const tsSpan = lastTs - firstTs || 1;
	const mapped = points.map((point) => {
		const x = ((point.timestamp - firstTs) / tsSpan) * 100;
		const y = 100 - Math.min(100, Math.max(0, point.percent));
		return { x, y };
	});
	const head = mapped[0];
	const tail = mapped
		.slice(1)
		.map((item) => `L ${item.x.toFixed(2)} ${item.y.toFixed(2)}`)
		.join(" ");
	return `M ${head.x.toFixed(2)} ${head.y.toFixed(2)} ${tail}`;
}

export function bandLabel(band: UsedRateBand): string {
	if (band === "critical") {
		return "危险";
	}
	if (band === "warning") {
		return "预警";
	}
	return "正常";
}

export function bandToneClassName(band: UsedRateBand): string {
	if (band === "critical") {
		return "bg-red-500";
	}
	if (band === "warning") {
		return "bg-amber-400";
	}
	return "bg-emerald-400";
}
