"use client";

import type { AlertDetailResponse, AlertRecordResponse } from "@db-monitor/api-client";
import {
	Badge,
	Button,
	Dialog,
	DialogBody,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	Separator,
	formatRelativeTime,
} from "@db-monitor/ui";
import { useRouter } from "next/navigation";
import { useCallback, useMemo } from "react";

import {
	acknowledgeAlertAction,
	addAlertNoteAction,
	assignAlertOwnerAction,
} from "../../monitoring-actions";
import { formatEngineLabel, selectRelatedAlerts, toSeverityTone } from "./alert-view-model";

export interface AlertDrawerProps {
	readonly alertDetail: AlertDetailResponse;
	readonly alerts: readonly AlertRecordResponse[];
	readonly closeHref: string;
}

const TIMELINE_MAX_HEIGHT = "max-h-56";

export function AlertDrawer({ alertDetail, alerts, closeHref }: AlertDrawerProps) {
	const router = useRouter();
	const handleOpenChange = useCallback(
		(next: boolean) => {
			if (!next) {
				router.push(closeHref);
			}
		},
		[closeHref, router],
	);

	const { record, history } = alertDetail;
	const severity = toSeverityTone(record.severity);
	const related = useMemo(() => selectRelatedAlerts(alerts, record), [alerts, record]);

	return (
		<Dialog onOpenChange={handleOpenChange} open={true}>
			<DialogContent className="fixed right-4 top-4 bottom-4 m-0 flex w-full max-w-xl flex-col rounded-lg p-0 sm:right-6 sm:top-6 sm:bottom-6">
				<DialogHeader className="flex flex-row items-start justify-between gap-3">
					<div className="flex min-w-0 flex-1 flex-col gap-1.5">
						<DialogTitle className="truncate">{record.rule_name}</DialogTitle>
						<DialogDescription className="truncate font-mono text-xs">
							{formatEngineLabel(record.engine)} · {record.instance_id} · {record.metric_name}
						</DialogDescription>
						<div className="flex flex-wrap gap-1.5">
							<Badge
								size="sm"
								variant={
									severity === "critical"
										? "destructive"
										: severity === "warning"
											? "warning"
											: severity === "info"
												? "info"
												: "ok"
								}
							>
								{toSeverityText(record.severity)}
							</Badge>
							<Badge size="sm" variant="outline">
								{toStatusText(record.status)}
							</Badge>
						</div>
					</div>
					<Button
						aria-label="关闭告警详情"
						onClick={() => handleOpenChange(false)}
						size="sm"
						variant="ghost"
					>
						关闭
					</Button>
				</DialogHeader>
				<DialogBody className="min-h-0 flex-1 overflow-y-auto">
					<div className="flex flex-col gap-5">
						<DrawerSummarySection record={record} />
						<Separator />
						<DrawerTimelineSection history={history} />
						<Separator />
						<DrawerLinkedSignalsSection record={record} />
						<Separator />
						<DrawerRelatedAlertsSection alerts={related} />
					</div>
				</DialogBody>
				<DialogFooter className="flex-col items-stretch gap-3 sm:flex-col">
					<DrawerActionsSection alertId={record.alert_id} record={record} />
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}

function DrawerSummarySection({ record }: { readonly record: AlertRecordResponse }) {
	const rows: readonly { label: string; value: string; mono?: boolean }[] = [
		{ label: "规则", value: record.rule_name },
		{ label: "引擎", value: formatEngineLabel(record.engine) },
		{ label: "实例", mono: true, value: record.instance_id },
		{ label: "指标", mono: true, value: record.metric_name },
		{ label: "当前值", mono: true, value: formatNumber(record.current_value) },
		{ label: "阈值", mono: true, value: formatNumber(record.threshold) },
		{ label: "负责人", mono: true, value: record.owner_user_id ?? "未指派" },
		{ label: "状态", value: toStatusText(record.status) },
		{ label: "首次触发", value: formatRelativeTime(record.opened_at) },
		{
			label: "确认时间",
			value: record.acknowledged_at ? formatRelativeTime(record.acknowledged_at) : "待确认",
		},
	];
	return (
		<section aria-labelledby="alerts-drawer-summary" className="flex flex-col gap-3">
			<SectionHeading id="alerts-drawer-summary" text="概要" />
			<dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
				{rows.map((row) => (
					<div className="flex flex-col gap-0.5" key={row.label}>
						<dt className="text-[11px] uppercase tracking-wider text-fg-muted">{row.label}</dt>
						<dd className={`truncate text-fg-primary ${row.mono ? "font-mono tabular-nums" : ""}`}>
							{row.value}
						</dd>
					</div>
				))}
			</dl>
		</section>
	);
}

function DrawerTimelineSection({
	history,
}: {
	readonly history: AlertDetailResponse["history"];
}) {
	if (history.length === 0) {
		return (
			<section className="flex flex-col gap-3">
				<SectionHeading text="时间线" />
				<p className="text-xs text-fg-muted">尚无事件</p>
			</section>
		);
	}
	return (
		<section className="flex flex-col gap-3">
			<SectionHeading text="时间线" />
			<ol
				className={`relative flex flex-col gap-3 overflow-y-auto border-l border-border-hairline pl-4 ${TIMELINE_MAX_HEIGHT}`}
			>
				{history.map((event, index) => (
					<li className="relative" key={`${event.occurred_at}-${index}`}>
						<span
							aria-hidden
							className="absolute -left-[17px] top-1.5 inline-block h-2 w-2 rounded-full bg-accent"
						/>
						<div className="flex flex-col gap-1">
							<div className="flex items-center gap-2">
								<span className="text-sm font-medium text-fg-primary">
									{toEventLabel(event.event_type)}
								</span>
								<span className="font-mono text-[11px] text-fg-muted tabular-nums">
									{formatRelativeTime(event.occurred_at)}
								</span>
							</div>
							<p className="text-xs text-fg-muted">{event.detail}</p>
						</div>
					</li>
				))}
			</ol>
		</section>
	);
}

function DrawerLinkedSignalsSection({ record }: { readonly record: AlertRecordResponse }) {
	return (
		<section className="flex flex-col gap-3">
			<SectionHeading text="关联信号" />
			<div className="rounded-md border border-dashed border-border-hairline bg-bg-elevated p-3 text-xs text-fg-muted">
				<p>
					指标 <span className="font-mono text-fg-secondary">{record.metric_name}</span>{" "}
					的拓扑信号检索能力即将上线
				</p>
				<p className="mt-1">当前值 / 阈值已在概要展示；联动 Sparkline 将在全局框架就位后呈现</p>
			</div>
		</section>
	);
}

function DrawerRelatedAlertsSection({
	alerts,
}: {
	readonly alerts: readonly AlertRecordResponse[];
}) {
	if (alerts.length === 0) {
		return (
			<section className="flex flex-col gap-3">
				<SectionHeading text="相关告警" />
				<p className="text-xs text-fg-muted">同实例同指标暂无其他活跃告警</p>
			</section>
		);
	}
	return (
		<section className="flex flex-col gap-3">
			<SectionHeading text="相关告警" />
			<ul className="flex flex-col gap-2">
				{alerts.map((alert) => (
					<li
						className="flex items-center justify-between gap-3 rounded-md border border-border-hairline bg-bg-elevated px-3 py-2"
						key={alert.alert_id}
					>
						<div className="flex min-w-0 flex-col">
							<span className="truncate text-sm text-fg-primary">{alert.rule_name}</span>
							<span className="font-mono text-[11px] text-fg-muted">{alert.metric_name}</span>
						</div>
						<Badge size="sm" variant="outline">
							{toStatusText(alert.status)}
						</Badge>
					</li>
				))}
			</ul>
		</section>
	);
}

function DrawerActionsSection({
	alertId,
	record,
}: {
	readonly alertId: string;
	readonly record: AlertRecordResponse;
}) {
	return (
		<section aria-labelledby="alerts-drawer-actions" className="flex w-full flex-col gap-3">
			<SectionHeading id="alerts-drawer-actions" text="处置" />
			<form action={acknowledgeAlertAction} className="flex items-center gap-2">
				<input name="alert_id" type="hidden" value={alertId} />
				<Button className="flex-1" size="md" type="submit" variant="default">
					确认告警
				</Button>
			</form>
			<form action={assignAlertOwnerAction} className="flex flex-col gap-2">
				<input name="alert_id" type="hidden" value={alertId} />
				<label
					className="text-[11px] uppercase tracking-wider text-fg-muted"
					htmlFor="owner_user_id"
				>
					指派负责人
				</label>
				<input
					className="w-full rounded-md border border-border-hairline bg-bg-elevated px-3 py-2 text-sm text-fg-primary outline-none focus:border-accent"
					defaultValue={record.owner_user_id ?? ""}
					id="owner_user_id"
					name="owner_user_id"
					placeholder="填写处置人账号"
					type="text"
				/>
				<Button size="sm" type="submit" variant="outline">
					更新负责人
				</Button>
			</form>
			<form action={addAlertNoteAction} className="flex flex-col gap-2">
				<input name="alert_id" type="hidden" value={alertId} />
				<label className="text-[11px] uppercase tracking-wider text-fg-muted" htmlFor="note">
					添加备注
				</label>
				<textarea
					className="min-h-20 w-full rounded-md border border-border-hairline bg-bg-elevated px-3 py-2 text-sm text-fg-primary outline-none focus:border-accent"
					id="note"
					name="note"
					placeholder="记录排查进展、影响面与下一步"
				/>
				<Button size="sm" type="submit" variant="outline">
					追加备注
				</Button>
			</form>
		</section>
	);
}

function SectionHeading({ id, text }: { readonly id?: string; readonly text: string }) {
	return (
		<h3 className="text-[11px] font-semibold uppercase tracking-wider text-fg-muted" id={id}>
			{text}
		</h3>
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

function toEventLabel(eventType: string): string {
	if (eventType === "opened") {
		return "告警触发";
	}
	if (eventType === "notified") {
		return "已通知";
	}
	if (eventType === "acknowledged") {
		return "已确认";
	}
	if (eventType === "owner_assigned") {
		return "已指派";
	}
	if (eventType === "note_added") {
		return "追加备注";
	}
	if (eventType === "resolved") {
		return "已解决";
	}
	return eventType;
}

function formatNumber(value: number): string {
	return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 3 }).format(value);
}
