"use client";

import { useEffect, useRef } from "react";
import type { TablespaceHistoryEntryResponse } from "@db-monitor/api-client";
import * as echarts from "echarts";

import { HISTORY_ALERT_LINE_PERCENT } from "../../../../src/tablespaces-ui";

interface TablespaceTrendChartProps {
	readonly history: readonly TablespaceHistoryEntryResponse[];
	readonly tablespaceName: string;
}

export function TablespaceTrendChart({ history, tablespaceName }: TablespaceTrendChartProps) {
	const containerRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		const container = containerRef.current;
		if (container === null) {
			return;
		}
		const instance = echarts.init(container);
		instance.setOption(buildChartOption({ history, tablespaceName }));
		const handleResize = () => instance.resize();
		window.addEventListener("resize", handleResize);
		return () => {
			window.removeEventListener("resize", handleResize);
			instance.dispose();
		};
	}, [history, tablespaceName]);

	return <div aria-label={`${tablespaceName} 30 天使用率趋势`} className="h-96 w-full" ref={containerRef} />;
}

interface ChartOptionInput {
	readonly history: readonly TablespaceHistoryEntryResponse[];
	readonly tablespaceName: string;
}

function buildChartOption(input: ChartOptionInput): echarts.EChartsOption {
	const points = input.history.map((entry) => [
		entry.collected_at,
		Number(entry.used_rate_percent.toFixed(2)),
	]);
	return {
		title: {
			left: "left",
			text: `${input.tablespaceName} 30 天使用率`,
			textStyle: { fontSize: 14 },
		},
		tooltip: { trigger: "axis" },
		xAxis: { type: "time" },
		yAxis: { max: 100, min: 0, name: "%", type: "value" },
		series: [
			{
				areaStyle: { opacity: 0.15 },
				data: points,
				lineStyle: { width: 2 },
				markLine: {
					data: [
						{
							label: { formatter: "95% 阈值" },
							lineStyle: { color: "#ef4444" },
							yAxis: HISTORY_ALERT_LINE_PERCENT,
						},
					],
					silent: true,
					symbol: "none",
				},
				name: "使用率",
				smooth: true,
				type: "line",
			},
		],
	};
}
