"use client";

import type { MetricSeriesResponse } from "@db-monitor/api-client";
import { Skeleton } from "@db-monitor/ui";
import { useEffect, useMemo, useRef } from "react";

import { readChartPalette } from "./overview-chart-palette";

const CHART_HEIGHT_PX = 220;
const ECHARTS_RESIZE_DEBOUNCE_MS = 120;

interface OverviewLineChartProps {
	readonly title: string;
	readonly series: MetricSeriesResponse | undefined;
	readonly colorIndex: number;
	readonly emptyLabel: string;
	readonly unitLabel?: string;
}

/**
 * Minimal ECharts line chart for Overview's 8 chart slots.
 *
 * - Colors come from CSS vars (`--chart-N` + `--fg-*` + `--border-*`); no hex hardcoding.
 * - ECharts is dynamically imported on mount to avoid SSR bundle bloat.
 * - Resize observer keeps chart responsive inside grid.
 */
export function OverviewLineChart(props: OverviewLineChartProps) {
	const { title, series, colorIndex, emptyLabel, unitLabel } = props;
	const containerRef = useRef<HTMLDivElement | null>(null);
	const instanceRef = useRef<{
		dispose: () => void;
		resize: () => void;
		setOption: (option: Record<string, unknown>) => void;
	} | null>(null);

	const option = useMemo(
		() => buildLineChartOption({ colorIndex, series, unitLabel }),
		[colorIndex, series, unitLabel],
	);

	const latestOptionRef = useRef(option);

	// Mount: init ECharts instance + resize observer. Setup is idempotent and depends
	// on no reactive inputs; the `option` effect below pushes the latest config every render.
	useEffect(() => {
		let cancelled = false;
		const element = containerRef.current;
		if (!element) {
			return;
		}

		(async () => {
			const echartsModule = await import("echarts");
			if (cancelled || !containerRef.current) {
				return;
			}
			const chart = echartsModule.init(containerRef.current, undefined, {
				renderer: "canvas",
			});
			instanceRef.current = {
				dispose: () => {
					chart.dispose();
				},
				resize: () => {
					chart.resize();
				},
				setOption: (next) => {
					chart.setOption(next, { notMerge: true });
				},
			};
			// Push the current option snapshot immediately so the first paint matches data.
			instanceRef.current.setOption(latestOptionRef.current);
		})();

		let resizeTimer: ReturnType<typeof setTimeout> | null = null;
		const scheduleResize = () => {
			if (resizeTimer !== null) {
				clearTimeout(resizeTimer);
			}
			resizeTimer = setTimeout(() => {
				instanceRef.current?.resize();
			}, ECHARTS_RESIZE_DEBOUNCE_MS);
		};
		const observer = new ResizeObserver(scheduleResize);
		observer.observe(element);

		return () => {
			cancelled = true;
			observer.disconnect();
			if (resizeTimer !== null) {
				clearTimeout(resizeTimer);
			}
			instanceRef.current?.dispose();
			instanceRef.current = null;
		};
	}, []);

	useEffect(() => {
		latestOptionRef.current = option;
		instanceRef.current?.setOption(option);
	}, [option]);

	const hasPoints = (series?.points.length ?? 0) > 0;

	return (
		<div className="flex flex-col gap-2 rounded-md border border-border-hairline bg-bg-base p-4">
			<div className="flex items-baseline justify-between gap-2">
				<h3 className="text-sm font-semibold text-fg-primary">{title}</h3>
				{unitLabel ? (
					<span className="font-mono text-xs text-fg-muted tabular-nums">{unitLabel}</span>
				) : null}
			</div>
			{hasPoints ? (
				<div ref={containerRef} style={{ height: CHART_HEIGHT_PX, width: "100%" }} />
			) : (
				<div
					className="flex flex-col items-center justify-center gap-2 rounded-sm bg-bg-elevated"
					style={{ height: CHART_HEIGHT_PX }}
				>
					<Skeleton className="h-3 w-40" />
					<p className="text-xs text-fg-muted">{emptyLabel}</p>
				</div>
			)}
		</div>
	);
}

interface BuildOptionArgs {
	readonly colorIndex: number;
	readonly series: MetricSeriesResponse | undefined;
	readonly unitLabel?: string;
}

function buildLineChartOption(args: BuildOptionArgs): Record<string, unknown> {
	const { colorIndex, series, unitLabel } = args;
	const palette = readChartPalette();
	const color =
		palette.colors[(colorIndex - 1) % palette.colors.length] ?? palette.colors[0] ?? "#5ea8ff";
	const data = (series?.points ?? []).map((point) => [point.timestamp, point.value] as const);

	return {
		animation: false,
		color: [color],
		grid: { top: 16, right: 16, bottom: 28, left: 44 },
		tooltip: {
			trigger: "axis",
			backgroundColor: palette.tooltipBg,
			borderColor: palette.tooltipBorder,
			borderWidth: 1,
			textStyle: { color: palette.tooltipText, fontSize: 12 },
			axisPointer: { type: "line", lineStyle: { color: palette.axisLine } },
		},
		xAxis: {
			type: "time",
			axisLine: { lineStyle: { color: palette.axisLine } },
			axisTick: { show: false },
			axisLabel: {
				color: palette.axisLabel,
				fontSize: 11,
				hideOverlap: true,
				margin: 8,
				formatter: {
					year: "{yyyy}",
					month: "{MMM}",
					day: "{MM}-{dd}",
					hour: "{HH}:{mm}",
					minute: "{HH}:{mm}",
					second: "{HH}:{mm}:{ss}",
					millisecond: "{HH}:{mm}:{ss}",
					none: "{HH}:{mm}",
				},
			},
			splitLine: { show: false },
		},
		yAxis: {
			type: "value",
			name: unitLabel,
			nameTextStyle: { color: palette.axisLabel, fontSize: 11, padding: [0, 0, 0, -36] },
			axisLine: { show: false },
			axisLabel: { color: palette.axisLabel, fontSize: 11 },
			splitLine: { lineStyle: { color: palette.splitLine, type: "dashed" } },
		},
		series: [
			{
				type: "line",
				smooth: true,
				showSymbol: false,
				lineStyle: { width: 2 },
				areaStyle: { opacity: 0.18 },
				data,
			},
		],
	};
}
