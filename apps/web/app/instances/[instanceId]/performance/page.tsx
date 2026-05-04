import type { InstanceResponse, InstanceTrendResponse } from "@db-monitor/api-client";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	PageContent,
} from "@db-monitor/ui";

import { buildInstancePresets } from "../../../../src/analytics-presets";
import { AnalyticsPresetNav } from "../../../../src/components/analytics-preset-nav";
import { MetricChart } from "../../../../src/components/metric-chart";
import { TimeWindowNav } from "../../../../src/components/time-window-nav";
import {
	type InsightTone,
	MONITORING_CHART_FRAME,
	buildInstancesFlowModel,
	supportsInstanceAnalytics,
} from "../../../../src/monitoring-ui";
import { createServerApiClient, parseTimeWindow } from "../../../../src/server-api";

interface PerformancePageProps {
	readonly params: Promise<{ readonly instanceId: string }>;
	readonly searchParams: Promise<{ readonly window?: string }>;
}

/**
 * Q13 性能 tab：time-window nav + preset nav + metric cards + 主图。
 */
export default async function PerformancePage({ params, searchParams }: PerformancePageProps) {
	const { instanceId } = await params;
	const resolvedSearchParams = await searchParams;
	const window = parseTimeWindow(resolvedSearchParams.window);
	const apiClient = await createServerApiClient();
	const instance = await apiClient.getInstance(instanceId);
	if (!supportsInstanceAnalytics(instance)) {
		return <AnalyticsUnsupportedNotice />;
	}
	const trend = await safeLoadTrend(apiClient, instanceId, window);
	if (trend === null) {
		return <TrendUnavailableNotice />;
	}
	const model = buildInstancesFlowModel({
		selectedInstance: instance,
		tableRows: [instance],
		trend,
	});

	return (
		<PageContent>
			<div className="space-y-4 p-6">
				<TimeWindowRow instance={instance} trend={trend} />
				<Card>
					<CardHeader>
						<CardTitle>Preset views</CardTitle>
						<CardDescription>
							以稳定路由 + 观察窗口重新打开该实例，用于常见处置回路。
						</CardDescription>
					</CardHeader>
					<CardContent>
						<AnalyticsPresetNav
							currentWindow={trend.window}
							presets={buildInstancePresets(instance.instance_id)}
						/>
					</CardContent>
				</Card>
				<div className="grid gap-4 md:grid-cols-2">
					{trend.cards.map((card) => (
						<Card key={card.metric_name}>
							<CardHeader>
								<CardTitle>{card.label}</CardTitle>
								<CardDescription>{card.unit}</CardDescription>
							</CardHeader>
							<CardContent>
								<p className="font-mono text-3xl font-semibold tabular-nums text-fg-primary">
									{formatMetricNumber(card.value)}
								</p>
							</CardContent>
						</Card>
					))}
				</div>
				<Card>
					<CardHeader>
						<CardTitle>Capacity readout</CardTitle>
						<CardDescription>基于当前窗口计算的容量 / 压力信号</CardDescription>
					</CardHeader>
					<CardContent>
						<div className="grid gap-3 md:grid-cols-3">
							{model.capacityReadout.map((insight) => (
								<CapacityInsightCard
									detail={insight.detail}
									key={insight.title}
									title={insight.title}
									tone={insight.tone}
									value={insight.value}
								/>
							))}
						</div>
					</CardContent>
				</Card>
				<Card>
					<CardHeader>
						<CardTitle>{MONITORING_CHART_FRAME.title}</CardTitle>
						<CardDescription>观察窗口 {trend.window}</CardDescription>
					</CardHeader>
					<CardContent>
						<MetricChart
							emptyState={MONITORING_CHART_FRAME.emptyState}
							series={trend.charts}
							title={MONITORING_CHART_FRAME.title}
						/>
					</CardContent>
				</Card>
			</div>
		</PageContent>
	);
}

interface TimeWindowRowProps {
	readonly instance: InstanceResponse;
	readonly trend: InstanceTrendResponse;
}

function TimeWindowRow({ instance, trend }: TimeWindowRowProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>Trend window</CardTitle>
				<CardDescription>
					在允许的观察窗口之间切换，URL 决定路由族，不影响已打开的实例视图。
				</CardDescription>
			</CardHeader>
			<CardContent>
				<TimeWindowNav
					currentWindow={trend.window}
					pathname={`/instances/${instance.instance_id}/performance`}
				/>
			</CardContent>
		</Card>
	);
}

interface CapacityInsightCardProps {
	readonly title: string;
	readonly value: string;
	readonly detail: string;
	readonly tone: InsightTone;
}

function CapacityInsightCard(props: CapacityInsightCardProps) {
	const toneClass =
		props.tone === "risk"
			? "border-sev-critical-border bg-sev-critical-bg"
			: props.tone === "watch"
				? "border-sev-warning-border bg-sev-warning-bg"
				: "border-border-subtle bg-surface-overlay";
	return (
		<div className={`rounded-md border px-4 py-3 ${toneClass}`}>
			<p className="text-xs font-semibold uppercase tracking-[0.18em] text-fg-muted">
				{props.title}
			</p>
			<p className="mt-2 font-mono text-lg font-semibold tabular-nums text-fg-primary">
				{props.value}
			</p>
			<p className="mt-1 text-xs text-fg-secondary">{props.detail}</p>
		</div>
	);
}

function AnalyticsUnsupportedNotice() {
	return (
		<PageContent>
			<div className="px-6 py-6">
				<Card>
					<CardHeader>
						<CardTitle>当前引擎暂不支持 trend 分析</CardTitle>
						<CardDescription>
							仅 MySQL 与 Oracle 实例支持性能 tab 的窗口 / 预设 / capacity readout。
						</CardDescription>
					</CardHeader>
				</Card>
			</div>
		</PageContent>
	);
}

function TrendUnavailableNotice() {
	return (
		<PageContent>
			<div className="px-6 py-6">
				<Card>
					<CardHeader>
						<CardTitle>性能数据暂未上报</CardTitle>
						<CardDescription>
							采集端尚未推送 trend；稍后刷新即可看到窗口 / 指标 / 图表。
						</CardDescription>
					</CardHeader>
				</Card>
			</div>
		</PageContent>
	);
}

function formatMetricNumber(value: number): string {
	if (!Number.isFinite(value)) {
		return "—";
	}
	if (Math.abs(value) >= 1000) {
		return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
	}
	return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
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
