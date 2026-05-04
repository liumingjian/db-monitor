import type { InstanceResponse } from "@db-monitor/api-client";

export const SPARK_METRIC_KEYS = ["connections", "qps", "active"] as const;
export type SparkMetricKey = (typeof SPARK_METRIC_KEYS)[number];

export const DEFAULT_SPARK_METRIC: SparkMetricKey = "connections";

export const VIEW_KEYS = ["table", "grid"] as const;
export type InstancesViewKey = (typeof VIEW_KEYS)[number];

export const DEFAULT_VIEW: InstancesViewKey = "table";

/**
 * 行内 sparkline 并发上限：超过该阈值不再为每行拉取 trend（避免首屏 N 次网络放大）。
 * 在 UI 上要显式告知用户，而非静默降级。
 */
export const SPARKLINE_FANOUT_LIMIT = 30;

/**
 * 每行 sparkline 数据：Record<instance_id, Record<SparkMetricKey, number[]>>。
 * 为 null 表示该行被 fanout 限流跳过。
 */
export type SparkValuesMap = Readonly<
	Record<string, Readonly<Record<SparkMetricKey, readonly number[]>> | null>
>;

export interface SparkMetricMapping {
	readonly mysql: string;
	readonly oracle: string;
}

/**
 * Slice 1 后端暴露的 metric 名称；CPU 在 Slice 1 不可用，故本页不提供 CPU 选项。
 */
export const SPARK_METRIC_MAPPING: Readonly<Record<SparkMetricKey, SparkMetricMapping>> = {
	connections: {
		mysql: "mysql_threads_connected",
		oracle: "oracle_sessions_total",
	},
	qps: {
		mysql: "mysql_queries_per_second",
		oracle: "oracle_user_calls_per_second",
	},
	active: {
		mysql: "mysql_threads_running",
		oracle: "oracle_sessions_active",
	},
};

export function normalizeSparkMetric(value: string | undefined): SparkMetricKey {
	return SPARK_METRIC_KEYS.includes(value as SparkMetricKey)
		? (value as SparkMetricKey)
		: DEFAULT_SPARK_METRIC;
}

export function normalizeViewKey(value: string | undefined): InstancesViewKey {
	return VIEW_KEYS.includes(value as InstancesViewKey) ? (value as InstancesViewKey) : DEFAULT_VIEW;
}

export function pickMetricNameForEngine(
	engine: InstanceResponse["engine"],
	metric: SparkMetricKey,
): string {
	const mapping = SPARK_METRIC_MAPPING[metric];
	return engine === "oracle" ? mapping.oracle : mapping.mysql;
}
