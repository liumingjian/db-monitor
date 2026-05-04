import type { InstanceResponse, InstanceTrendResponse } from "@db-monitor/api-client";
import {
	Badge,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	PageContent,
	Separator,
} from "@db-monitor/ui";
import type { ReactNode } from "react";

import {
	buildInstanceCapabilityBoundary,
	buildInstancesFlowModel,
	getInstanceConnectionLabel,
	supportsInstanceAnalytics,
} from "../../../src/monitoring-ui";
import { createServerApiClient, parseTimeWindow } from "../../../src/server-api";

interface InstanceOverviewPageProps {
	readonly params: Promise<{ readonly instanceId: string }>;
	readonly searchParams: Promise<{ readonly window?: string }>;
}

/**
 * Q13 概览 tab：实例元信息 + detail readouts + capability boundary。
 *
 * 排版契约 (ui-ux-pro-max Quick Reference §6 Typography):
 * - CardTitle 16px semibold, CardDescription 12px muted — 跨卡统一
 * - DataFieldRow 给字段对一致字号与对齐
 * - mono+tabular 仅用于技术标识 (host:port / version / id / 时间戳数字部分);
 *   中文枚举走 sans
 * - 标签 (labels) 按语义映射 Badge variant, 不再灰底齐平
 */
export default async function InstanceOverviewPage({
	params,
	searchParams,
}: InstanceOverviewPageProps) {
	const { instanceId } = await params;
	const resolvedSearchParams = await searchParams;
	const window = parseTimeWindow(resolvedSearchParams.window);
	const apiClient = await createServerApiClient();
	const instance = await apiClient.getInstance(instanceId);
	const trend = supportsInstanceAnalytics(instance)
		? await safeLoadTrend(apiClient, instanceId, window)
		: null;
	const model = buildInstancesFlowModel({
		selectedInstance: instance,
		tableRows: [instance],
		trend,
	});
	const capabilityBoundary = buildInstanceCapabilityBoundary(instance);

	return (
		<PageContent>
			<div className="grid gap-4 p-6 md:grid-cols-3">
				<InstanceIdentityCard instance={model.selectedInstance} />
				<CapabilityBoundaryCard
					detail={capabilityBoundary.detail}
					value={capabilityBoundary.value}
				/>
				<ServerMetadataCard instance={model.selectedInstance} trend={trend} />
			</div>
			<Separator className="mx-6" />
			<div className="grid gap-4 px-6 py-6 md:grid-cols-3">
				{model.detailReadouts.map((readout) => (
					<Card key={readout.title}>
						<CardHeader>
							<CardTitle>{readout.title}</CardTitle>
						</CardHeader>
						<CardContent>
							<p className="font-mono text-2xl font-semibold tabular-nums text-fg-primary">
								{readout.value}
							</p>
						</CardContent>
					</Card>
				))}
			</div>
		</PageContent>
	);
}

interface InstanceIdentityCardProps {
	readonly instance: InstanceResponse;
}

function InstanceIdentityCard({ instance }: InstanceIdentityCardProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>实例身份</CardTitle>
				<CardDescription>环境 · 引擎 · 连接信息</CardDescription>
			</CardHeader>
			<CardContent>
				<dl className="flex flex-col divide-y divide-border-hairline">
					<DataFieldRow label="环境" value={instance.environment} />
					<DataFieldRow label="引擎" value={instance.engine.toUpperCase()} mono />
					<DataFieldRow
						label={getInstanceConnectionLabel(instance)}
						value={instance.connection.database}
						mono
					/>
					<DataFieldRow
						label="主机"
						value={`${instance.connection.host}:${instance.connection.port}`}
						mono
					/>
					<DataFieldRow
						label="创建"
						value={formatTimestamp(instance.created_at)}
						mono
						title={instance.created_at}
						muted
					/>
				</dl>
			</CardContent>
		</Card>
	);
}

interface CapabilityBoundaryCardProps {
	readonly value: string;
	readonly detail: string;
}

function CapabilityBoundaryCard(props: CapabilityBoundaryCardProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>能力边界</CardTitle>
				<CardDescription>{props.value}</CardDescription>
			</CardHeader>
			<CardContent>
				<p className="text-sm leading-relaxed text-fg-secondary">{props.detail}</p>
			</CardContent>
		</Card>
	);
}

interface ServerMetadataCardProps {
	readonly instance: InstanceResponse;
	readonly trend: InstanceTrendResponse | null;
}

function ServerMetadataCard({ instance, trend }: ServerMetadataCardProps) {
	const serverVersion =
		trend?.instance.server_version ?? instance.validation.server_version ?? "unavailable";
	const serverRole = trend?.instance.server_role ?? "unavailable";

	return (
		<Card>
			<CardHeader>
				<CardTitle>服务端元数据</CardTitle>
				<CardDescription>采集端汇报的版本 / 角色 / 校验</CardDescription>
			</CardHeader>
			<CardContent>
				<dl className="flex flex-col divide-y divide-border-hairline">
					<DataFieldRow
						label="校验状态"
						value={
							<Badge
								size="sm"
								variant={instance.validation.status === "passed" ? "ok" : "destructive"}
							>
								{instance.validation.status}
							</Badge>
						}
					/>
					<DataFieldRow label="服务端版本" value={serverVersion} mono />
					<DataFieldRow label="服务端角色" value={serverRole} mono />
					<DataFieldRow
						label="Labels"
						value={
							instance.labels.length === 0 ? (
								<span className="text-fg-muted">—</span>
							) : (
								<div className="flex flex-wrap justify-end gap-1">
									{instance.labels.map((label) => (
										<Badge key={label} size="sm" variant={resolveLabelVariant(label)}>
											{label}
										</Badge>
									))}
								</div>
							)
						}
					/>
				</dl>
			</CardContent>
		</Card>
	);
}

interface DataFieldRowProps {
	readonly label: string;
	readonly value: ReactNode;
	readonly mono?: boolean;
	readonly muted?: boolean;
	readonly title?: string;
}

function DataFieldRow({ label, value, mono, muted, title }: DataFieldRowProps) {
	const valueClass = [
		"min-w-0 break-words text-right text-sm",
		mono ? "font-mono tabular-nums" : "",
		muted ? "text-fg-secondary" : "text-fg-primary",
	]
		.filter(Boolean)
		.join(" ");
	const isInlineValue = typeof value === "string" || typeof value === "number";

	return (
		<div className="grid grid-cols-[7rem_1fr] items-baseline gap-3 py-2 first:pt-0 last:pb-0">
			<dt className="text-xs text-fg-muted">{label}</dt>
			<dd className={isInlineValue ? valueClass : "min-w-0 text-right text-sm text-fg-primary"}>
				{isInlineValue ? <span title={title}>{value}</span> : value}
			</dd>
		</div>
	);
}

function formatTimestamp(iso: string): string {
	const date = new Date(iso);
	if (Number.isNaN(date.getTime())) {
		return iso;
	}
	const yyyy = date.getUTCFullYear();
	const mm = String(date.getUTCMonth() + 1).padStart(2, "0");
	const dd = String(date.getUTCDate()).padStart(2, "0");
	const hh = String(date.getUTCHours()).padStart(2, "0");
	const mi = String(date.getUTCMinutes()).padStart(2, "0");
	return `${yyyy}-${mm}-${dd} ${hh}:${mi} UTC`;
}

function resolveLabelVariant(
	label: string,
): "destructive" | "warning" | "ok" | "info" | "secondary" {
	const normalized = label.toLowerCase();
	if (normalized === "critical" || normalized === "danger") {
		return "destructive";
	}
	if (normalized === "warning" || normalized === "warn") {
		return "warning";
	}
	if (normalized === "primary" || normalized === "main" || normalized === "leader") {
		return "info";
	}
	if (normalized === "ok" || normalized === "healthy" || normalized === "passed") {
		return "ok";
	}
	return "secondary";
}

async function safeLoadTrend(
	apiClient: Awaited<ReturnType<typeof createServerApiClient>>,
	instanceId: string,
	window: Parameters<typeof apiClient.getInstanceTrends>[1],
): Promise<InstanceTrendResponse | null> {
	try {
		return await apiClient.getInstanceTrends(instanceId, window);
	} catch {
		return null;
	}
}
