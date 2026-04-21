"use client";

import type { MetricSeriesResponse } from "@db-monitor/api-client";
import * as echarts from "echarts";
import { useEffect, useRef } from "react";

interface MetricChartProps {
	readonly emptyState: string;
	readonly series: readonly MetricSeriesResponse[];
	readonly title: string;
}

export function MetricChart({ emptyState, series, title }: MetricChartProps) {
	const containerRef = useRef<HTMLDivElement | null>(null);
	useEffect(() => {
		if (containerRef.current === null || series.length === 0) {
			return;
		}
		const chart = echarts.init(containerRef.current);
		chart.setOption(buildChartOption(title, series));
		const handleResize = () => chart.resize();
		window.addEventListener("resize", handleResize);
		return () => {
			window.removeEventListener("resize", handleResize);
			chart.dispose();
		};
	}, [series, title]);

	if (series.every((entry) => entry.points.length === 0)) {
		return <p className="text-sm text-[var(--muted)]">{emptyState}</p>;
	}
	return <div className="h-80 w-full" ref={containerRef} />;
}

function buildChartOption(
	title: string,
	series: readonly MetricSeriesResponse[],
): echarts.EChartsOption {
	return {
		grid: { bottom: 28, left: 40, right: 20, top: 24 },
		legend: { top: 0 },
		series: series.map((entry) => ({
			data: entry.points.map((point) => point.value),
			name: entry.label,
			smooth: true,
			type: "line",
		})),
		textStyle: { fontFamily: "IBM Plex Sans" },
		title: { left: "center", text: title, textStyle: { fontSize: 14, fontWeight: 600 } },
		tooltip: { trigger: "axis" },
		xAxis: {
			boundaryGap: false,
			data: series[0]?.points.map((point) => formatTimestamp(point.timestamp)) ?? [],
			type: "category",
		},
		yAxis: { scale: true, type: "value" },
	};
}

function formatTimestamp(value: string): string {
	return new Date(value).toLocaleTimeString("en-US", {
		hour: "2-digit",
		minute: "2-digit",
	});
}
