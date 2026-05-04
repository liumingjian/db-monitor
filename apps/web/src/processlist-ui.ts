import type {
	InstanceResponse,
	ListProcesslistFilters,
	ProcesslistEntryResponse,
	ProcesslistSnapshotResponse,
} from "@db-monitor/api-client";

export const PROCESSLIST_DEFAULT_LIMIT = 200;
export const PROCESSLIST_MAX_LIMIT = 500;

export const KILL_PERMISSION = "instances:action";
export const KILL_BLOCK_VALIDATION_MESSAGE = "实例校验未通过，无法 kill";
export const KILL_BLOCK_MONITOR_USER_MESSAGE = "监控用户自身连接不可 kill";

export type ProcesslistEmptyReason = "validation" | "no-snapshot" | "no-match" | null;

export interface ProcesslistFilterValues {
	readonly user: string;
	readonly host: string;
	readonly command: string;
	readonly minTimeSeconds: string;
	readonly collectedAfter: string;
	readonly collectedBefore: string;
	readonly limit: string;
}

export interface ProcesslistEmptyState {
	readonly reason: ProcesslistEmptyReason;
	readonly title: string;
	readonly detail: string;
}

export interface ProcesslistViewModel {
	readonly emptyState: ProcesslistEmptyState | null;
	readonly entries: readonly ProcesslistEntryResponse[];
	readonly filters: ProcesslistFilterValues;
	readonly snapshotAt: string | null;
	readonly snapshotLabel: string;
	readonly validationPassed: boolean;
}

export const EMPTY_PROCESSLIST_FILTERS: ProcesslistFilterValues = {
	collectedAfter: "",
	collectedBefore: "",
	command: "",
	host: "",
	limit: "",
	minTimeSeconds: "",
	user: "",
};

export function buildProcesslistFilterValues(
	input: Partial<Record<keyof ProcesslistFilterValues, string | undefined>> = {},
): ProcesslistFilterValues {
	return {
		collectedAfter: (input.collectedAfter ?? "").trim(),
		collectedBefore: (input.collectedBefore ?? "").trim(),
		command: (input.command ?? "").trim(),
		host: (input.host ?? "").trim(),
		limit: (input.limit ?? "").trim(),
		minTimeSeconds: (input.minTimeSeconds ?? "").trim(),
		user: (input.user ?? "").trim(),
	};
}

export function toProcesslistApiFilters(filters: ProcesslistFilterValues): ListProcesslistFilters {
	const minTime = parsePositiveInt(filters.minTimeSeconds);
	const limit = parsePositiveInt(filters.limit);
	return {
		collected_after: nonEmpty(filters.collectedAfter),
		collected_before: nonEmpty(filters.collectedBefore),
		command: nonEmpty(filters.command),
		host: nonEmpty(filters.host),
		limit: limit === undefined ? undefined : clampLimit(limit),
		min_time_seconds: minTime,
		user: nonEmpty(filters.user),
	};
}

export function buildProcesslistViewModel(
	instance: InstanceResponse,
	snapshot: ProcesslistSnapshotResponse,
	filters: ProcesslistFilterValues,
): ProcesslistViewModel {
	const validationPassed = instance.validation.status === "passed";
	const emptyState = resolveEmptyState({
		validationPassed,
		entries: snapshot.entries,
		snapshotAt: snapshot.snapshot_at,
	});
	return {
		emptyState,
		entries: snapshot.entries,
		filters,
		snapshotAt: snapshot.snapshot_at,
		snapshotLabel: snapshot.snapshot_at ?? "尚无快照",
		validationPassed,
	};
}

interface EmptyStateInput {
	readonly entries: readonly ProcesslistEntryResponse[];
	readonly snapshotAt: string | null;
	readonly validationPassed: boolean;
}

function resolveEmptyState(input: EmptyStateInput): ProcesslistEmptyState | null {
	if (!input.validationPassed) {
		return {
			detail: "请先完成实例连接校验，processlist 仅对校验通过的实例开放。",
			reason: "validation",
			title: "实例校验未通过",
		};
	}
	if (input.entries.length > 0) {
		return null;
	}
	if (input.snapshotAt === null) {
		return {
			detail: "采集任务尚未上报数据，稍后刷新即可看到最新会话。",
			reason: "no-snapshot",
			title: "尚未采集",
		};
	}
	return {
		detail: "最新一次快照内没有匹配当前筛选条件的会话。",
		reason: "no-match",
		title: "当前快照无匹配结果",
	};
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

export interface KillRowState {
	readonly disabled: boolean;
	readonly reason: string | null;
}

export interface KillRowInput {
	readonly entryUser: string;
	readonly monitorUsername: string;
	readonly validationPassed: boolean;
}

export function resolveKillRowState(input: KillRowInput): KillRowState {
	if (!input.validationPassed) {
		return { disabled: true, reason: KILL_BLOCK_VALIDATION_MESSAGE };
	}
	if (input.entryUser === input.monitorUsername) {
		return { disabled: true, reason: KILL_BLOCK_MONITOR_USER_MESSAGE };
	}
	return { disabled: false, reason: null };
}

export function hasKillPermission(permissions: readonly string[]): boolean {
	return permissions.includes(KILL_PERMISSION);
}

export type KillProcessErrorCode =
	| "invalid_input"
	| "unauthorized"
	| "forbidden"
	| "not_found"
	| "blocked"
	| "driver_failure"
	| "unknown";

export const KILL_ERROR_FALLBACK: Readonly<Record<KillProcessErrorCode, string>> = {
	blocked: "安全网拦截：实例校验未通过或目标是监控用户自身。",
	driver_failure: "数据库驱动调用失败，请稍后重试或查看后端日志。",
	forbidden: "当前角色无 instances:action 权限。",
	invalid_input: "请输入 kill 原因后再提交。",
	not_found: "实例不存在或无权访问。",
	unauthorized: "会话已失效，请重新登录。",
	unknown: "未知错误，请查看后端日志。",
};

export function mapKillStatusToCode(status: number): KillProcessErrorCode {
	if (status === 401) return "unauthorized";
	if (status === 403) return "forbidden";
	if (status === 404) return "not_found";
	if (status === 409) return "blocked";
	if (status === 502) return "driver_failure";
	return "unknown";
}

function clampLimit(limit: number): number {
	if (limit < 1) {
		return 1;
	}
	if (limit > PROCESSLIST_MAX_LIMIT) {
		return PROCESSLIST_MAX_LIMIT;
	}
	return limit;
}
