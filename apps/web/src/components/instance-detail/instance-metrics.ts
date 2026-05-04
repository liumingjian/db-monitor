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

interface CardReadout {
	readonly value: string;
	readonly unit: string;
	readonly numeric: boolean;
}

const PLACEHOLDER_READOUT: CardReadout = { value: PLACEHOLDER, unit: "", numeric: true };

export interface InstanceMetricStripInput {
	readonly instance: InstanceResponse;
	readonly trend: InstanceTrendResponse | null;
}

/**
 * Q13 规则 2：Quick Metrics Strip 5–6 cells. value/unit 拆开两个字段以便 cell
 * 渲染层把数字 mono semibold + 单位 muted 分层显示 (Quick Reference §6 Typography:
 * font-scale + number-tabular)。文本类 token (如 "通过") 标 numeric=false, 走 sans。
 */
export function buildInstanceQuickMetricItems(
	input: InstanceMetricStripInput,
): readonly QuickMetricItem[] {
	const engine = input.instance.engine;
	const mapping = engine === "oracle" ? ORACLE_METRIC_MAP : MYSQL_METRIC_MAP;
	const validation = input.instance.validation.status;

	const cpu = readCardReadout(input.trend, mapping.cpu, "%");
	const conn = readCardReadout(input.trend, mapping.connections, "");
	const qps = readCardReadout(input.trend, mapping.qps, "");
	const slow = readCardReadout(input.trend, mapping.slowQueries, "");
	const lag = readCardReadout(input.trend, mapping.replicationLag, "s");
	const validationLabel = validation === "passed" ? "通过" : validation;

	return [
		{
			hint: "采集端上报",
			key: "cpu",
			label: "CPU",
			value: cpu.value,
			unit: cpu.unit,
			numeric: cpu.numeric,
		},
		{
			hint: engine === "oracle" ? "活跃会话" : "并发连接",
			key: "connections",
			label: engine === "oracle" ? "活跃会话" : "连接数",
			value: conn.value,
			unit: conn.unit,
			numeric: conn.numeric,
		},
		{
			hint: "每秒语句数",
			key: "qps",
			label: "QPS",
			value: qps.value,
			unit: qps.unit,
			numeric: qps.numeric,
		},
		{
			hint: engine === "oracle" ? "长运行会话" : "慢查询 / 秒",
			key: "slow-queries",
			label: engine === "oracle" ? "长运行" : "慢查询",
			value: slow.value,
			unit: slow.unit,
			numeric: slow.numeric,
		},
		{
			hint: engine === "oracle" ? "Standby 延迟" : "从库延迟",
			key: "replication-lag",
			label: "复制延迟",
			value: lag.value,
			unit: lag.unit,
			numeric: lag.numeric,
		},
		{
			hint: "实例连接校验",
			key: "validation",
			label: "校验",
			numeric: false,
			value: validationLabel,
		},
	];
}

function readCardReadout(
	trend: InstanceTrendResponse | null,
	metricName: string,
	unitSuffix: string,
): CardReadout {
	if (trend === null) {
		return PLACEHOLDER_READOUT;
	}
	const card = trend.cards.find((entry) => entry.metric_name === metricName);
	if (card === undefined) {
		return PLACEHOLDER_READOUT;
	}
	const rawValue = card.value;
	if (!Number.isFinite(rawValue)) {
		return PLACEHOLDER_READOUT;
	}
	return {
		value: formatCardNumber(rawValue),
		unit: unitSuffix.length > 0 ? unitSuffix : (card.unit ?? ""),
		numeric: true,
	};
}

function formatCardNumber(value: number): string {
	if (Math.abs(value) >= 1000) {
		return value.toLocaleString("en-US", { maximumFractionDigits: 0 });
	}
	return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
}
