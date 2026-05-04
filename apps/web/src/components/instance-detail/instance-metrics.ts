import type { InstanceResponse, InstanceTrendResponse } from "@db-monitor/api-client";
import type { QuickMetricItem } from "@db-monitor/ui";

const MYSQL_METRIC_MAP: Readonly<Record<string, string>> = {
	cpu: "mysql_cpu_utilization",
	connections: "mysql_threads_connected",
	qps: "mysql_queries_per_second",
	slowQueries: "mysql_slow_queries_per_second",
	replicationLag: "mysql_replication_lag_seconds",
};

const ORACLE_METRIC_MAP: Readonly<Record<string, string>> = {
	cpu: "oracle_cpu_utilization",
	connections: "oracle_sessions_active",
	qps: "oracle_executions_per_second",
	slowQueries: "oracle_long_running_sessions",
	replicationLag: "oracle_standby_lag_seconds",
};

const PLACEHOLDER = "—";

export interface InstanceMetricStripInput {
	readonly instance: InstanceResponse;
	readonly trend: InstanceTrendResponse | null;
}

/**
 * Q13 规则 2：Quick Metrics Strip 5–6 cells。若 trend 缺失或 metric 未上报，
 * 显示 `—` + hint，不伪造数值。
 */
export function buildInstanceQuickMetricItems(
	input: InstanceMetricStripInput,
): readonly QuickMetricItem[] {
	const engine = input.instance.engine;
	const mapping = engine === "oracle" ? ORACLE_METRIC_MAP : MYSQL_METRIC_MAP;
	const validation = input.instance.validation.status;
	return [
		{
			hint: "采集端上报的 CPU 使用率",
			key: "cpu",
			label: "CPU",
			value: readCardValue(input.trend, mapping.cpu, "%"),
		},
		{
			hint: engine === "oracle" ? "活跃会话" : "并发连接",
			key: "connections",
			label: engine === "oracle" ? "活跃会话" : "连接数",
			value: readCardValue(input.trend, mapping.connections, ""),
		},
		{
			hint: "每秒语句数",
			key: "qps",
			label: "QPS",
			value: readCardValue(input.trend, mapping.qps, ""),
		},
		{
			hint: engine === "oracle" ? "长运行会话" : "慢查询 / 秒",
			key: "slow-queries",
			label: engine === "oracle" ? "长运行" : "慢查询",
			value: readCardValue(input.trend, mapping.slowQueries, ""),
		},
		{
			hint: engine === "oracle" ? "Standby 延迟" : "从库延迟",
			key: "replication-lag",
			label: "复制延迟",
			value: readCardValue(input.trend, mapping.replicationLag, "s"),
		},
		{
			hint: "实例连接校验状态",
			key: "validation",
			label: "校验",
			value: validation === "passed" ? "通过" : validation,
		},
	];
}

function readCardValue(
	trend: InstanceTrendResponse | null,
	metricName: string,
	unitSuffix: string,
): string {
	if (trend === null) {
		return PLACEHOLDER;
	}
	const card = trend.cards.find((entry) => entry.metric_name === metricName);
	if (card === undefined) {
		return PLACEHOLDER;
	}
	const rawValue = card.value;
	if (!Number.isFinite(rawValue)) {
		return PLACEHOLDER;
	}
	const formatted = formatCardNumber(rawValue);
	if (unitSuffix.length === 0) {
		return `${formatted}${card.unit ? ` ${card.unit}` : ""}`.trim();
	}
	return `${formatted} ${unitSuffix}`;
}

function formatCardNumber(value: number): string {
	if (Math.abs(value) >= 1000) {
		return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
	}
	return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
}
