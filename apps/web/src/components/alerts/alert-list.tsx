import type { AlertRecordResponse } from "@db-monitor/api-client";
import { Badge, formatRelativeTime } from "@db-monitor/ui";
import Link from "next/link";

import {
	type AlertSeverityTone,
	type AlertTabKey,
	formatEngineLabel,
	toSeverityTone,
} from "./alert-view-model";

interface AlertListProps {
	readonly alerts: readonly AlertRecordResponse[];
	readonly buildDrawerHref: (alertId: string) => string;
	readonly hasAnyFilter: boolean;
	readonly tab: AlertTabKey;
}

export function AlertList({ alerts, buildDrawerHref, hasAnyFilter, tab }: AlertListProps) {
	if (alerts.length === 0) {
		return <AlertListEmptyState hasAnyFilter={hasAnyFilter} tab={tab} />;
	}
	return (
		<ul className="flex flex-col gap-2">
			{alerts.map((alert) => (
				<AlertListItem alert={alert} buildDrawerHref={buildDrawerHref} key={alert.alert_id} />
			))}
		</ul>
	);
}

function AlertListItem({
	alert,
	buildDrawerHref,
}: {
	readonly alert: AlertRecordResponse;
	readonly buildDrawerHref: (alertId: string) => string;
}) {
	const severity = toSeverityTone(alert.severity);
	return (
		<li>
			<Link
				className="group flex flex-col gap-2 rounded-md border border-border-hairline bg-bg-elevated p-4 transition-colors hover:border-accent/60 hover:bg-surface-overlay"
				href={buildDrawerHref(alert.alert_id)}
			>
				<div className="flex items-start justify-between gap-3">
					<div className="flex min-w-0 flex-col gap-1">
						<div className="flex flex-wrap items-center gap-2">
							<SeverityBadge severity={severity} />
							<StatusBadge status={alert.status} />
							<span className="text-[11px] uppercase tracking-wider text-fg-muted">
								{formatEngineLabel(alert.engine)}
							</span>
						</div>
						<p className="truncate text-sm font-semibold text-fg-primary">{alert.rule_name}</p>
						<p className="truncate font-mono text-xs text-fg-muted">
							{alert.instance_id} · {alert.metric_name}
						</p>
					</div>
					<div className="flex shrink-0 flex-col items-end gap-1 text-right">
						<span className="font-mono text-sm text-fg-primary tabular-nums">
							{formatNumericValue(alert.current_value)}
						</span>
						<span className="font-mono text-[11px] text-fg-muted tabular-nums">
							阈值 {formatNumericValue(alert.threshold)}
						</span>
					</div>
				</div>
				<div className="flex flex-wrap items-center gap-3 text-xs text-fg-muted">
					<span>首次触发 {formatRelativeTime(alert.opened_at)}</span>
					<span>
						负责人{" "}
						<span className="font-mono text-fg-secondary">{alert.owner_user_id ?? "未指派"}</span>
					</span>
					<span>
						确认{" "}
						<span className="font-mono text-fg-secondary">
							{alert.acknowledged_by_user_id ?? "待确认"}
						</span>
					</span>
				</div>
			</Link>
		</li>
	);
}

function SeverityBadge({ severity }: { readonly severity: AlertSeverityTone }) {
	const variant =
		severity === "critical"
			? "destructive"
			: severity === "warning"
				? "warning"
				: severity === "info"
					? "info"
					: "ok";
	return (
		<Badge size="sm" variant={variant}>
			{toSeverityText(severity)}
		</Badge>
	);
}

function StatusBadge({ status }: { readonly status: string }) {
	return (
		<Badge size="sm" variant="outline">
			{toStatusText(status)}
		</Badge>
	);
}

function AlertListEmptyState({
	hasAnyFilter,
	tab,
}: {
	readonly hasAnyFilter: boolean;
	readonly tab: AlertTabKey;
}) {
	const { title, hint } = resolveEmptyText(tab, hasAnyFilter);
	return (
		<div className="flex flex-col items-start gap-2 rounded-md border border-dashed border-border-hairline bg-bg-elevated p-6">
			<p className="text-sm font-medium text-fg-primary">{title}</p>
			<p className="text-xs text-fg-muted">{hint}</p>
		</div>
	);
}

function resolveEmptyText(
	tab: AlertTabKey,
	hasAnyFilter: boolean,
): {
	readonly hint: string;
	readonly title: string;
} {
	if (hasAnyFilter) {
		return { hint: "尝试清除过滤或切换 Tab", title: "当前过滤条件下无告警" };
	}
	if (tab === "resolved") {
		return { hint: "已解决告警会在此归档", title: "暂无已解决告警" };
	}
	if (tab === "active") {
		return { hint: "所有告警均已关闭，值班平稳", title: "当前无活跃告警" };
	}
	return { hint: "接入实例并配置规则后，告警会出现在这里", title: "尚未接入任何告警" };
}

function toSeverityText(severity: AlertSeverityTone): string {
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

function toStatusText(status: string): string {
	if (status === "open") {
		return "活跃";
	}
	if (status === "acknowledged") {
		return "已确认";
	}
	if (status === "resolved") {
		return "已解决";
	}
	return status;
}

function formatNumericValue(value: number): string {
	return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 3 }).format(value);
}
