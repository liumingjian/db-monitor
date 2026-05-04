/**
 * Shared display formatters for Slice 1.5 UI.
 *
 * ADR-0012 D7 mandates: thousand separators, 1 decimal for percent, SI bytes (base10) default,
 * auto-scaling durations, <24h relative / >=24h absolute for times, strict 0 vs "—" distinction.
 *
 * All functions are pure (no I/O, no globals mutated).
 */

const DEFAULT_LOCALE = "zh-CN";
const FALLBACK = "—";

const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MS_PER_SECOND = 1000;
const MS_PER_MINUTE = MS_PER_SECOND * SECONDS_PER_MINUTE;
const MS_PER_HOUR = MS_PER_MINUTE * MINUTES_PER_HOUR;
const MS_PER_DAY = MS_PER_HOUR * HOURS_PER_DAY;

const RELATIVE_THRESHOLD_JUST_NOW_MS = 60 * MS_PER_SECOND;
const RELATIVE_ABSOLUTE_SWITCH_MS = MS_PER_DAY;

const PERCENT_SCALE = 100;
const PERCENT_DEFAULT_DECIMALS = 1;

const BASE_10_STEP = 1000;
const BASE_2_STEP = 1024;

const BYTE_UNITS_SI: readonly string[] = ["B", "KB", "MB", "GB", "TB", "PB"];
const BYTE_UNITS_IEC: readonly string[] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"];

export interface FormatNumberOptions {
	readonly decimals?: number;
	readonly locale?: string;
}

export interface FormatPercentOptions {
	readonly decimals?: number;
}

export interface FormatBytesOptions {
	readonly base?: 10 | 2;
}

const isFiniteNumber = (value: unknown): value is number =>
	typeof value === "number" && Number.isFinite(value);

export function formatNumber(value: number, options: FormatNumberOptions = {}): string {
	if (!isFiniteNumber(value)) {
		return FALLBACK;
	}
	const decimals = options.decimals;
	const locale = options.locale ?? DEFAULT_LOCALE;
	const formatter = new Intl.NumberFormat(locale, {
		maximumFractionDigits: decimals ?? 20,
		minimumFractionDigits: decimals ?? 0,
	});
	return formatter.format(value);
}

export function formatPercent(
	value: number | null | undefined,
	options: FormatPercentOptions = {},
): string {
	if (value === null || value === undefined || !isFiniteNumber(value)) {
		return FALLBACK;
	}
	const decimals = options.decimals ?? PERCENT_DEFAULT_DECIMALS;
	return `${(value * PERCENT_SCALE).toFixed(decimals)}%`;
}

function pickByteUnit(
	bytes: number,
	step: number,
	units: readonly string[],
): {
	readonly value: number;
	readonly unit: string;
} {
	let remaining = bytes;
	let index = 0;
	while (remaining >= step && index < units.length - 1) {
		remaining /= step;
		index += 1;
	}
	return { unit: units[index] ?? units[units.length - 1] ?? "B", value: remaining };
}

export function formatBytes(bytes: number, options: FormatBytesOptions = {}): string {
	if (!isFiniteNumber(bytes)) {
		return FALLBACK;
	}
	if (bytes === 0) {
		return "0 B";
	}
	const base = options.base ?? 10;
	const step = base === 2 ? BASE_2_STEP : BASE_10_STEP;
	const units = base === 2 ? BYTE_UNITS_IEC : BYTE_UNITS_SI;
	const sign = bytes < 0 ? "-" : "";
	const absolute = Math.abs(bytes);
	const { unit, value } = pickByteUnit(absolute, step, units);
	const formatted = unit === "B" ? value.toString() : value.toFixed(1);
	return `${sign}${formatted} ${unit}`;
}

function formatDurationHoursMinutes(ms: number): string {
	const hours = Math.floor(ms / MS_PER_HOUR);
	const minutes = Math.floor((ms % MS_PER_HOUR) / MS_PER_MINUTE);
	return `${hours}h ${minutes}m`;
}

function formatDurationDaysHours(ms: number): string {
	const days = Math.floor(ms / MS_PER_DAY);
	const hours = Math.floor((ms % MS_PER_DAY) / MS_PER_HOUR);
	return `${days}d ${hours}h`;
}

export function formatDuration(ms: number): string {
	if (!isFiniteNumber(ms) || ms < 0) {
		return FALLBACK;
	}
	if (ms < MS_PER_SECOND) {
		return `${ms.toFixed(1)} ms`;
	}
	if (ms < MS_PER_MINUTE) {
		return `${(ms / MS_PER_SECOND).toFixed(1)} s`;
	}
	if (ms < MS_PER_HOUR) {
		return `${Math.round(ms / MS_PER_MINUTE)} min`;
	}
	if (ms < MS_PER_DAY) {
		return formatDurationHoursMinutes(ms);
	}
	return formatDurationDaysHours(ms);
}

function pad2(value: number): string {
	return value.toString().padStart(2, "0");
}

function toAbsoluteTimestamp(date: Date): string {
	const year = date.getFullYear();
	const month = pad2(date.getMonth() + 1);
	const day = pad2(date.getDate());
	const hour = pad2(date.getHours());
	const minute = pad2(date.getMinutes());
	const second = pad2(date.getSeconds());
	return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
}

function formatPastRelative(diffMs: number): string {
	if (diffMs < RELATIVE_THRESHOLD_JUST_NOW_MS) {
		return "刚刚";
	}
	if (diffMs < MS_PER_HOUR) {
		return `${Math.floor(diffMs / MS_PER_MINUTE)} 分钟前`;
	}
	return `${Math.floor(diffMs / MS_PER_HOUR)} 小时前`;
}

function formatFutureRelative(diffMs: number): string | null {
	if (diffMs < RELATIVE_THRESHOLD_JUST_NOW_MS) {
		return "即将";
	}
	if (diffMs < MS_PER_HOUR) {
		return `再过 ${Math.floor(diffMs / MS_PER_MINUTE)} 分钟`;
	}
	if (diffMs < RELATIVE_ABSOLUTE_SWITCH_MS) {
		return `再过 ${Math.floor(diffMs / MS_PER_HOUR)} 小时`;
	}
	return null;
}

export function formatRelativeTime(
	date: Date | string | number | null | undefined,
	now: Date = new Date(),
): string {
	if (date === null || date === undefined) {
		return FALLBACK;
	}
	const target = date instanceof Date ? date : new Date(date);
	const targetMs = target.getTime();
	if (Number.isNaN(targetMs)) {
		return FALLBACK;
	}
	const diffMs = now.getTime() - targetMs;
	if (diffMs >= 0) {
		if (diffMs < RELATIVE_ABSOLUTE_SWITCH_MS) {
			return formatPastRelative(diffMs);
		}
		return toAbsoluteTimestamp(target);
	}
	const future = formatFutureRelative(-diffMs);
	return future ?? toAbsoluteTimestamp(target);
}

export function formatTimestamp(
	date: Date | string | number | null | undefined,
	fallback: string = FALLBACK,
): string {
	if (date === null || date === undefined) {
		return fallback;
	}
	const target = date instanceof Date ? date : new Date(date);
	if (Number.isNaN(target.getTime())) {
		return fallback;
	}
	return toAbsoluteTimestamp(target);
}

export function formatValue(value: number | null | undefined, fallback: string = FALLBACK): string {
	if (value === null || value === undefined) {
		return fallback;
	}
	if (typeof value !== "number" || Number.isNaN(value)) {
		return fallback;
	}
	return value.toString();
}
