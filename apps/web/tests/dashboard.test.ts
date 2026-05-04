import { describe, expect, it } from "vitest";

import { PREVIEW_OVERVIEW } from "../src/monitoring-preview";
import { buildDashboardModel } from "../src/monitoring-ui";

describe("dashboard views", () => {
	it("maps overview cards and chart series into dashboard sections", () => {
		const model = buildDashboardModel();

		expect(model.chartFrame.title).toBe("Fleet Activity");
		expect(model.heroMetrics.map((metric) => metric.label)).toEqual([
			"Threads Connected",
			"Threads Running",
			"QPS",
			"Inbound Throughput",
			"Outbound Throughput",
			"Buffer Pool Reads",
			"Replication Lag",
		]);
		expect(model.chartSeries).toEqual([
			"mysql_threads_connected",
			"mysql_threads_running",
			"mysql_queries_per_second",
			"mysql_bytes_received_per_second",
			"mysql_bytes_sent_per_second",
			"mysql_innodb_buffer_pool_reads_per_second",
			"mysql_replication_lag_seconds",
		]);
		expect(model.capacityInsights.map((insight) => insight.title)).toEqual([
			"Traffic direction",
			"Engine pressure",
			"Replica headroom",
		]);
		expect(model.capacityInsights.map((insight) => insight.value)).toEqual([
			"Serving-heavy",
			"Watch cache misses",
			"Replica lag risk",
		]);
		expect(model.capacityLeaders.map((leader) => leader.title)).toEqual([
			"Highest QPS",
			"Most Running Threads",
			"Worst Replication Lag",
		]);
		expect(model.capabilityBoundary.value).toBe("Fleet metrics available");
		expect(model.coverageReadout.map((readout) => readout.value)).toEqual([
			"MySQL",
			"MySQL",
			"MySQL",
		]);
		expect(model.engineSummaries).toEqual([
			{
				detail: "No unhealthy instances are visible in this window.",
				title: "MySQL",
				value: "1/1 healthy",
			},
		]);
	});

	it("surfaces mixed-engine coverage boundaries without pretending parity", () => {
		const model = buildDashboardModel({
			...PREVIEW_OVERVIEW,
			coverage: {
				detail_analytics_engines: ["mysql", "oracle"],
				fleet_health_engines: ["mysql", "oracle"],
				overview_instance_metric_engines: ["mysql"],
				overview_metric_engines: ["mysql"],
			},
			instances: [
				...PREVIEW_OVERVIEW.instances,
				{
					environment: "prod",
					engine: "oracle",
					instance_id: "inst-prod-oracle",
					labels: ["oracle", "baseline"],
					metrics: [],
					name: "prod-oracle-primary",
					status: "healthy",
				},
			],
			summary: {
				engines: [
					{
						engine: "mysql",
						healthy_instances: 1,
						total_instances: 1,
						unhealthy_instances: 0,
					},
					{
						engine: "oracle",
						healthy_instances: 1,
						total_instances: 1,
						unhealthy_instances: 0,
					},
				],
				healthy_instances: 2,
				total_instances: 2,
				unhealthy_instances: 0,
			},
		});

		expect(model.capabilityBoundary.value).toBe("Mixed-engine baseline");
		expect(model.chartFrame.title).toBe("MySQL Fleet Activity");
		expect(model.heroMetrics.map((metric) => metric.label)).toContain("MySQL QPS");
		expect(model.capacityInsights.map((insight) => insight.title)).toEqual([
			"MySQL traffic direction",
			"MySQL engine pressure",
			"Coverage boundary",
		]);
		expect(model.capacityLeaders.map((leader) => leader.title)).toEqual([
			"Highest MySQL QPS",
			"Most MySQL Running Threads",
			"Worst MySQL Replication Lag",
		]);
		expect(model.coverageReadout.map((readout) => readout.value)).toEqual([
			"MySQL + Oracle",
			"MySQL + Oracle",
			"MySQL",
		]);
		expect(model.engineSummaries.map((summary) => summary.title)).toEqual(["MySQL", "Oracle"]);
	});

	it("surfaces mixed-engine fleet parity once oracle overview metrics are available", () => {
		const model = buildDashboardModel({
			...PREVIEW_OVERVIEW,
			cards: [
				...PREVIEW_OVERVIEW.cards,
				{
					label: "Sessions Total",
					metric_name: "oracle_sessions_total",
					unit: "sessions",
					value: 24,
				},
				{
					label: "Sessions Active",
					metric_name: "oracle_sessions_active",
					unit: "sessions",
					value: 6,
				},
				{
					label: "Session Waits",
					metric_name: "oracle_session_waits",
					unit: "sessions",
					value: 2,
				},
				{
					label: "User Calls",
					metric_name: "oracle_user_calls_per_second",
					unit: "calls/s",
					value: 0.2,
				},
				{
					label: "Physical Reads",
					metric_name: "oracle_physical_reads_per_second",
					unit: "reads/s",
					value: 0.1,
				},
			],
			charts: [
				...PREVIEW_OVERVIEW.charts,
				{
					label: "Sessions Total",
					metric_name: "oracle_sessions_total",
					points: [
						{ timestamp: "2026-04-19T19:45:00+08:00", value: 18 },
						{ timestamp: "2026-04-19T19:50:00+08:00", value: 24 },
					],
					unit: "sessions",
				},
				{
					label: "Sessions Active",
					metric_name: "oracle_sessions_active",
					points: [
						{ timestamp: "2026-04-19T19:45:00+08:00", value: 4 },
						{ timestamp: "2026-04-19T19:50:00+08:00", value: 6 },
					],
					unit: "sessions",
				},
				{
					label: "Session Waits",
					metric_name: "oracle_session_waits",
					points: [
						{ timestamp: "2026-04-19T19:45:00+08:00", value: 1 },
						{ timestamp: "2026-04-19T19:50:00+08:00", value: 2 },
					],
					unit: "sessions",
				},
				{
					label: "User Calls",
					metric_name: "oracle_user_calls_per_second",
					points: [
						{ timestamp: "2026-04-19T19:45:00+08:00", value: 0.1 },
						{ timestamp: "2026-04-19T19:50:00+08:00", value: 0.2 },
					],
					unit: "calls/s",
				},
				{
					label: "Physical Reads",
					metric_name: "oracle_physical_reads_per_second",
					points: [
						{ timestamp: "2026-04-19T19:45:00+08:00", value: 0.05 },
						{ timestamp: "2026-04-19T19:50:00+08:00", value: 0.1 },
					],
					unit: "reads/s",
				},
			],
			coverage: {
				detail_analytics_engines: ["mysql", "oracle"],
				fleet_health_engines: ["mysql", "oracle"],
				overview_instance_metric_engines: ["mysql", "oracle"],
				overview_metric_engines: ["mysql", "oracle"],
			},
			instances: [
				...PREVIEW_OVERVIEW.instances,
				{
					environment: "prod",
					engine: "oracle",
					instance_id: "inst-prod-oracle",
					labels: ["oracle", "baseline"],
					metrics: [
						{
							label: "Sessions Total",
							metric_name: "oracle_sessions_total",
							unit: "sessions",
							value: 24,
						},
						{
							label: "Sessions Active",
							metric_name: "oracle_sessions_active",
							unit: "sessions",
							value: 6,
						},
						{
							label: "Session Waits",
							metric_name: "oracle_session_waits",
							unit: "sessions",
							value: 2,
						},
						{
							label: "User Calls",
							metric_name: "oracle_user_calls_per_second",
							unit: "calls/s",
							value: 0.2,
						},
						{
							label: "Physical Reads",
							metric_name: "oracle_physical_reads_per_second",
							unit: "reads/s",
							value: 0.1,
						},
					],
					name: "prod-oracle-primary",
					status: "healthy",
				},
			],
			summary: {
				engines: [
					{
						engine: "mysql",
						healthy_instances: 1,
						total_instances: 1,
						unhealthy_instances: 0,
					},
					{
						engine: "oracle",
						healthy_instances: 1,
						total_instances: 1,
						unhealthy_instances: 0,
					},
				],
				healthy_instances: 2,
				total_instances: 2,
				unhealthy_instances: 0,
			},
		});

		expect(model.capabilityBoundary.value).toBe("Fleet metrics available");
		expect(model.chartFrame.title).toBe("Mixed-Engine Fleet Activity");
		expect(model.heroMetrics.map((metric) => metric.label)).toContain("MySQL QPS");
		expect(model.heroMetrics.map((metric) => metric.label)).toContain("Oracle Sessions Total");
		expect(model.capacityInsights.map((insight) => insight.title)).toEqual([
			"MySQL traffic direction",
			"MySQL engine pressure",
			"MySQL replica headroom",
			"Oracle workload direction",
			"Oracle engine pressure",
			"Oracle concurrency posture",
		]);
		expect(model.capacityLeaders.map((leader) => leader.title)).toEqual([
			"Highest MySQL QPS",
			"Most MySQL Running Threads",
			"Worst MySQL Replication Lag",
			"Highest Oracle User Calls",
			"Most Oracle Active Sessions",
			"Highest Oracle Session Waits",
		]);
		expect(model.coverageReadout.map((readout) => readout.value)).toEqual([
			"MySQL + Oracle",
			"MySQL + Oracle",
			"MySQL + Oracle",
		]);
	});
});
