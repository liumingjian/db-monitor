"use client";

import { Skeleton } from "@db-monitor/ui";
import { useEffect, useMemo, useRef } from "react";

const SPARKLINE_HEIGHT_PX = 36;
const ECHARTS_RESIZE_DEBOUNCE_MS = 120;

/**
 * ECharts 6 的最小子集，避免导入整包类型；运行时依然 `import("echarts")`。
 */
interface EChartsHandle {
	dispose: () => void;
	resize: () => void;
	setOption: (option: Record<string, unknown>) => void;
}

interface InstanceSparklineProps {
	readonly values: readonly number[] | null;
	readonly colorIndex: number;
	readonly ariaLabel: string;
	readonly emptyLabel: string;
}

/**
 * 行内 sparkline：只画 line，无 axis、无 tooltip、无 legend。
 *
 * 色值走 CSS var（`--chart-N` + `--border-hairline`），主题切换在下一次 mount/refresh 生效。
 */
export function InstanceSparkline(props: InstanceSparklineProps) {
	const { values, colorIndex, ariaLabel, emptyLabel } = props;
	const containerRef = useRef<HTMLDivElement | null>(null);
	const instanceRef = useRef<EChartsHandle | null>(null);

	const hasPoints = (values?.length ?? 0) >= 2;

	const option = useMemo(
		() => (hasPoints ? buildSparklineOption(values ?? [], colorIndex) : null),
		[hasPoints, values, colorIndex],
	);

	useEffect(() => {
		if (!hasPoints) {
			return;
		}
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
			const handle: EChartsHandle = {
				dispose: () => chart.dispose(),
				resize: () => chart.resize(),
				setOption: (next) => chart.setOption(next, { notMerge: true }),
			};
			instanceRef.current = handle;
			if (option !== null) {
				handle.setOption(option);
			}
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
	}, [hasPoints, option]);

	useEffect(() => {
		if (option === null) {
			return;
		}
		instanceRef.current?.setOption(option);
	}, [option]);

	if (!hasPoints) {
		return (
			<div
				aria-label={emptyLabel}
				className="flex items-center justify-center"
				style={{ height: SPARKLINE_HEIGHT_PX }}
			>
				<Skeleton className="h-1 w-full" rounded="sm" />
			</div>
		);
	}

	return (
		<div
			aria-label={ariaLabel}
			ref={containerRef}
			role="img"
			style={{ height: SPARKLINE_HEIGHT_PX, width: "100%" }}
		/>
	);
}

function buildSparklineOption(
	values: readonly number[],
	colorIndex: number,
): Record<string, unknown> {
	const color = readChartVar(colorIndex);
	const splitLine = readCssVar("--border-hairline", "rgba(255,255,255,0.08)");
	return {
		animation: false,
		color: [color],
		grid: { top: 2, right: 2, bottom: 2, left: 2, containLabel: false },
		xAxis: {
			type: "category",
			show: false,
			boundaryGap: false,
			data: values.map((_, index) => String(index)),
		},
		yAxis: {
			type: "value",
			show: false,
			splitLine: { show: false, lineStyle: { color: splitLine } },
		},
		series: [
			{
				type: "line",
				smooth: true,
				symbol: "none",
				lineStyle: { width: 1.5 },
				areaStyle: { opacity: 0.2 },
				data: values.map((value) => value),
			},
		],
	};
}

const SPARK_FALLBACK_COLORS: readonly string[] = [
	"#5ea8ff",
	"#3ddcca",
	"#ffb547",
	"#ff5a67",
	"#c084fc",
	"#f472b6",
	"#a3e635",
	"#38bdf8",
];

function readChartVar(colorIndex: number): string {
	const safeIndex = (((colorIndex - 1) % 8) + 8) % 8;
	const fallback = SPARK_FALLBACK_COLORS[safeIndex] ?? "#5ea8ff";
	return readCssVar(`--chart-${safeIndex + 1}`, fallback);
}

function readCssVar(name: string, fallback: string): string {
	if (typeof window === "undefined") {
		return fallback;
	}
	const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
	return raw.length > 0 ? raw : fallback;
}
