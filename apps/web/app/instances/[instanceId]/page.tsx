import type { InstanceResponse, InstanceTrendResponse } from "@db-monitor/api-client";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	PageContent,
	Separator,
} from "@db-monitor/ui";

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
 * Q13 概览 tab：只渲染 instance 元信息 + detail readouts + capability boundary。
 * 走势图、preset、capacity insight 搬到 `/performance` 子路由。
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
					label={capabilityBoundary.label}
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
				<dl className="grid grid-cols-2 gap-3 text-sm">
					<dt className="text-fg-muted">环境</dt>
					<dd className="font-mono tabular-nums text-fg-primary">{instance.environment}</dd>
					<dt className="text-fg-muted">引擎</dt>
					<dd className="font-mono tabular-nums text-fg-primary">
						{instance.engine.toUpperCase()}
					</dd>
					<dt className="text-fg-muted">{getInstanceConnectionLabel(instance)}</dt>
					<dd className="font-mono tabular-nums text-fg-primary">{instance.connection.database}</dd>
					<dt className="text-fg-muted">主机</dt>
					<dd className="font-mono tabular-nums text-fg-primary">
						{instance.connection.host}:{instance.connection.port}
					</dd>
					<dt className="text-fg-muted">创建</dt>
					<dd className="font-mono tabular-nums text-fg-secondary">{instance.created_at}</dd>
				</dl>
			</CardContent>
		</Card>
	);
}

interface CapabilityBoundaryCardProps {
	readonly label: string;
	readonly value: string;
	readonly detail: string;
}

function CapabilityBoundaryCard(props: CapabilityBoundaryCardProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>{props.label}</CardTitle>
				<CardDescription>{props.value}</CardDescription>
			</CardHeader>
			<CardContent>
				<p className="text-sm text-fg-secondary">{props.detail}</p>
			</CardContent>
		</Card>
	);
}

interface ServerMetadataCardProps {
	readonly instance: InstanceResponse;
	readonly trend: InstanceTrendResponse | null;
}

function ServerMetadataCard({ instance, trend }: ServerMetadataCardProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>服务端元数据</CardTitle>
				<CardDescription>采集端汇报的版本 / 角色 / 校验</CardDescription>
			</CardHeader>
			<CardContent>
				<dl className="grid grid-cols-2 gap-3 text-sm">
					<dt className="text-fg-muted">校验状态</dt>
					<dd className="font-mono tabular-nums text-fg-primary">{instance.validation.status}</dd>
					<dt className="text-fg-muted">服务端版本</dt>
					<dd className="font-mono tabular-nums text-fg-primary">
						{trend?.instance.server_version ?? instance.validation.server_version ?? "unavailable"}
					</dd>
					<dt className="text-fg-muted">服务端角色</dt>
					<dd className="font-mono tabular-nums text-fg-primary">
						{trend?.instance.server_role ?? "unavailable"}
					</dd>
					<dt className="text-fg-muted">Labels</dt>
					<dd className="flex flex-wrap gap-1">
						{instance.labels.length === 0 ? (
							<span className="font-mono text-fg-muted">—</span>
						) : (
							instance.labels.map((label) => (
								<span
									className="inline-flex items-center rounded-md border border-border-subtle bg-surface-overlay px-1.5 py-0.5 font-mono text-xs text-fg-secondary"
									key={label}
								>
									{label}
								</span>
							))
						)}
					</dd>
				</dl>
			</CardContent>
		</Card>
	);
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
