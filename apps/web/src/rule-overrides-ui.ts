import type {
	AlertRuleResponse,
	RuleOverrideRequest,
	RuleOverrideResponse,
	UpdateAlertRuleRequest,
} from "@db-monitor/api-client";

export type EnabledTriState = "inherit" | "on" | "off";

export const ENABLED_TRI_STATES: readonly EnabledTriState[] = [
	"inherit",
	"on",
	"off",
] as const;

export const ENABLED_TRI_STATE_LABELS: Readonly<Record<EnabledTriState, string>> = {
	inherit: "继承默认",
	off: "关闭",
	on: "开启",
};

export interface OverrideDraftRow {
	readonly clientId: string;
	readonly enabled: EnabledTriState;
	readonly instanceId: string;
	readonly threshold: string;
}

export function toEnabledTriState(value: boolean | null | undefined): EnabledTriState {
	if (value === true) {
		return "on";
	}
	if (value === false) {
		return "off";
	}
	return "inherit";
}

export function fromEnabledTriState(value: EnabledTriState): boolean | null {
	if (value === "on") {
		return true;
	}
	if (value === "off") {
		return false;
	}
	return null;
}

export function parseThresholdInput(raw: string): number | null {
	const trimmed = raw.trim();
	if (trimmed.length === 0) {
		return null;
	}
	const parsed = Number.parseFloat(trimmed);
	if (!Number.isFinite(parsed)) {
		throw new OverrideValidationError(`threshold 输入无法解析为数值：${raw}`);
	}
	return parsed;
}

export function parseEnabledTriState(raw: string): EnabledTriState {
	if (ENABLED_TRI_STATES.includes(raw as EnabledTriState)) {
		return raw as EnabledTriState;
	}
	throw new OverrideValidationError(`enabled 三态取值非法：${raw}`);
}

export class OverrideValidationError extends Error {
	constructor(message: string) {
		super(message);
		this.name = "OverrideValidationError";
	}
}

export function toDraftRows(
	overrides: readonly RuleOverrideResponse[],
): OverrideDraftRow[] {
	return overrides.map((override, index) => ({
		clientId: `existing-${override.instance_id}-${index}`,
		enabled: toEnabledTriState(override.enabled),
		instanceId: override.instance_id,
		threshold: override.threshold === null ? "" : String(override.threshold),
	}));
}

export function buildEmptyDraftRow(clientId: string): OverrideDraftRow {
	return {
		clientId,
		enabled: "inherit",
		instanceId: "",
		threshold: "",
	};
}

export function toOverrideRequest(row: OverrideDraftRow): RuleOverrideRequest {
	if (row.instanceId.length === 0) {
		throw new OverrideValidationError("override 行缺少 instance_id");
	}
	return {
		enabled: fromEnabledTriState(row.enabled),
		instance_id: row.instanceId,
		threshold: parseThresholdInput(row.threshold),
	};
}

export function toOverrideRequests(
	rows: readonly OverrideDraftRow[],
): readonly RuleOverrideRequest[] {
	ensureNoDuplicateInstances(rows);
	return rows.map(toOverrideRequest);
}

function ensureNoDuplicateInstances(rows: readonly OverrideDraftRow[]): void {
	const seen = new Set<string>();
	for (const row of rows) {
		if (row.instanceId.length === 0) {
			continue;
		}
		if (seen.has(row.instanceId)) {
			throw new OverrideValidationError(
				`同一实例重复配置 override：${row.instanceId}`,
			);
		}
		seen.add(row.instanceId);
	}
}

export function buildUpdateRulePayload(input: {
	readonly rule: AlertRuleResponse;
	readonly rows: readonly OverrideDraftRow[];
}): UpdateAlertRuleRequest {
	const { rule, rows } = input;
	return {
		enabled: rule.enabled,
		engine: rule.engine,
		instance_ids: rule.instance_ids,
		metric_name: rule.metric_name,
		name: rule.name,
		operator: rule.operator as UpdateAlertRuleRequest["operator"],
		overrides: toOverrideRequests(rows),
		severity: rule.severity as UpdateAlertRuleRequest["severity"],
		threshold: rule.threshold,
	};
}
