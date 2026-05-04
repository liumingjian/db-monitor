import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	EntityBadge,
	PageContent,
} from "@db-monitor/ui";

import { buildInstanceAuditFeed } from "../../../../src/components/instance-detail/audit-feed";
import type { InstanceAuditEvent } from "../../../../src/components/instance-detail/audit-feed";
import { createServerApiClient } from "../../../../src/server-api";

interface AuditPageProps {
	readonly params: Promise<{ readonly instanceId: string }>;
}

const AUDIT_NOTIFY_FETCH_LIMIT = 200;

/**
 * Q13 审计 tab：合成该实例相关的告警 + 通知历史时间线。
 * 前端按 instance_id 过滤 —— 非伪造，是 Settings+Audit page (#8) 同构的合成模式。
 */
export default async function InstanceAuditPage({ params }: AuditPageProps) {
	const { instanceId } = await params;
	const apiClient = await createServerApiClient();
	const [alerts, notifyHistory] = await Promise.all([
		apiClient.listAlerts({ instance: instanceId }),
		apiClient.listNotifyHistory({ limit: AUDIT_NOTIFY_FETCH_LIMIT }),
	]);
	const events = buildInstanceAuditFeed({ alerts, instanceId, notifyHistory });

	return (
		<PageContent>
			<div className="space-y-4 p-6">
				<Card>
					<CardHeader>
						<CardTitle>审计时间线</CardTitle>
						<CardDescription>
							合成该实例的告警事件与通知历史，按时间倒序；数据来源为 `listAlerts` +
							`listNotifyHistory`（无专属端点）。
						</CardDescription>
					</CardHeader>
					<CardContent>
						{events.length === 0 ? <AuditEmptyState /> : <AuditTimeline events={events} />}
					</CardContent>
				</Card>
			</div>
		</PageContent>
	);
}

function AuditEmptyState() {
	return (
		<div className="rounded-md border border-border-subtle bg-surface-overlay px-4 py-4 text-sm text-fg-secondary">
			当前实例尚无告警或通知记录。一旦触发或者发送通道产生尝试，事件会自动出现在这里。
		</div>
	);
}

interface AuditTimelineProps {
	readonly events: readonly InstanceAuditEvent[];
}

function AuditTimeline({ events }: AuditTimelineProps) {
	return (
		<ol className="flex flex-col gap-2">
			{events.map((event) => (
				<li
					className="flex items-start gap-3 rounded-md border border-border-subtle bg-bg-elevated px-3 py-2"
					key={event.id}
				>
					<span className="font-mono text-xs tabular-nums text-fg-muted">{event.occurredAt}</span>
					<EntityBadge label={event.kind === "alert" ? "告警" : "通知"} tone={event.severity} />
					<div className="min-w-0 flex-1">
						<p className="truncate text-sm text-fg-primary">{event.title}</p>
						<p className="truncate text-xs text-fg-muted">{event.detail}</p>
					</div>
					<span className="shrink-0 text-xs font-semibold uppercase tracking-[0.12em] text-fg-muted">
						{event.status}
					</span>
				</li>
			))}
		</ol>
	);
}
