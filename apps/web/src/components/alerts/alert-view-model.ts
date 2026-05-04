import type { AlertRecordResponse } from "@db-monitor/api-client";

export type AlertTabKey = "active" | "timeline" | "acknowledged" | "resolved";

export const ALERT_TAB_KEYS: readonly AlertTabKey[] = [
	"active",
	"timeline",
	"acknowledged",
	"resolved",
];

const ALERT_TAB_STATUS_MAP: Readonly<Record<AlertTabKey, readonly string[]>> = {
	active: ["open"],
	timeline: [],
	acknowledged: ["acknowledged"],
	resolved: ["resolved"],
};

const SLA_BREACH_MINUTES = 30;
const MINUTE_MS = 60_000;

export interface AlertCounts {
	readonly active: number;
	readonly acknowledged: number;
	readonly resolved: number;
	readonly total: number;
	readonly critical: number;
	readonly unacknowledged: number;
	readonly slaBreach: number;
}

export function toAlertTabKey(value: string | undefined): AlertTabKey {
	return ALERT_TAB_KEYS.includes(value as AlertTabKey) ? (value as AlertTabKey) : "active";
}

export function filterAlertsByTab(
	alerts: readonly AlertRecordResponse[],
	tab: AlertTabKey,
): readonly AlertRecordResponse[] {
	const statuses = ALERT_TAB_STATUS_MAP[tab];
	if (statuses.length === 0) {
		return alerts;
	}
	const allowed = new Set(statuses);
	return alerts.filter((alert) => allowed.has(alert.status));
}

export function computeAlertCounts(alerts: readonly AlertRecordResponse[]): AlertCounts {
	const now = Date.now();
	let active = 0;
	let acknowledged = 0;
	let resolved = 0;
	let critical = 0;
	let unacknowledged = 0;
	let slaBreach = 0;
	for (const alert of alerts) {
		if (alert.status === "open") {
			active += 1;
			unacknowledged += 1;
		} else if (alert.status === "acknowledged") {
			acknowledged += 1;
		} else if (alert.status === "resolved") {
			resolved += 1;
		}
		if (alert.severity === "critical") {
			critical += 1;
		}
		if (alert.status === "open" && isSlaBreached(alert.opened_at, now)) {
			slaBreach += 1;
		}
	}
	return {
		acknowledged,
		active,
		critical,
		resolved,
		slaBreach,
		total: alerts.length,
		unacknowledged,
	};
}

function isSlaBreached(openedAt: string, now: number): boolean {
	const opened = new Date(openedAt).getTime();
	if (Number.isNaN(opened)) {
		return false;
	}
	return now - opened >= SLA_BREACH_MINUTES * MINUTE_MS;
}

export function formatEngineLabel(engine: AlertRecordResponse["engine"]): string {
	return engine === "oracle" ? "Oracle" : "MySQL";
}

export type AlertSeverityTone = "critical" | "warning" | "info" | "ok";

export function toSeverityTone(severity: string): AlertSeverityTone {
	if (severity === "critical" || severity === "warning" || severity === "info") {
		return severity;
	}
	return "ok";
}

export function selectRelatedAlerts(
	alerts: readonly AlertRecordResponse[],
	target: AlertRecordResponse,
	limit = 5,
): readonly AlertRecordResponse[] {
	return alerts
		.filter(
			(candidate) =>
				candidate.alert_id !== target.alert_id && candidate.instance_id === target.instance_id,
		)
		.slice(0, limit);
}
