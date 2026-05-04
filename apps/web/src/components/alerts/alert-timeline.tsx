import type { AlertRecordResponse } from "@db-monitor/api-client";
import { Badge, formatRelativeTime } from "@db-monitor/ui";
import Link from "next/link";

import { formatEngineLabel, toSeverityTone } from "./alert-view-model";

interface AlertTimelineProps {
	readonly alerts: readonly AlertRecordResponse[];
	readonly buildDrawerHref: (alertId: string) => string;
}

interface TimelineEntry {
	readonly alertId: string;
	readonly at: string;
	readonly detail: string;
	readonly event: "opened" | "acknowledged" | "resolved";
	readonly severity: AlertRecordResponse["severity"];
	readonly rule: string;
	readonly instanceId: string;
	readonly engine: AlertRecordResponse["engine"];
}

export function AlertTimeline({ alerts, buildDrawerHref }: AlertTimelineProps) {
	const entries = buildTimelineEntries(alerts);
	if (entries.length === 0) {
		return (
			<div className="rounded-md border border-dashed border-border-hairline bg-bg-elevated p-6 text-sm text-fg-muted">
				暂无告警事件流
			</div>
		);
	}
	return (
		<ol className="relative flex flex-col gap-3 border-l border-border-hairline pl-4">
			{entries.map((entry) => (
				<li className="relative" key={`${entry.alertId}-${entry.event}-${entry.at}`}>
					<span
						aria-hidden
						className="absolute -left-[21px] top-3 inline-block h-2 w-2 rounded-full bg-accent"
					/>
					<Link
						className="flex flex-col gap-1 rounded-md border border-border-hairline bg-bg-elevated p-3 transition-colors hover:border-accent/60"
						href={buildDrawerHref(entry.alertId)}
					>
						<div className="flex flex-wrap items-center gap-2">
							<EventBadge event={entry.event} />
							<Badge
								size="sm"
								variant={
									toSeverityTone(entry.severity) === "critical"
										? "destructive"
										: toSeverityTone(entry.severity) === "warning"
											? "warning"
											: "info"
								}
							>
								{toSeverityText(entry.severity)}
							</Badge>
							<span className="text-[11px] uppercase tracking-wider text-fg-muted">
								{formatEngineLabel(entry.engine)}
							</span>
							<span className="font-mono text-[11px] text-fg-muted tabular-nums">
								{formatRelativeTime(entry.at)}
							</span>
						</div>
						<p className="text-sm font-medium text-fg-primary">{entry.rule}</p>
						<p className="font-mono text-xs text-fg-muted">
							{entry.instanceId} · {entry.detail}
						</p>
					</Link>
				</li>
			))}
		</ol>
	);
}

function buildTimelineEntries(alerts: readonly AlertRecordResponse[]): readonly TimelineEntry[] {
	const entries: TimelineEntry[] = [];
	for (const alert of alerts) {
		entries.push({
			alertId: alert.alert_id,
			at: alert.opened_at,
			detail: `${alert.metric_name} · 当前值 ${alert.current_value} · 阈值 ${alert.threshold}`,
			engine: alert.engine,
			event: "opened",
			instanceId: alert.instance_id,
			rule: alert.rule_name,
			severity: alert.severity,
		});
		if (alert.acknowledged_at !== null) {
			entries.push({
				alertId: alert.alert_id,
				at: alert.acknowledged_at,
				detail: `已确认 · ${alert.acknowledged_by_user_id ?? "未记录负责人"}`,
				engine: alert.engine,
				event: "acknowledged",
				instanceId: alert.instance_id,
				rule: alert.rule_name,
				severity: alert.severity,
			});
		}
		if (alert.resolved_at !== null) {
			entries.push({
				alertId: alert.alert_id,
				at: alert.resolved_at,
				detail: "告警已解决",
				engine: alert.engine,
				event: "resolved",
				instanceId: alert.instance_id,
				rule: alert.rule_name,
				severity: alert.severity,
			});
		}
	}
	return entries.sort((a, b) => new Date(b.at).getTime() - new Date(a.at).getTime());
}

function EventBadge({ event }: { readonly event: TimelineEntry["event"] }) {
	if (event === "acknowledged") {
		return (
			<Badge size="sm" variant="info">
				已确认
			</Badge>
		);
	}
	if (event === "resolved") {
		return (
			<Badge size="sm" variant="ok">
				已解决
			</Badge>
		);
	}
	return (
		<Badge size="sm" variant="destructive">
			告警触发
		</Badge>
	);
}

function toSeverityText(severity: string): string {
	if (severity === "critical") {
		return "紧急";
	}
	if (severity === "warning") {
		return "警告";
	}
	if (severity === "info") {
		return "提示";
	}
	return "健康";
}
