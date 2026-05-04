import type {
	MetricCardResponse,
	MetricSeriesResponse,
	OverviewResponse,
} from "@db-monitor/api-client";
import {
	EntitySummary,
	PageContent,
	QuickMetrics,
	formatPercent,
	formatRelativeTime,
} from "@db-monitor/ui";
import type { EntityBadgeModel, QuickMetricItem } from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";

import { FleetHealthMatrix } from "../../src/components/overview/fleet-health-matrix";
import { InstancesSnapshotTable } from "../../src/components/overview/instances-snapshot-table";
import { OverviewAutoRefresh } from "../../src/components/overview/overview-auto-refresh";
import { OverviewLineChart } from "../../src/components/overview/overview-line-chart";
import { OverviewShell } from "../../src/components/overview/overview-shell";
import { WindowSelector } from "../../src/components/overview/window-selector";
import {
	APPROVED_TIME_WINDOWS,
	createServerApiClient,
	parseTimeWindow,
	requireServerSession,
} from "../../src/server-api";

interface OverviewPageProps {
	readonly searchParams: Promise<{
		readonly window?: string;
	}>;
}

// Row 2-4: the 8 Q9 charts (metric_name + palette index 1..8 + i18n key).
const CHART_SLOTS: readonly {
	readonly metric: string;
	readonly colorIndex: number;
	readonly titleKey: string;
}[] = [
	{ metric: "mysql_threads_connected", colorIndex: 1, titleKey: "chartThreadsConnected" },
	{ metric: "mysql_threads_running", colorIndex: 2, titleKey: "chartThreadsRunning" },
	{ metric: "mysql_queries_per_second", colorIndex: 3, titleKey: "chartQps" },
	{
		metric: "mysql_bytes_received_per_second",
		colorIndex: 4,
		titleKey: "chartBytesReceived",
	},
	{ metric: "mysql_bytes_sent_per_second", colorIndex: 5, titleKey: "chartBytesSent" },
	{
		metric: "mysql_innodb_buffer_pool_reads_per_second",
		colorIndex: 6,
		titleKey: "chartBufferPoolReads",
	},
	{ metric: "mysql_replication_lag_seconds", colorIndex: 7, titleKey: "chartReplicationLag" },
	{ metric: "mysql_uptime_seconds", colorIndex: 8, titleKey: "chartUptime" },
];

const KEY_METRIC_FOR_TABLE = "mysql_queries_per_second";

export default async function OverviewPage({ searchParams }: OverviewPageProps) {
	const session = await requireServerSession("/overview");
	const params = await searchParams;
	const timeWindow = parseTimeWindow(params.window);

	const apiClient = await createServerApiClient();
	const overview = await apiClient.getOverview(timeWindow);

	const t = await getTranslations("overviewPage");
	const tCommon = await getTranslations("common");

	const username = session.displayName ?? session.username ?? tCommon("appName");

	const entitySummary = (
		<EntitySummary
			title={t("summaryTitle")}
			subtitle={t("summarySubtitle", { window: timeWindow })}
			badges={buildHealthBadges(overview, t)}
			actions={
				<>
					<WindowSelector
						currentWindow={timeWindow}
						windows={APPROVED_TIME_WINDOWS}
						ariaLabel={t("windowSelectorLabel")}
					/>
					<OverviewAutoRefresh
						generatedAt={formatRelativeTime(overview.generated_at)}
						generatedAtLabel={t("lastUpdated")}
						pauseLabel={t("pause")}
						resumeLabel={t("resume")}
						refreshLabel={t("refresh")}
					/>
				</>
			}
		/>
	);

	const quickMetrics = <QuickMetrics items={buildQuickMetrics(overview, t)} />;

	return (
		<OverviewShell username={username} entitySummary={entitySummary} quickMetrics={quickMetrics}>
			<PageContent>
				<ChartGrid overview={overview} t={t} />
				<FleetHealthMatrix
					instances={overview.instances}
					title={t("fleetMatrixTitle")}
					subtitle={t("fleetMatrixSubtitle")}
					emptyLabel={t("fleetMatrixEmpty")}
					statusLabels={{
						healthy: t("statusHealthy"),
						unhealthy: t("statusUnhealthy"),
						unknown: t("statusUnknown"),
					}}
				/>
				<InstancesSnapshotTable
					instances={overview.instances}
					heading={t("tableTitle")}
					subheading={t("tableSubtitle")}
					emptyLabel={t("tableEmpty")}
					keyMetricName={KEY_METRIC_FOR_TABLE}
					keyMetricLabel={t("tableKeyMetricLabel")}
					columns={{
						name: t("columnName"),
						engine: t("columnEngine"),
						environment: t("columnEnvironment"),
						status: t("columnStatus"),
						keyMetric: t("columnKeyMetric"),
						labels: t("columnLabels"),
					}}
					statusLabels={{
						healthy: t("statusHealthy"),
						unhealthy: t("statusUnhealthy"),
						unknown: t("statusUnknown"),
					}}
				/>
			</PageContent>
		</OverviewShell>
	);
}

type TFn = Awaited<ReturnType<typeof getTranslations<"overviewPage">>>;

function ChartGrid({ overview, t }: { readonly overview: OverviewResponse; readonly t: TFn }) {
	const chartLookup = new Map<string, MetricSeriesResponse>();
	for (const series of overview.charts) {
		chartLookup.set(series.metric_name, series);
	}

	return (
		<div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
			{CHART_SLOTS.map((slot) => {
				const series = chartLookup.get(slot.metric);
				return (
					<OverviewLineChart
						key={slot.metric}
						title={t(slot.titleKey)}
						unitLabel={series?.unit}
						series={series}
						colorIndex={slot.colorIndex}
						emptyLabel={t("chartEmpty")}
					/>
				);
			})}
		</div>
	);
}

function buildQuickMetrics(overview: OverviewResponse, t: TFn): readonly QuickMetricItem[] {
	const total = overview.summary.total_instances;
	const healthy = overview.summary.healthy_instances;
	const unhealthy = overview.summary.unhealthy_instances;
	const healthyRatio = total === 0 ? null : healthy / total;

	const pickCard = (metric: string): MetricCardResponse | undefined =>
		overview.cards.find((card) => card.metric_name === metric);

	const items: QuickMetricItem[] = [
		{
			key: "total",
			label: t("metricTotalInstances"),
			value: total.toString(),
			hint: t("metricEngines", { count: overview.summary.engines.length }),
		},
		{
			key: "healthy-ratio",
			label: t("metricHealthyRatio"),
			value: formatPercent(healthyRatio),
			hint: t("metricHealthyHint", { healthy, unhealthy }),
		},
	];

	const qps = pickCard("mysql_queries_per_second");
	if (qps) {
		items.push({
			key: "qps",
			label: t("metricQps"),
			value: qps.value.toFixed(2),
			hint: qps.unit,
		});
	}

	const conn = pickCard("mysql_threads_connected");
	if (conn) {
		items.push({
			key: "threads-connected",
			label: t("metricThreadsConnected"),
			value: conn.value.toFixed(0),
			hint: conn.unit,
		});
	}

	const lag = pickCard("mysql_replication_lag_seconds");
	if (lag) {
		items.push({
			key: "replication-lag",
			label: t("metricReplicationLag"),
			value: lag.value.toFixed(1),
			hint: lag.unit,
		});
	}

	return items;
}

function buildHealthBadges(overview: OverviewResponse, t: TFn): readonly EntityBadgeModel[] {
	const { healthy_instances: healthy, unhealthy_instances: unhealthy } = overview.summary;
	const badges: EntityBadgeModel[] = [];
	if (unhealthy > 0) {
		badges.push({ tone: "critical", label: t("badgeUnhealthy", { count: unhealthy }) });
	} else {
		badges.push({ tone: "ok", label: t("badgeAllHealthy") });
	}
	badges.push({ tone: "info", label: t("badgeWindow", { window: overview.window }) });
	return badges;
}
