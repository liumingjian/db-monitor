import type { AlertRecordResponse, NotifyHistoryResponse } from "@db-monitor/api-client";

export type InstanceAuditEventKind = "alert" | "notify";

export interface InstanceAuditEvent {
	readonly id: string;
	readonly kind: InstanceAuditEventKind;
	readonly occurredAt: string;
	readonly title: string;
	readonly detail: string;
	readonly status: string;
	readonly severity: "critical" | "warning" | "info" | "ok";
}

export interface BuildInstanceAuditFeedInput {
	readonly alerts: readonly AlertRecordResponse[];
	readonly notifyHistory: readonly NotifyHistoryResponse[];
	readonly instanceId: string;
}

/**
 * Q13 审计 tab：合成两类事件（alerts + notify history）做时间线。
 * 后端当前无 instance-scoped audit 端点，本函数仅做前端按 instance_id
 * 过滤并按 `occurredAt` 倒排，等同 Settings+Audit page (#8) 的合成模式。
 */
export function buildInstanceAuditFeed(
	input: BuildInstanceAuditFeedInput,
): readonly InstanceAuditEvent[] {
	const alertEvents = input.alerts
		.filter((alert) => alert.instance_id === input.instanceId)
		.map(toAlertEvent);
	const notifyEvents = input.notifyHistory
		.filter((entry) => entry.instance_id === input.instanceId)
		.map(toNotifyEvent);
	return [...alertEvents, ...notifyEvents].sort((a, b) =>
		a.occurredAt < b.occurredAt ? 1 : a.occurredAt > b.occurredAt ? -1 : 0,
	);
}

function toAlertEvent(alert: AlertRecordResponse): InstanceAuditEvent {
	return {
		detail: `rule=${alert.rule_name} · metric=${alert.metric_name} · value=${alert.current_value} (阈 ${alert.threshold})`,
		id: `alert:${alert.alert_id}`,
		kind: "alert",
		occurredAt: alert.last_evaluated_at,
		severity: normaliseSeverity(alert.severity, alert.status),
		status: alert.status,
		title: alert.rule_name,
	};
}

function toNotifyEvent(entry: NotifyHistoryResponse): InstanceAuditEvent {
	const delivered = entry.delivered_at !== null;
	return {
		detail: `channel=${entry.channel} · rule=${entry.rule_id} · attempt=${entry.attempt}${
			entry.error !== null ? ` · error=${entry.error}` : ""
		}`,
		id: `notify:${entry.rule_id}:${entry.attempted_at}:${entry.attempt}`,
		kind: "notify",
		occurredAt: entry.attempted_at,
		severity: delivered ? "ok" : entry.error !== null ? "critical" : "warning",
		status: entry.status,
		title: `通知发送 · ${entry.channel}`,
	};
}

function normaliseSeverity(severity: string, status: string): InstanceAuditEvent["severity"] {
	if (status === "resolved") {
		return "ok";
	}
	if (severity === "critical") {
		return "critical";
	}
	if (severity === "warning") {
		return "warning";
	}
	return "info";
}
