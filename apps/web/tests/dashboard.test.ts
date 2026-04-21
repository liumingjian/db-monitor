import { describe, expect, it } from "vitest";

import { buildDashboardModel } from "../src/monitoring-ui";
import { PREVIEW_OVERVIEW } from "../src/monitoring-preview";

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
					...PREVIEW_OVERVIEW.instances[0],
					engine: "oracle",
					instance_id: "inst-prod-oracle",
					name: "prod-oracle-primary",
					qps: 0,
					replication_lag_seconds: 0,
					threads_connected: 0,
					threads_running: 0,
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
		expect(model.engineSummaries.map((summary) => summary.title)).toEqual([
			"MySQL",
			"Oracle",
		]);
	});
});
