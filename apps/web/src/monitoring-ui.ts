import type {
	AlertDetailResponse,
	AlertEngineCatalogResponse,
	AlertRecordResponse,
	AlertRuleResponse,
	InstanceResponse,
	InstanceTrendResponse,
	OverviewResponse,
	SystemSettingResponse,
} from "@db-monitor/api-client";
import {
	ALERT_TABLE_COLUMNS,
	INSTANCE_CHART_FRAME,
	INSTANCE_FORM_FIELDS,
	INSTANCE_TABLE_COLUMNS,
	OVERVIEW_CHART_FRAME,
	RULE_FORM_FIELDS,
	type RULE_OPERATORS,
	type RULE_SEVERITIES,
	RULE_TABLE_COLUMNS,
	SETTINGS_FORM_FIELDS,
} from "@db-monitor/ui";

import {
	PREVIEW_ALERTS,
	PREVIEW_ALERT_DETAIL,
	PREVIEW_INSTANCE,
	PREVIEW_INSTANCE_FORM_VALUES,
	PREVIEW_ORACLE_INSTANCE_TREND,
	PREVIEW_INSTANCE_TREND,
	PREVIEW_OVERVIEW,
	PREVIEW_RULE_CATALOG,
	PREVIEW_RULES,
	PREVIEW_RULE_FORM_VALUES,
	PREVIEW_SETTINGS,
} from "./monitoring-preview";

export interface InstanceFormValues {
	readonly engine: "mysql" | "oracle";
	readonly database: string;
	readonly environment: string;
	readonly host: string;
	readonly labels: string;
	readonly name: string;
	readonly password: string;
	readonly port: string;
	readonly username: string;
}

export interface InstanceListFilterValues {
	readonly environment: string;
	readonly label: string;
	readonly name: string;
	readonly status: "" | "failed" | "passed";
}

export interface RuleFormValues {
	readonly engine: "mysql" | "oracle";
	readonly instance_ids: string;
	readonly metric_name: string;
	readonly name: string;
	readonly operator: (typeof RULE_OPERATORS)[number];
	readonly severity: (typeof RULE_SEVERITIES)[number];
	readonly threshold: string;
}

export interface AlertListFilterValues {
	readonly instance: string;
	readonly opened_after: string;
	readonly opened_before: string;
	readonly severity: "" | "critical" | "warning";
	readonly status: "" | "acknowledged" | "open" | "resolved";
}

export type InsightTone = "steady" | "watch" | "risk";

export interface CapacityInsight {
	readonly detail: string;
	readonly title: string;
	readonly tone: InsightTone;
	readonly value: string;
}

export interface CapacityLeader {
	readonly detail: string;
	readonly instanceName: string;
	readonly title: string;
	readonly value: string;
}

export interface DashboardReadout {
	readonly detail: string;
	readonly title: string;
	readonly value: string;
}

export interface InstancesFlowModel {
	readonly capacityReadout: readonly CapacityInsight[];
	readonly detailSeries: readonly string[];
	readonly filters: InstanceListFilterValues;
	readonly formFields: typeof INSTANCE_FORM_FIELDS;
	readonly formValues: InstanceFormValues;
	readonly selectedInstance: InstanceResponse;
	readonly tableColumns: typeof INSTANCE_TABLE_COLUMNS;
	readonly tableRows: readonly InstanceResponse[];
	readonly trend: InstanceTrendResponse | null;
}

export interface DashboardModel {
	readonly capabilityBoundary: InstanceCapabilityBoundary;
	readonly chartFrame: typeof OVERVIEW_CHART_FRAME;
	readonly chartSeries: readonly string[];
	readonly capacityInsights: readonly CapacityInsight[];
	readonly capacityLeaders: readonly CapacityLeader[];
	readonly coverageReadout: readonly DashboardReadout[];
	readonly engineSummaries: readonly DashboardReadout[];
	readonly heroMetrics: readonly { readonly label: string; readonly value: number }[];
	readonly overview: OverviewResponse;
}

export interface OperationsModel {
	readonly alertColumns: typeof ALERT_TABLE_COLUMNS;
	readonly alertDetail: AlertDetailResponse;
	readonly alertFilters: AlertListFilterValues;
	readonly alerts: readonly AlertRecordResponse[];
	readonly ruleCatalog: readonly AlertEngineCatalogResponse[];
	readonly ruleColumns: typeof RULE_TABLE_COLUMNS;
	readonly ruleFields: typeof RULE_FORM_FIELDS;
	readonly ruleFormValues: RuleFormValues;
	readonly rules: readonly AlertRuleResponse[];
	readonly settingFields: typeof SETTINGS_FORM_FIELDS;
	readonly settings: readonly SystemSettingResponse[];
}

export function buildDashboardModel(overview: OverviewResponse = PREVIEW_OVERVIEW): DashboardModel {
	return {
		capabilityBoundary: buildOverviewCapabilityBoundary(overview),
		chartFrame: buildOverviewChartFrame(overview),
		chartSeries: overview.charts.map((series) => series.metric_name),
		capacityInsights: buildOverviewCapacityInsights(overview),
		capacityLeaders: buildOverviewCapacityLeaders(overview),
		coverageReadout: buildOverviewCoverageReadout(overview),
		engineSummaries: buildOverviewEngineSummaries(overview),
		heroMetrics: buildOverviewHeroMetrics(overview),
		overview,
	};
}

export function buildInstancesFlowModel(
	options: {
		readonly filters?: Partial<InstanceListFilterValues>;
		readonly formValues?: InstanceFormValues;
		readonly selectedInstance?: InstanceResponse;
		readonly tableRows?: readonly InstanceResponse[];
		readonly trend?: InstanceTrendResponse | null;
	} = {},
): InstancesFlowModel {
	const selectedInstance = options.selectedInstance ?? PREVIEW_INSTANCE;
	const trend =
		options.trend === undefined
			? selectedInstance.engine === "oracle"
				? PREVIEW_ORACLE_INSTANCE_TREND
				: PREVIEW_INSTANCE_TREND
			: options.trend;
	return {
		capacityReadout:
			trend === null ? [] : buildInstanceCapacityReadout(selectedInstance, trend),
		detailSeries: trend === null ? [] : trend.charts.map((series) => series.metric_name),
		filters: buildInstanceListFilterValues(options.filters),
		formFields: INSTANCE_FORM_FIELDS,
		formValues: options.formValues ?? PREVIEW_INSTANCE_FORM_VALUES,
		selectedInstance,
		tableColumns: INSTANCE_TABLE_COLUMNS,
		tableRows: options.tableRows ?? [selectedInstance],
		trend,
	};
}

export function buildOperationsModel(
	options: {
		readonly alertDetail?: AlertDetailResponse;
		readonly alertFilters?: Partial<AlertListFilterValues>;
		readonly alerts?: readonly AlertRecordResponse[];
		readonly ruleCatalog?: readonly AlertEngineCatalogResponse[];
		readonly ruleFormValues?: RuleFormValues;
		readonly rules?: readonly AlertRuleResponse[];
		readonly settings?: readonly SystemSettingResponse[];
	} = {},
): OperationsModel {
	return {
		alertColumns: ALERT_TABLE_COLUMNS,
		alertDetail: options.alertDetail ?? PREVIEW_ALERT_DETAIL,
		alertFilters: buildAlertListFilterValues(options.alertFilters),
		alerts: options.alerts ?? PREVIEW_ALERTS,
		ruleCatalog: options.ruleCatalog ?? PREVIEW_RULE_CATALOG,
		ruleColumns: RULE_TABLE_COLUMNS,
		ruleFields: RULE_FORM_FIELDS,
		ruleFormValues: options.ruleFormValues ?? PREVIEW_RULE_FORM_VALUES,
		rules: options.rules ?? PREVIEW_RULES,
		settingFields: SETTINGS_FORM_FIELDS,
		settings: options.settings ?? PREVIEW_SETTINGS,
	};
}

export function buildSmokeRouteSet(): readonly string[] {
	return [
		"/login",
		"/overview",
		"/instances",
		"/instances/inst-prod-primary",
		"/alerts",
		"/alerts/alert-lag",
		"/rules",
		"/settings",
	];
}

export function buildInstanceListFilterValues(
	filters: Partial<Record<keyof InstanceListFilterValues, string | undefined>> = {},
): InstanceListFilterValues {
	return {
		environment: normalizeTextFilter(filters.environment),
		label: normalizeTextFilter(filters.label),
		name: normalizeTextFilter(filters.name),
		status: normalizeEnumFilter(filters.status, ["failed", "passed"] as const),
	};
}

export function buildAlertListFilterValues(
	filters: Partial<Record<keyof AlertListFilterValues, string | undefined>> = {},
): AlertListFilterValues {
	return {
		instance: normalizeTextFilter(filters.instance),
		opened_after: normalizeTextFilter(filters.opened_after),
		opened_before: normalizeTextFilter(filters.opened_before),
		severity: normalizeEnumFilter(filters.severity, ["critical", "warning"] as const),
		status: normalizeEnumFilter(filters.status, ["acknowledged", "open", "resolved"] as const),
	};
}

export const MONITORING_CHART_FRAME = INSTANCE_CHART_FRAME;

export interface InstanceCapabilityBoundary {
	readonly detail: string;
	readonly label: string;
	readonly value: string;
}

export function buildInstanceCapabilityBoundary(
	instance: InstanceResponse,
): InstanceCapabilityBoundary {
	if (instance.engine === "oracle") {
		return {
			detail:
				"Oracle instances now expose minimal trend analytics, preset windows, and capacity readouts on the detail page, and they contribute to fleet health and engine coverage on the overview. Cards, charts, and signal leaders still follow the engines listed in overview coverage.",
			label: "Capability boundary",
			value: "Fleet health + trends available",
		};
	}
	return {
		detail:
			"MySQL instances support onboarding, validation, fleet metrics, trend analytics, preset views, and capacity readouts in the current UI.",
		label: "Capability boundary",
		value: "Fleet + detail analytics",
	};
}

export function getInstanceConnectionLabel(instance: InstanceResponse): string {
	return instance.engine === "oracle" ? "DSN / Service" : "Database";
}

export function supportsInstanceAnalytics(instance: InstanceResponse): boolean {
	return instance.engine === "mysql" || instance.engine === "oracle";
}

function normalizeTextFilter(value: string | undefined): string {
	return value?.trim() ?? "";
}

function normalizeEnumFilter<const TAllowed extends readonly string[]>(
	value: string | undefined,
	allowed: TAllowed,
): TAllowed[number] | "" {
	return value !== undefined && allowed.includes(value as TAllowed[number])
		? (value as TAllowed[number])
		: "";
}

function buildOverviewCapacityInsights(overview: OverviewResponse): readonly CapacityInsight[] {
	if (!hasOverviewMetricCoverage(overview)) {
		return [
			{
				detail: `Fleet health and engine summary are available for ${formatEngineCoverageValue(overview.coverage.fleet_health_engines)}, but overview cards and leaders are not populated for the observed engines yet.`,
				title: "Fleet metric scope",
				tone: "watch",
				value: "Health-only view",
			},
			{
				detail: "Open individual instances to inspect supported trend analytics and engine-specific readouts.",
				title: "Detail analytics",
				tone: "steady",
				value: formatEngineCoverageValue(overview.coverage.detail_analytics_engines),
			},
			{
				detail: `${overview.summary.total_instances} instances are represented in the current overview window.`,
				title: "Observed engines",
				tone: "steady",
				value: formatEngineCoverageValue(overview.summary.engines.map((summary) => summary.engine)),
			},
		];
	}

	const metricScopeLabel = formatEngineCoverageValue(overview.coverage.overview_metric_engines);
	const metricInstances = getOverviewMetricInstances(overview);
	const inbound = getCardMetricValue(overview.cards, "mysql_bytes_received_per_second");
	const outbound = getCardMetricValue(overview.cards, "mysql_bytes_sent_per_second");
	const bufferPoolReads = getCardMetricValue(
		overview.cards,
		"mysql_innodb_buffer_pool_reads_per_second",
	);
	const lagLeader = selectTopInstance(
		metricInstances,
		(instance) => instance.replication_lag_seconds,
	);

	if (hasPartialOverviewMetricCoverage(overview)) {
		return [
			buildTrafficDirectionInsight(inbound, outbound, {
				subject: `${metricScopeLabel} overview coverage`,
				title: `${metricScopeLabel} traffic direction`,
			}),
			buildEnginePressureInsight(bufferPoolReads, {
				subject: `${metricScopeLabel} overview coverage`,
				title: `${metricScopeLabel} engine pressure`,
			}),
			buildCoverageBoundaryInsight(overview),
		];
	}

	return [
		buildTrafficDirectionInsight(inbound, outbound),
		buildEnginePressureInsight(bufferPoolReads),
		buildReplicaHeadroomInsight(lagLeader),
	];
}

function buildOverviewCapacityLeaders(overview: OverviewResponse): readonly CapacityLeader[] {
	const metricInstances = getOverviewMetricInstances(overview);
	if (metricInstances.length === 0) {
		return [];
	}
	const partialCoverage = hasPartialOverviewMetricCoverage(overview);
	const metricScopeLabel = formatEngineCoverageValue(overview.coverage.overview_metric_engines);

	return [
		buildLeader({
			detail: partialCoverage
				? `Among ${metricScopeLabel} overview instances, queries are concentrating here fastest in the current window.`
				: "Queries are concentrating here fastest in the current window.",
			instance: selectTopInstance(metricInstances, (instance) => instance.qps),
			title: partialCoverage ? `Highest ${metricScopeLabel} QPS` : "Highest QPS",
			unit: "qps",
			valueSelector: (instance) => instance.qps,
		}),
		buildLeader({
			detail: partialCoverage
				? `Among ${metricScopeLabel} overview instances, this node is carrying the densest active concurrency right now.`
				: "This instance is carrying the densest active concurrency right now.",
			instance: selectTopInstance(metricInstances, (instance) => instance.threads_running),
			title: partialCoverage
				? `Most ${metricScopeLabel} Running Threads`
				: "Most Running Threads",
			unit: "threads",
			valueSelector: (instance) => instance.threads_running,
		}),
		buildLeader({
			detail: partialCoverage
				? `Among ${metricScopeLabel} overview instances, replica freshness is loosest here, so this is the first place to investigate.`
				: "Replica freshness is loosest here, so this is the first place to investigate.",
			instance: selectTopInstance(
				metricInstances,
				(instance) => instance.replication_lag_seconds,
			),
			title: partialCoverage
				? `Worst ${metricScopeLabel} Replication Lag`
				: "Worst Replication Lag",
			unit: "seconds",
			valueSelector: (instance) => instance.replication_lag_seconds,
		}),
	].filter((leader): leader is CapacityLeader => leader !== null);
}

function buildInstanceCapacityReadout(
	instance: InstanceResponse,
	trend: InstanceTrendResponse,
): readonly CapacityInsight[] {
	if (instance.engine === "oracle") {
		const userCalls = getCardMetricValue(trend.cards, "oracle_user_calls_per_second");
		const physicalReads = getCardMetricValue(
			trend.cards,
			"oracle_physical_reads_per_second",
		);
		const sessionsTotal = getCardMetricValue(trend.cards, "oracle_sessions_total");
		const sessionsActive = getCardMetricValue(trend.cards, "oracle_sessions_active");
		const sessionWaits = getCardMetricValue(trend.cards, "oracle_session_waits");
		const activeShare =
			sessionsTotal <= 0 ? 0 : Math.min(sessionsActive / sessionsTotal, 1);

		return [
			{
				detail: `${formatMetricValue(userCalls, "calls/s")} user calls versus ${formatMetricValue(physicalReads, "reads/s")} physical reads in this window.`,
				title: "Workload direction",
				tone: "steady",
				value: describeOracleWorkloadDirection(userCalls, physicalReads),
			},
			describeOracleEnginePressure(sessionWaits, physicalReads),
			describeOracleConcurrencyPosture(sessionsTotal, sessionsActive, activeShare),
		];
	}

	const inbound = getCardMetricValue(trend.cards, "mysql_bytes_received_per_second");
	const outbound = getCardMetricValue(trend.cards, "mysql_bytes_sent_per_second");
	const bufferPoolReads = getCardMetricValue(
		trend.cards,
		"mysql_innodb_buffer_pool_reads_per_second",
	);
	const qps = getCardMetricValue(trend.cards, "mysql_queries_per_second");
	const replicationLag = getCardMetricValue(trend.cards, "mysql_replication_lag_seconds");
	const threadsConnected = getCardMetricValue(trend.cards, "mysql_threads_connected");
	const threadsRunning = getCardMetricValue(trend.cards, "mysql_threads_running");
	const runningShare =
		threadsConnected <= 0 ? 0 : Math.min(threadsRunning / threadsConnected, 1);

	return [
		{
			detail: `${formatMetricValue(outbound, "bytes/s")} out vs ${formatMetricValue(inbound, "bytes/s")} in at ${formatMetricValue(qps, "qps")}.`,
			title: "Workload direction",
			tone: "steady",
			value: describeTrafficDirection(inbound, outbound),
		},
		describeDetailEnginePressure(bufferPoolReads, replicationLag),
		describeConcurrencyPosture(threadsConnected, threadsRunning, runningShare),
	];
}

function buildTrafficDirectionInsight(
	inbound: number,
	outbound: number,
	options: {
		readonly subject: string;
		readonly title: string;
	} = {
		subject: "Fleet",
		title: "Traffic direction",
	},
): CapacityInsight {
	const value = describeTrafficDirection(inbound, outbound);
	if (value === "Serving-heavy") {
		return {
			detail: `${options.subject} egress is ${formatMetricValue(outbound, "bytes/s")} versus ${formatMetricValue(inbound, "bytes/s")} ingress in this window.`,
			title: options.title,
			tone: "steady",
			value,
		};
	}
	if (value === "Write-heavy") {
		return {
			detail: `${options.subject} ingress is ${formatMetricValue(inbound, "bytes/s")} versus ${formatMetricValue(outbound, "bytes/s")} egress in this window.`,
			title: options.title,
			tone: "steady",
			value,
		};
	}
	return {
		detail: `${options.subject} ingress ${formatMetricValue(inbound, "bytes/s")} and egress ${formatMetricValue(outbound, "bytes/s")} are moving in the same band.`,
		title: options.title,
		tone: "steady",
		value,
	};
}

function buildEnginePressureInsight(
	bufferPoolReads: number,
	options: {
		readonly subject: string;
		readonly title: string;
	} = {
		subject: "Fleet",
		title: "Engine pressure",
	},
): CapacityInsight {
	if (bufferPoolReads >= 1) {
		return {
			detail: `${options.subject} buffer pool reads are already at ${formatMetricValue(bufferPoolReads, "reads/s")}, which suggests the working set is missing cache.`,
			title: options.title,
			tone: "risk",
			value: "Hot cache misses",
		};
	}
	if (bufferPoolReads > 0) {
		return {
			detail: `${options.subject} buffer pool reads are visible at ${formatMetricValue(bufferPoolReads, "reads/s")}; keep an eye on cache churn if throughput rises.`,
			title: options.title,
			tone: "watch",
			value: "Watch cache misses",
		};
	}
	return {
		detail: `No buffer pool read misses have surfaced across ${options.subject.toLowerCase()} in the current window.`,
		title: options.title,
		tone: "steady",
		value: "Cache stable",
	};
}

function buildReplicaHeadroomInsight(
	lagLeader: OverviewResponse["instances"][number] | null,
	options: {
		readonly title: string;
	} = {
		title: "Replica headroom",
	},
): CapacityInsight {
	if (lagLeader === null || lagLeader.replication_lag_seconds <= 0) {
		return {
			detail: "No instance is reporting replica lag in the current observation window.",
			title: options.title,
			tone: "steady",
			value: "Fresh replicas",
		};
	}
	if (lagLeader.replication_lag_seconds >= 5) {
		return {
			detail: `${lagLeader.name} is lagging by ${formatMetricValue(lagLeader.replication_lag_seconds, "seconds")}.`,
			title: options.title,
			tone: "risk",
			value: "Replica lag risk",
		};
	}
	return {
		detail: `${lagLeader.name} is the current lag leader at ${formatMetricValue(lagLeader.replication_lag_seconds, "seconds")}.`,
		title: options.title,
		tone: "watch",
		value: "Replica lag visible",
	};
}

function describeDetailEnginePressure(
	bufferPoolReads: number,
	replicationLag: number,
): CapacityInsight {
	if (replicationLag >= 5 || bufferPoolReads >= 1) {
		return {
			detail: `Replication lag is ${formatMetricValue(replicationLag, "seconds")} and buffer pool reads are ${formatMetricValue(bufferPoolReads, "reads/s")}.`,
			title: "Engine pressure",
			tone: "risk",
			value: "Risk visible",
		};
	}
	if (replicationLag > 0 || bufferPoolReads > 0) {
		return {
			detail: `Replication lag is ${formatMetricValue(replicationLag, "seconds")} with buffer pool reads at ${formatMetricValue(bufferPoolReads, "reads/s")}.`,
			title: "Engine pressure",
			tone: "watch",
			value: "Watch trend",
		};
	}
	return {
		detail: "Replica lag and buffer pool read pressure are both quiet in this window.",
		title: "Engine pressure",
		tone: "steady",
		value: "Stable",
	};
}

function describeOracleWorkloadDirection(
	userCalls: number,
	physicalReads: number,
): string {
	if (userCalls > 0 && userCalls >= physicalReads * 1.25) {
		return "Call-heavy";
	}
	if (physicalReads > 0 && physicalReads >= userCalls * 1.25) {
		return "Read-heavy";
	}
	return "Balanced";
}

function describeOracleEnginePressure(
	sessionWaits: number,
	physicalReads: number,
): CapacityInsight {
	if (sessionWaits >= 5 || physicalReads >= 1) {
		return {
			detail: `Session waits are ${formatMetricValue(sessionWaits, "sessions")} with physical reads at ${formatMetricValue(physicalReads, "reads/s")}.`,
			title: "Engine pressure",
			tone: "risk",
			value: "Wait pressure",
		};
	}
	if (sessionWaits > 0 || physicalReads > 0) {
		return {
			detail: `Session waits are ${formatMetricValue(sessionWaits, "sessions")} while physical reads are ${formatMetricValue(physicalReads, "reads/s")}.`,
			title: "Engine pressure",
			tone: "watch",
			value: "Watch waits",
		};
	}
	return {
		detail: "Session waits and physical reads are both quiet in this window.",
		title: "Engine pressure",
		tone: "steady",
		value: "Waits quiet",
	};
}

function describeOracleConcurrencyPosture(
	sessionsTotal: number,
	sessionsActive: number,
	activeShare: number,
): CapacityInsight {
	if (sessionsActive <= 0) {
		return {
			detail: `No active sessions are visible out of ${formatMetricValue(sessionsTotal, "sessions")} total.`,
			title: "Concurrency posture",
			tone: "steady",
			value: "Idle",
		};
	}
	if (activeShare >= 0.5) {
		return {
			detail: `${formatMetricValue(sessionsActive, "sessions")} of ${formatMetricValue(sessionsTotal, "sessions")} sessions are active right now.`,
			title: "Concurrency posture",
			tone: "watch",
			value: "Hot session set",
		};
	}
	return {
		detail: `${formatMetricValue(sessionsActive, "sessions")} of ${formatMetricValue(sessionsTotal, "sessions")} sessions are active right now.`,
		title: "Concurrency posture",
		tone: "steady",
		value: "Pooled headroom",
	};
}

function describeConcurrencyPosture(
	threadsConnected: number,
	threadsRunning: number,
	runningShare: number,
): CapacityInsight {
	if (threadsRunning <= 0) {
		return {
			detail: `No active threads are running out of ${formatMetricValue(threadsConnected, "connections")} connected.`,
			title: "Concurrency posture",
			tone: "steady",
			value: "Idle",
		};
	}
	if (runningShare >= 0.5) {
		return {
			detail: `${formatMetricValue(threadsRunning, "threads")} of ${formatMetricValue(threadsConnected, "connections")} connected threads are currently active.`,
			title: "Concurrency posture",
			tone: "watch",
			value: "Hot working set",
		};
	}
	return {
		detail: `${formatMetricValue(threadsRunning, "threads")} of ${formatMetricValue(threadsConnected, "connections")} connected threads are currently active.`,
		title: "Concurrency posture",
		tone: "steady",
		value: "Pooled headroom",
	};
}

function describeTrafficDirection(inbound: number, outbound: number): string {
	if (outbound > 0 && outbound >= inbound * 1.25) {
		return "Serving-heavy";
	}
	if (inbound > 0 && inbound >= outbound * 1.25) {
		return "Write-heavy";
	}
	return "Balanced";
}

function buildOverviewHeroMetrics(
	overview: OverviewResponse,
): readonly { readonly label: string; readonly value: number }[] {
	if (!hasPartialOverviewMetricCoverage(overview)) {
		return overview.cards.map((card) => ({ label: card.label, value: card.value }));
	}
	const metricScopeLabel = formatEngineCoverageValue(overview.coverage.overview_metric_engines);
	return overview.cards.map((card) => ({
		label: `${metricScopeLabel} ${card.label}`,
		value: card.value,
	}));
}

function buildOverviewChartFrame(
	overview: OverviewResponse,
): typeof OVERVIEW_CHART_FRAME {
	if (!hasPartialOverviewMetricCoverage(overview)) {
		return OVERVIEW_CHART_FRAME;
	}
	const metricScopeLabel = formatEngineCoverageValue(overview.coverage.overview_metric_engines);
	return {
		...OVERVIEW_CHART_FRAME,
		title: `${metricScopeLabel} Fleet Activity`,
	};
}

function buildOverviewCapabilityBoundary(
	overview: OverviewResponse,
): InstanceCapabilityBoundary {
	const detailCoverage = formatEngineCoverageValue(overview.coverage.detail_analytics_engines);
	const fleetHealthCoverage = formatEngineCoverageValue(overview.coverage.fleet_health_engines);
	const overviewMetricCoverage = formatEngineCoverageValue(
		overview.coverage.overview_metric_engines,
	);

	if (!hasOverviewMetricCoverage(overview)) {
		return {
			detail: `Fleet health and engine summary currently cover ${fleetHealthCoverage}. Detail analytics are available for ${detailCoverage}, but overview cards, charts, and signal leaders are not populated for the observed engines yet.`,
			label: "Capability boundary",
			value: "Health-only overview",
		};
	}
	if (hasPartialOverviewMetricCoverage(overview)) {
		return {
			detail: `Fleet health and engine summary cover ${fleetHealthCoverage}. Detail analytics are available for ${detailCoverage}. Overview cards, charts, and signal leaders currently reflect ${overviewMetricCoverage} coverage.`,
			label: "Capability boundary",
			value: "Mixed-engine baseline",
		};
	}
	return {
		detail: `Fleet health, cards, charts, and signal leaders currently align on ${overviewMetricCoverage} coverage in the overview.`,
		label: "Capability boundary",
		value: "Fleet metrics available",
	};
}

function buildOverviewCoverageReadout(
	overview: OverviewResponse,
): readonly DashboardReadout[] {
	return [
		{
			detail: "Per-instance trend analytics and capacity readouts.",
			title: "Detail analytics",
			value: formatEngineCoverageValue(overview.coverage.detail_analytics_engines),
		},
		{
			detail: "Fleet summary health and instance status coverage.",
			title: "Fleet health",
			value: formatEngineCoverageValue(overview.coverage.fleet_health_engines),
		},
		{
			detail: "Overview cards, charts, and signal leaders currently draw from these engines.",
			title: "Fleet metrics",
			value: formatEngineCoverageValue(overview.coverage.overview_metric_engines),
		},
	];
}

function buildOverviewEngineSummaries(
	overview: OverviewResponse,
): readonly DashboardReadout[] {
	return overview.summary.engines.map((summary) => ({
		detail:
			summary.unhealthy_instances > 0
				? `${summary.unhealthy_instances} unhealthy instances are visible in this window.`
				: "No unhealthy instances are visible in this window.",
		title: formatDatabaseEngine(summary.engine),
		value: `${summary.healthy_instances}/${summary.total_instances} healthy`,
	}));
}

function buildCoverageBoundaryInsight(overview: OverviewResponse): CapacityInsight {
	return {
		detail: `Fleet health covers ${formatEngineCoverageValue(overview.coverage.fleet_health_engines)}, while cards and signal leaders currently reflect ${formatEngineCoverageValue(overview.coverage.overview_metric_engines)} coverage.`,
		title: "Coverage boundary",
		tone: "watch",
		value: "Metrics scoped",
	};
}

function hasOverviewMetricCoverage(overview: OverviewResponse): boolean {
	return overview.coverage.overview_metric_engines.length > 0;
}

function hasPartialOverviewMetricCoverage(overview: OverviewResponse): boolean {
	if (!hasOverviewMetricCoverage(overview)) {
		return false;
	}
	const metricEngines = new Set(overview.coverage.overview_metric_engines);
	const fleetHealthEngines = new Set(overview.coverage.fleet_health_engines);
	if (metricEngines.size !== fleetHealthEngines.size) {
		return true;
	}
	for (const engine of fleetHealthEngines) {
		if (!metricEngines.has(engine)) {
			return true;
		}
	}
	return false;
}

function getOverviewMetricInstances(
	overview: OverviewResponse,
): readonly OverviewResponse["instances"][number][] {
	const metricEngines = new Set(overview.coverage.overview_instance_metric_engines);
	return overview.instances.filter((instance) => metricEngines.has(instance.engine));
}

function formatEngineCoverageValue(
	engines: readonly InstanceResponse["engine"][],
): string {
	if (engines.length === 0) {
		return "Not yet available";
	}
	return formatEngineList(engines);
}

function formatEngineList(engines: readonly InstanceResponse["engine"][]): string {
	const uniqueEngines = Array.from(new Set(engines));
	if (uniqueEngines.length === 0) {
		return "None";
	}
	if (uniqueEngines.length === 1) {
		return formatDatabaseEngine(uniqueEngines[0]);
	}
	return uniqueEngines.map((engine) => formatDatabaseEngine(engine)).join(" + ");
}

export function formatDatabaseEngine(engine: InstanceResponse["engine"]): string {
	return engine === "oracle" ? "Oracle" : "MySQL";
}

function buildLeader(
	options: {
		readonly detail: string;
		readonly instance: OverviewResponse["instances"][number] | null;
		readonly title: string;
		readonly unit: string;
		readonly valueSelector: (instance: OverviewResponse["instances"][number]) => number;
	},
): CapacityLeader | null {
	if (options.instance === null) {
		return null;
	}
	return {
		detail: options.detail,
		instanceName: options.instance.name,
		title: options.title,
		value: formatMetricValue(options.valueSelector(options.instance), options.unit),
	};
}

function selectTopInstance(
	instances: readonly OverviewResponse["instances"][number][],
	selector: (instance: OverviewResponse["instances"][number]) => number,
): OverviewResponse["instances"][number] | null {
	return instances.reduce<OverviewResponse["instances"][number] | null>((current, instance) => {
		if (current === null || selector(instance) > selector(current)) {
			return instance;
		}
		return current;
	}, null);
}

function getCardMetricValue(
	cards: readonly { readonly metric_name: string; readonly unit: string; readonly value: number }[],
	metricName: string,
): number {
	return cards.find((card) => card.metric_name === metricName)?.value ?? 0;
}

function formatMetricValue(value: number, unit: string): string {
	const formatted = new Intl.NumberFormat("en-US", {
		maximumFractionDigits: value >= 10 ? 1 : 2,
	}).format(value);
	if (unit === "seconds") {
		return `${formatted} s`;
	}
	return `${formatted} ${unit}`;
}
