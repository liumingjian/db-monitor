import type {
	AlertRecordResponse,
	ManagedUserResponse,
	NotifyHistoryResponse,
	SystemSettingResponse,
} from "@db-monitor/api-client";

export type AuditEventType =
	| "alert.opened"
	| "alert.acknowledged"
	| "alert.owner_assigned"
	| "alert.resolved"
	| "setting.updated"
	| "notify.delivered"
	| "notify.failed"
	| "notify.skipped";

export type AuditSeverity = "critical" | "warning" | "info" | "ok";

export interface AuditActor {
	readonly userId: string | null;
	readonly displayName: string | null;
	readonly username: string | null;
	readonly roles: readonly string[];
	readonly isSystem: boolean;
}

export interface AuditTarget {
	readonly type: "alert" | "setting" | "notify";
	readonly id: string;
	readonly label: string;
}

export interface AuditDiff {
	readonly before: Readonly<Record<string, string | number | null>>;
	readonly after: Readonly<Record<string, string | number | null>>;
}

export interface AuditMetadata {
	readonly engine?: string;
	readonly severity?: AuditSeverity;
	readonly status?: string;
	readonly channel?: string;
	readonly attempt?: number;
	readonly settingKey?: string;
}

export interface AuditEvent {
	readonly id: string;
	readonly occurredAt: string;
	readonly type: AuditEventType;
	readonly severity: AuditSeverity;
	readonly actor: AuditActor;
	readonly target: AuditTarget;
	readonly diff: AuditDiff | null;
	readonly metadata: AuditMetadata;
}

const SYSTEM_ACTOR: AuditActor = {
	userId: null,
	displayName: null,
	username: null,
	roles: [],
	isSystem: true,
};

export interface BuildAuditFeedOptions {
	readonly alerts: readonly AlertRecordResponse[];
	readonly settings: readonly SystemSettingResponse[];
	readonly notifyHistory: readonly NotifyHistoryResponse[];
	readonly users: readonly ManagedUserResponse[];
	readonly limit: number;
}

export function buildAuditFeed(options: BuildAuditFeedOptions): readonly AuditEvent[] {
	const { alerts, settings, notifyHistory, users, limit } = options;
	const userById = new Map(users.map((user) => [user.user_id, user] as const));

	const events: AuditEvent[] = [
		...alertsToEvents(alerts, userById),
		...settingsToEvents(settings),
		...notifyToEvents(notifyHistory),
	];

	events.sort((left, right) => right.occurredAt.localeCompare(left.occurredAt));
	return events.slice(0, limit);
}

function alertsToEvents(
	alerts: readonly AlertRecordResponse[],
	userById: Map<string, ManagedUserResponse>,
): readonly AuditEvent[] {
	const result: AuditEvent[] = [];
	for (const alert of alerts) {
		result.push(buildAlertOpenedEvent(alert));
		if (alert.acknowledged_at) {
			result.push(
				buildAlertAckEvent(alert, userById.get(alert.acknowledged_by_user_id ?? "") ?? null),
			);
		}
		if (alert.owner_user_id && alert.owner_assigned_at) {
			result.push(buildAlertOwnerEvent(alert, userById.get(alert.owner_user_id) ?? null));
		}
		if (alert.resolved_at) {
			result.push(buildAlertResolvedEvent(alert));
		}
	}
	return result;
}

function buildAlertOpenedEvent(alert: AlertRecordResponse): AuditEvent {
	return {
		id: `alert-opened:${alert.alert_id}`,
		occurredAt: alert.opened_at,
		type: "alert.opened",
		severity: toSeverity(alert.severity),
		actor: SYSTEM_ACTOR,
		target: {
			type: "alert",
			id: alert.alert_id,
			label: alert.rule_name,
		},
		diff: {
			before: { status: "—", current_value: null },
			after: {
				status: "open",
				current_value: alert.current_value,
				threshold: alert.threshold,
			},
		},
		metadata: {
			engine: alert.engine,
			severity: toSeverity(alert.severity),
			status: alert.status,
		},
	};
}

function buildAlertAckEvent(
	alert: AlertRecordResponse,
	actor: ManagedUserResponse | null,
): AuditEvent {
	return {
		id: `alert-ack:${alert.alert_id}`,
		occurredAt: alert.acknowledged_at ?? alert.opened_at,
		type: "alert.acknowledged",
		severity: toSeverity(alert.severity),
		actor: toActor(actor),
		target: {
			type: "alert",
			id: alert.alert_id,
			label: alert.rule_name,
		},
		diff: {
			before: { status: "open" },
			after: { status: "acknowledged" },
		},
		metadata: {
			engine: alert.engine,
			severity: toSeverity(alert.severity),
			status: "acknowledged",
		},
	};
}

function buildAlertOwnerEvent(
	alert: AlertRecordResponse,
	actor: ManagedUserResponse | null,
): AuditEvent {
	return {
		id: `alert-owner:${alert.alert_id}`,
		occurredAt: alert.owner_assigned_at ?? alert.opened_at,
		type: "alert.owner_assigned",
		severity: toSeverity(alert.severity),
		actor: toActor(actor),
		target: {
			type: "alert",
			id: alert.alert_id,
			label: alert.rule_name,
		},
		diff: {
			before: { owner_user_id: null },
			after: { owner_user_id: alert.owner_user_id ?? null },
		},
		metadata: {
			engine: alert.engine,
			severity: toSeverity(alert.severity),
			status: alert.status,
		},
	};
}

function buildAlertResolvedEvent(alert: AlertRecordResponse): AuditEvent {
	return {
		id: `alert-resolved:${alert.alert_id}`,
		occurredAt: alert.resolved_at ?? alert.opened_at,
		type: "alert.resolved",
		severity: "ok",
		actor: SYSTEM_ACTOR,
		target: {
			type: "alert",
			id: alert.alert_id,
			label: alert.rule_name,
		},
		diff: {
			before: { status: alert.acknowledged_at ? "acknowledged" : "open" },
			after: { status: "resolved" },
		},
		metadata: {
			engine: alert.engine,
			severity: toSeverity(alert.severity),
			status: "resolved",
		},
	};
}

function settingsToEvents(settings: readonly SystemSettingResponse[]): readonly AuditEvent[] {
	return settings.map((setting) => ({
		id: `setting:${setting.key}:${setting.updated_at}`,
		occurredAt: setting.updated_at,
		type: "setting.updated" as const,
		severity: "info" as const,
		actor: SYSTEM_ACTOR,
		target: {
			type: "setting" as const,
			id: setting.key,
			label: setting.key,
		},
		diff: {
			before: { value: "—" },
			after: { value: setting.value },
		},
		metadata: {
			settingKey: setting.key,
		},
	}));
}

function notifyToEvents(notifyHistory: readonly NotifyHistoryResponse[]): readonly AuditEvent[] {
	return notifyHistory.map((entry) => {
		const type: AuditEventType =
			entry.status === "delivered"
				? "notify.delivered"
				: entry.status === "failed"
					? "notify.failed"
					: "notify.skipped";
		const severity: AuditSeverity =
			entry.status === "failed" ? "critical" : entry.status === "skipped" ? "warning" : "ok";
		return {
			id: `notify:${entry.rule_id}:${entry.channel}:${entry.attempt}:${entry.attempted_at}`,
			occurredAt: entry.attempted_at,
			type,
			severity,
			actor: SYSTEM_ACTOR,
			target: {
				type: "notify" as const,
				id: `${entry.rule_id}:${entry.channel}:${entry.attempt}`,
				label: `${entry.channel} · rule ${entry.rule_id}`,
			},
			diff: {
				before: { status: "pending" },
				after: {
					status: entry.status,
					delivered_at: entry.delivered_at,
					error: entry.error,
				},
			},
			metadata: {
				channel: entry.channel,
				attempt: entry.attempt,
				status: entry.status,
				severity,
			},
		};
	});
}

function toActor(user: ManagedUserResponse | null): AuditActor {
	if (user === null) {
		return SYSTEM_ACTOR;
	}
	return {
		userId: user.user_id,
		displayName: user.display_name,
		username: user.username,
		roles: user.roles,
		isSystem: false,
	};
}

function toSeverity(value: string): AuditSeverity {
	if (value === "critical") {
		return "critical";
	}
	if (value === "warning") {
		return "warning";
	}
	if (value === "ok" || value === "healthy" || value === "resolved") {
		return "ok";
	}
	return "info";
}
