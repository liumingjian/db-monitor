"use client";

/**
 * Chart palette & theme tokens for Overview ECharts instances.
 *
 * 严格遵守 ADR-0012：ECharts 不允许硬编码颜色。每次渲染 / 每次 auto-refresh 重新读取
 * CSS var，使得主题切换（data-theme="dark" -> "light"）在下一次挂载/刷新时立即生效。
 */

const CHART_VAR_NAMES = [
	"--chart-1",
	"--chart-2",
	"--chart-3",
	"--chart-4",
	"--chart-5",
	"--chart-6",
	"--chart-7",
	"--chart-8",
] as const;

const THEME_VAR_NAMES = {
	fgPrimary: "--fg-primary",
	fgSecondary: "--fg-secondary",
	fgMuted: "--fg-muted",
	borderHairline: "--border-hairline",
	borderSubtle: "--border-subtle",
	bgElevated: "--bg-elevated",
} as const;

export interface OverviewChartPalette {
	readonly colors: readonly string[];
	readonly axisLabel: string;
	readonly axisLine: string;
	readonly splitLine: string;
	readonly tooltipBg: string;
	readonly tooltipBorder: string;
	readonly tooltipText: string;
	readonly legendText: string;
}

function readVar(name: string, fallback: string): string {
	if (typeof window === "undefined") {
		return fallback;
	}
	const root = document.documentElement;
	const raw = getComputedStyle(root).getPropertyValue(name).trim();
	return raw.length > 0 ? raw : fallback;
}

/** Read chart colors + axis tokens from the current CSS var cascade. */
export function readChartPalette(): OverviewChartPalette {
	const colors = CHART_VAR_NAMES.map((name, index) =>
		readVar(name, FALLBACK_COLORS[index] ?? "#5ea8ff"),
	);
	return {
		colors,
		axisLabel: readVar(THEME_VAR_NAMES.fgMuted, "#94a3b8"),
		axisLine: readVar(THEME_VAR_NAMES.borderHairline, "rgba(255,255,255,0.08)"),
		splitLine: readVar(THEME_VAR_NAMES.borderHairline, "rgba(255,255,255,0.08)"),
		tooltipBg: readVar(THEME_VAR_NAMES.bgElevated, "#1c2029"),
		tooltipBorder: readVar(THEME_VAR_NAMES.borderSubtle, "rgba(255,255,255,0.12)"),
		tooltipText: readVar(THEME_VAR_NAMES.fgPrimary, "#f8fafc"),
		legendText: readVar(THEME_VAR_NAMES.fgSecondary, "#cbd5e1"),
	};
}

/** Pick a single chart color by its 1-based index (1..8). Wraps if OOB. */
export function pickChartColor(index1Based: number): string {
	const palette = readChartPalette();
	const safe =
		(((index1Based - 1) % palette.colors.length) + palette.colors.length) % palette.colors.length;
	return palette.colors[safe] ?? "#5ea8ff";
}

// SSR fallback only (first paint before hydration). Aligned with dark-theme tokens.
const FALLBACK_COLORS: readonly string[] = [
	"#5ea8ff",
	"#3ddcca",
	"#ffb547",
	"#ff5a67",
	"#c084fc",
	"#f472b6",
	"#a3e635",
	"#38bdf8",
];
