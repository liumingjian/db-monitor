import type {
	AlertRecordResponse,
	InstanceResponse,
	InstanceTrendResponse,
	NotifyHistoryResponse,
} from "@db-monitor/api-client";
import { describe, expect, it } from "vitest";

import { buildInstanceAuditFeed } from "../src/components/instance-detail/audit-feed";
import { buildInstanceQuickMetricItems } from "../src/components/instance-detail/instance-metrics";
import { buildInstanceTabs } from "../src/components/instance-detail/instance-tabs";

const BASE_INSTANCE: InstanceResponse = {
	connection: {
		database: "dbmon",
		host: "10.0.0.4",
		port: 3306,
		username: "monitor",
	},
	created_at: "2026-04-20T08:00:00Z",
	engine: "mysql",
	environment: "prod",
	instance_id: "inst-1",
	labels: ["oltp"],
	name: "prod-primary",
	validation: {
		checked_at: "2026-04-23T08:00:00Z",
		detail: "",
		server_version: "8.0.36",
		status: "passed",
	},
};

const BASE_TREND: InstanceTrendResponse = {
	bucket_seconds: 60,
	cards: [
		{ label: "CPU", metric_name: "mysql_cpu_utilization", unit: "%", value: 42.5 },
		{ label: "Conns", metric_name: "mysql_threads_connected", unit: "", value: 128 },
		{ label: "QPS", metric_name: "mysql_queries_per_second", unit: "", value: 2450 },
		{
			label: "Slow",
			metric_name: "mysql_slow_queries_per_second",
			unit: "",
			value: 0.25,
		},
		{
			label: "Lag",
			metric_name: "mysql_replication_lag_seconds",
			unit: "s",
			value: 0,
		},
	],
	charts: [],
	generated_at: "2026-04-23T08:00:00Z",
	instance: {
		environment: "prod",
		instance_id: "inst-1",
		labels: ["oltp"],
		name: "prod-primary",
		server_role: "primary",
		server_version: "8.0.36",
		status: "active",
	},
	window: "1h",
};

describe("buildInstanceTabs", () => {
	it("emits 8 tabs in canonical order", () => {
		const tabs = buildInstanceTabs({ engine: "mysql", instanceId: "inst-1" });
		expect(tabs.map((tab) => tab.key)).toEqual([
			"overview",
			"performance",
			"sessions",
			"sql",
			"storage",
			"replication",
			"configuration",
			"audit",
		]);
	});

	it("marks replication / configuration as placeholder regardless of engine", () => {
		const mysqlTabs = buildInstanceTabs({ engine: "mysql", instanceId: "x" });
		const oracleTabs = buildInstanceTabs({ engine: "oracle", instanceId: "x" });
		for (const tabs of [mysqlTabs, oracleTabs]) {
			expect(tabs.find((tab) => tab.key === "replication")?.capability).toBe("placeholder");
			expect(tabs.find((tab) => tab.key === "configuration")?.capability).toBe("placeholder");
		}
	});

	it("downgrades storage to weak for mysql and sql to weak for oracle", () => {
		const mysqlTabs = buildInstanceTabs({ engine: "mysql", instanceId: "x" });
		const oracleTabs = buildInstanceTabs({ engine: "oracle", instanceId: "x" });
		expect(mysqlTabs.find((tab) => tab.key === "storage")?.capability).toBe("weak");
		expect(mysqlTabs.find((tab) => tab.key === "sql")?.capability).toBe("strong");
		expect(oracleTabs.find((tab) => tab.key === "storage")?.capability).toBe("strong");
		expect(oracleTabs.find((tab) => tab.key === "sql")?.capability).toBe("weak");
	});
});

describe("buildInstanceQuickMetricItems", () => {
	it("returns 6 cells mirroring trend cards for mysql", () => {
		const items = buildInstanceQuickMetricItems({
			instance: BASE_INSTANCE,
			trend: BASE_TREND,
		});
		expect(items).toHaveLength(6);
		expect(items.map((item) => item.key)).toEqual([
			"cpu",
			"connections",
			"qps",
			"slow-queries",
			"replication-lag",
			"validation",
		]);
		expect(items[0]?.value).toContain("42.5");
		expect(items[5]?.value).toBe("通过");
	});

	it("emits em-dash when trend is null (no fabricated numbers)", () => {
		const items = buildInstanceQuickMetricItems({
			instance: BASE_INSTANCE,
			trend: null,
		});
		for (const metricKey of ["cpu", "connections", "qps", "slow-queries", "replication-lag"]) {
			expect(items.find((item) => item.key === metricKey)?.value).toBe("—");
		}
	});
});

describe("buildInstanceAuditFeed", () => {
	const alertForInstance: AlertRecordResponse = {
		acknowledged_at: null,
		acknowledged_by_user_id: null,
		alert_id: "alert-1",
		current_value: 90,
		engine: "mysql",
		instance_id: "inst-1",
		last_evaluated_at: "2026-04-23T08:05:00Z",
		metric_name: "cpu",
		opened_at: "2026-04-23T08:00:00Z",
		owner_assigned_at: null,
		owner_user_id: null,
		resolved_at: null,
		rule_id: "rule-a",
		rule_name: "high-cpu",
		severity: "critical",
		status: "open",
		threshold: 80,
	};

	const alertForOther: AlertRecordResponse = {
		...alertForInstance,
		alert_id: "alert-2",
		instance_id: "inst-2",
	};

	const notifyForInstance: NotifyHistoryResponse = {
		attempt: 1,
		attempted_at: "2026-04-23T08:04:00Z",
		channel: "webhook",
		delivered_at: "2026-04-23T08:04:05Z",
		error: null,
		instance_id: "inst-1",
		organization_id: "org-1",
		rule_id: "rule-a",
		status: "delivered",
	};

	const notifyForOther: NotifyHistoryResponse = {
		...notifyForInstance,
		instance_id: "inst-3",
	};

	it("filters events by instance_id and orders descending", () => {
		const events = buildInstanceAuditFeed({
			alerts: [alertForInstance, alertForOther],
			instanceId: "inst-1",
			notifyHistory: [notifyForInstance, notifyForOther],
		});
		expect(events.map((event) => event.id)).toEqual([
			"alert:alert-1",
			"notify:rule-a:2026-04-23T08:04:00Z:1",
		]);
	});

	it("returns empty timeline when nothing matches", () => {
		const events = buildInstanceAuditFeed({
			alerts: [alertForOther],
			instanceId: "inst-1",
			notifyHistory: [notifyForOther],
		});
		expect(events).toHaveLength(0);
	});
});
