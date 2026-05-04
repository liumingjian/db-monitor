import type {
	InstanceResponse,
	ListSlowQueriesFilters,
	SlowQueryEntryResponse,
	SlowQuerySnapshotResponse,
} from "@db-monitor/api-client";

export const SLOW_QUERY_DEFAULT_LIMIT = 50;
export const SLOW_QUERY_MAX_LIMIT = 200;

export const PS_DISABLED_HINT_MESSAGE =
	"Performance Schema events_statements_history_long 未启用，请在被监控实例设置 performance_schema=ON 并确保 events_statements_history_long_size >= 10000";

export type SlowQueryEmptyReason = "validation" | "ps-disabled" | "no-data" | "no-match" | null;

export interface SlowQueryFilterValues {
	readonly minDurationMs: string;
	readonly user: string;
	readonly schema: string;
	readonly digestPrefix: string;
	readonly startedAfter: string;
	readonly startedBefore: string;
	readonly limit: string;
}

export interface SlowQueryEmptyState {
	readonly reason: SlowQueryEmptyReason;
	readonly title: string;
	readonly detail: string;
}

export interface SlowQueryViewModel {
	readonly emptyState: SlowQueryEmptyState | null;
	readonly entries: readonly SlowQueryEntryResponse[];
	readonly filters: SlowQueryFilterValues;
	readonly psHint: string | null;
	readonly validationPassed: boolean;
	readonly window: { readonly fromAt: string; readonly toAt: string };
}

export const EMPTY_SLOW_QUERY_FILTERS: SlowQueryFilterValues = {
	digestPrefix: "",
	limit: "",
	minDurationMs: "",
	schema: "",
	startedAfter: "",
	startedBefore: "",
	user: "",
};

export function buildSlowQueryFilterValues(
	input: Partial<Record<keyof SlowQueryFilterValues, string | undefined>> = {},
): SlowQueryFilterValues {
	return {
		digestPrefix: (input.digestPrefix ?? "").trim(),
		limit: (input.limit ?? "").trim(),
		minDurationMs: (input.minDurationMs ?? "").trim(),
		schema: (input.schema ?? "").trim(),
		startedAfter: (input.startedAfter ?? "").trim(),
		startedBefore: (input.startedBefore ?? "").trim(),
		user: (input.user ?? "").trim(),
	};
}

export function toSlowQueryApiFilters(filters: SlowQueryFilterValues): ListSlowQueriesFilters {
	const minDuration = parsePositiveNumber(filters.minDurationMs);
	const limit = parsePositiveInt(filters.limit);
	return {
		digest_prefix: nonEmpty(filters.digestPrefix),
		limit: limit === undefined ? undefined : clampLimit(limit),
		min_duration_ms: minDuration,
		schema: nonEmpty(filters.schema),
		started_after: nonEmpty(filters.startedAfter),
		started_before: nonEmpty(filters.startedBefore),
		user: nonEmpty(filters.user),
	};
}

export function detectPsHint(instance: InstanceResponse): string | null {
	const detail = instance.validation.detail ?? "";
	if (detail.includes("performance_schema=ON")) {
		return PS_DISABLED_HINT_MESSAGE;
	}
	if (detail.includes("events_statements_history_long_size")) {
		return detail;
	}
	if (detail.includes("performance_schema 探测失败")) {
		return detail;
	}
	return null;
}

export function buildSlowQueryViewModel(
	instance: InstanceResponse,
	snapshot: SlowQuerySnapshotResponse,
	filters: SlowQueryFilterValues,
): SlowQueryViewModel {
	const validationPassed = instance.validation.status === "passed";
	const psHint = detectPsHint(instance);
	const emptyState = resolveEmptyState({
		entries: snapshot.entries,
		filters,
		psHint,
		validationPassed,
	});
	return {
		emptyState,
		entries: snapshot.entries,
		filters,
		psHint,
		validationPassed,
		window: { fromAt: snapshot.window.from_at, toAt: snapshot.window.to_at },
	};
}

interface EmptyStateInput {
	readonly entries: readonly SlowQueryEntryResponse[];
	readonly filters: SlowQueryFilterValues;
	readonly psHint: string | null;
	readonly validationPassed: boolean;
}

function resolveEmptyState(input: EmptyStateInput): SlowQueryEmptyState | null {
	if (!input.validationPassed) {
		return {
			detail: "请先完成实例连接校验，慢查询仅对校验通过的实例开放。",
			reason: "validation",
			title: "实例校验未通过",
		};
	}
	if (input.psHint?.includes("performance_schema=ON")) {
		return {
			detail: PS_DISABLED_HINT_MESSAGE,
			reason: "ps-disabled",
			title: "Performance Schema 未启用",
		};
	}
	if (input.entries.length > 0) {
		return null;
	}
	if (hasActiveFilter(input.filters)) {
		return {
			detail: "当前筛选条件下未命中任何慢查询，可放宽时间窗或降低阈值。",
			reason: "no-match",
			title: "当前窗口无匹配结果",
		};
	}
	return {
		detail: "最近 15 分钟内没有满足阈值的慢查询。",
		reason: "no-data",
		title: "窗口内无慢查询",
	};
}

function hasActiveFilter(filters: SlowQueryFilterValues): boolean {
	return (
		filters.minDurationMs.length > 0 ||
		filters.user.length > 0 ||
		filters.schema.length > 0 ||
		filters.digestPrefix.length > 0 ||
		filters.startedAfter.length > 0 ||
		filters.startedBefore.length > 0
	);
}

function nonEmpty(value: string): string | undefined {
	const trimmed = value.trim();
	return trimmed.length === 0 ? undefined : trimmed;
}

function parsePositiveInt(value: string): number | undefined {
	const trimmed = value.trim();
	if (trimmed.length === 0) {
		return undefined;
	}
	const parsed = Number.parseInt(trimmed, 10);
	if (Number.isNaN(parsed) || parsed < 0) {
		return undefined;
	}
	return parsed;
}

function parsePositiveNumber(value: string): number | undefined {
	const trimmed = value.trim();
	if (trimmed.length === 0) {
		return undefined;
	}
	const parsed = Number.parseFloat(trimmed);
	if (Number.isNaN(parsed) || parsed < 0) {
		return undefined;
	}
	return parsed;
}

function clampLimit(limit: number): number {
	if (limit < 1) {
		return 1;
	}
	if (limit > SLOW_QUERY_MAX_LIMIT) {
		return SLOW_QUERY_MAX_LIMIT;
	}
	return limit;
}
