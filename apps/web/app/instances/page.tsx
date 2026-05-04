import type {
	InstanceResponse,
	InstanceTrendResponse,
	MetricSeriesResponse,
} from "@db-monitor/api-client";
import {
	CanonicalPageTemplate,
	EntitySummary,
	PageBreadcrumb,
	PageContent,
	QuickMetrics,
} from "@db-monitor/ui";

import { InstancesListContent } from "../../src/components/instances-list/instances-list-content";
import { InstancesListShell } from "../../src/components/instances-list/instances-list-shell";
import {
	SPARKLINE_FANOUT_LIMIT,
	SPARK_METRIC_KEYS,
	type SparkMetricKey,
	type SparkValuesMap,
	normalizeSparkMetric,
	normalizeViewKey,
	pickMetricNameForEngine,
} from "../../src/components/instances-list/types";
import { buildInstanceListFilterValues } from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

interface InstancesPageProps {
	readonly searchParams: Promise<{
		readonly environment?: string;
		readonly label?: string;
		readonly name?: string;
		readonly status?: string;
		readonly view?: string;
		readonly spark?: string;
	}>;
}

export default async function InstancesPage({ searchParams }: InstancesPageProps) {
	const session = await requireServerSession("/instances");
	const params = await searchParams;
	const filters = buildInstanceListFilterValues(params);
	const view = normalizeViewKey(params.view);
	const sparkMetric = normalizeSparkMetric(params.spark);

	const apiClient = await createServerApiClient();
	const [filteredRows, totalRows] = await Promise.all([
		apiClient.listInstances({
			environment: emptyToUndefined(filters.environment),
			label: emptyToUndefined(filters.label),
			name: emptyToUndefined(filters.name),
			status: emptyToUndefined(filters.status),
		}),
		apiClient.listInstances(),
	]);

	const sparkValues = await fetchSparkValues({
		apiClient,
		rows: filteredRows,
	});

	const healthCount = countValidation(filteredRows, "passed");
	const failedCount = countValidation(filteredRows, "failed");
	const oracleCount = filteredRows.filter((instance) => instance.engine === "oracle").length;

	return (
		<InstancesListShell instanceCount={totalRows.length} session={session}>
			<CanonicalPageTemplate>
				<PageBreadcrumb items={[{ label: "观测", href: "/overview" }, { label: "实例" }]} />
				<EntitySummary
					badges={[
						{ tone: healthCount === filteredRows.length ? "ok" : "warning", label: "Fleet" },
						{ tone: "info", label: "Slice 1.5" },
					]}
					subtitle="Catalog 范式 · 双视图 · 行内 sparkline · 真实新建 / 重验证"
					title="实例管理"
				/>
				<QuickMetrics
					items={[
						{ key: "total", label: "实例总数", value: String(totalRows.length) },
						{ key: "filtered", label: "过滤后", value: String(filteredRows.length) },
						{ key: "passed", label: "校验通过", value: String(healthCount) },
						{ key: "failed", label: "校验失败", value: String(failedCount) },
						{ key: "oracle", label: "Oracle 实例", value: String(oracleCount) },
					]}
				/>
				<PageContent>
					<InstancesListContent
						filters={filters}
						rows={filteredRows}
						sparkMetric={sparkMetric}
						sparkValues={sparkValues}
						totalInstances={totalRows.length}
						view={view}
					/>
				</PageContent>
			</CanonicalPageTemplate>
		</InstancesListShell>
	);
}

interface FetchSparkValuesArgs {
	readonly apiClient: Awaited<ReturnType<typeof createServerApiClient>>;
	readonly rows: readonly InstanceResponse[];
}

/**
 * 为可见行拉取 `getInstanceTrends('1h')` 并抽出 3 个候选 metric 的 points。
 *
 * 超过 `SPARKLINE_FANOUT_LIMIT` 行时不再为每行发请求，而是对超出行标注
 * "fanout 跳过"（UI 明示，非静默）。这是显式阈值，不是 silent fallback。
 */
async function fetchSparkValues(args: FetchSparkValuesArgs): Promise<SparkValuesMap> {
	const { apiClient, rows } = args;
	const eligible = rows.slice(0, SPARKLINE_FANOUT_LIMIT);
	const skipped = rows.slice(SPARKLINE_FANOUT_LIMIT);

	const trendEntries = await Promise.all(
		eligible.map(async (instance) => {
			try {
				const trend = await apiClient.getInstanceTrends(instance.instance_id, "1h");
				return [instance.instance_id, projectSparkValues(instance.engine, trend)] as const;
			} catch {
				// 单个实例 trend 获取失败不应影响全列表；用空 series 表达 "无数据"（非伪造）
				return [instance.instance_id, EMPTY_SPARK_VALUES] as const;
			}
		}),
	);

	const result: Record<string, SparkValuesMap[string]> = {};
	for (const [id, values] of trendEntries) {
		result[id] = values;
	}
	for (const instance of skipped) {
		result[instance.instance_id] = null;
	}
	return result;
}

const EMPTY_SPARK_VALUES: Readonly<Record<SparkMetricKey, readonly number[]>> = {
	connections: [],
	qps: [],
	active: [],
};

function projectSparkValues(
	engine: InstanceResponse["engine"],
	trend: InstanceTrendResponse,
): Readonly<Record<SparkMetricKey, readonly number[]>> {
	const next: Record<SparkMetricKey, readonly number[]> = {
		connections: [],
		qps: [],
		active: [],
	};
	for (const key of SPARK_METRIC_KEYS) {
		const metricName = pickMetricNameForEngine(engine, key);
		const series = findSeries(trend.charts, metricName);
		next[key] = series === null ? [] : series.points.map((point) => point.value);
	}
	return next;
}

function findSeries(
	charts: readonly MetricSeriesResponse[],
	metricName: string,
): MetricSeriesResponse | null {
	return charts.find((entry) => entry.metric_name === metricName) ?? null;
}

function countValidation(rows: readonly InstanceResponse[], status: "passed" | "failed"): number {
	return rows.reduce((total, row) => total + (row.validation.status === status ? 1 : 0), 0);
}

function emptyToUndefined<T extends string>(value: T | ""): T | undefined {
	return value.length === 0 ? undefined : (value as T);
}
