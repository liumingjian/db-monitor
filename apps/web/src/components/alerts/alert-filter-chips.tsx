import Link from "next/link";
import type { AlertListFilterValues } from "../../monitoring-ui";

export interface AlertFilterChipsProps {
	readonly filters: AlertListFilterValues;
	readonly matchedCount: number;
	readonly baseHref: string;
}

interface ChipSpec {
	readonly activeLabel: string;
	readonly allLabel: string;
	readonly activeValue: string;
	readonly key: keyof AlertListFilterValues;
	readonly labelPrefix: string;
}

const COUNT_SINGLE_THRESHOLD = 0;

export function AlertFilterChips({ filters, matchedCount, baseHref }: AlertFilterChipsProps) {
	const specs: readonly ChipSpec[] = [
		{
			activeLabel: toSeverityLabel(filters.severity),
			activeValue: filters.severity,
			allLabel: "全部严重度",
			key: "severity",
			labelPrefix: "严重度",
		},
		{
			activeLabel: toStatusLabel(filters.status),
			activeValue: filters.status,
			allLabel: "全部状态",
			key: "status",
			labelPrefix: "状态",
		},
		{
			activeLabel: filters.instance,
			activeValue: filters.instance,
			allLabel: "全部实例",
			key: "instance",
			labelPrefix: "实例",
		},
		{
			activeLabel: filters.opened_after,
			activeValue: filters.opened_after,
			allLabel: "全部时间",
			key: "opened_after",
			labelPrefix: "时间窗",
		},
	];

	return (
		<div className="flex flex-col gap-3">
			<div className="flex flex-wrap items-center gap-2">
				{specs.map((spec) => (
					<Chip
						activeLabel={spec.activeLabel}
						allLabel={spec.allLabel}
						baseHref={baseHref}
						filters={filters}
						isActive={spec.activeValue.length > 0}
						key={spec.key}
						labelPrefix={spec.labelPrefix}
						removeKey={spec.key}
					/>
				))}
				<ReadOnlyChip allLabel="全部引擎" labelPrefix="引擎" />
				<ReadOnlyChip allLabel="全部指标" labelPrefix="指标" />
				<ReadOnlyChip allLabel="全部负责人" labelPrefix="负责人" />
				{hasAnyFilter(filters) ? (
					<Link
						className="inline-flex h-7 items-center gap-1 rounded-full border border-border-hairline bg-surface-overlay px-3 text-xs text-fg-secondary transition-colors hover:border-accent hover:text-fg-primary"
						href={baseHref}
					>
						清除全部过滤
					</Link>
				) : null}
			</div>
			<p className="text-xs text-fg-muted">
				{matchedCount <= COUNT_SINGLE_THRESHOLD
					? "未命中任何告警"
					: `命中 ${matchedCount.toString()} 条告警`}
			</p>
		</div>
	);
}

interface ChipProps {
	readonly activeLabel: string;
	readonly allLabel: string;
	readonly baseHref: string;
	readonly filters: AlertListFilterValues;
	readonly isActive: boolean;
	readonly labelPrefix: string;
	readonly removeKey: keyof AlertListFilterValues;
}

function Chip({
	activeLabel,
	allLabel,
	baseHref,
	filters,
	isActive,
	labelPrefix,
	removeKey,
}: ChipProps) {
	if (!isActive) {
		return (
			<span className="inline-flex h-7 items-center gap-1 rounded-full border border-border-hairline bg-bg-elevated px-3 text-xs text-fg-muted">
				<span className="font-medium text-fg-secondary">{labelPrefix}</span>
				<span>{allLabel}</span>
			</span>
		);
	}
	const clearHref = buildClearHref(baseHref, filters, removeKey);
	return (
		<span className="inline-flex h-7 items-center gap-1.5 rounded-full border border-accent/60 bg-accent/10 px-3 text-xs text-fg-primary">
			<span className="font-medium text-accent">{labelPrefix}</span>
			<span className="font-mono text-[11px]">{activeLabel}</span>
			<Link aria-label="清除" className="text-fg-muted hover:text-fg-primary" href={clearHref}>
				×
			</Link>
		</span>
	);
}

function ReadOnlyChip({
	allLabel,
	labelPrefix,
}: {
	readonly allLabel: string;
	readonly labelPrefix: string;
}) {
	return (
		<span className="inline-flex h-7 items-center gap-1 rounded-full border border-border-hairline bg-bg-elevated px-3 text-xs text-fg-muted">
			<span className="font-medium text-fg-secondary">{labelPrefix}</span>
			<span>{allLabel}</span>
		</span>
	);
}

function hasAnyFilter(filters: AlertListFilterValues): boolean {
	return (
		filters.instance.length > 0 ||
		filters.opened_after.length > 0 ||
		filters.opened_before.length > 0 ||
		filters.severity.length > 0 ||
		filters.status.length > 0
	);
}

function buildClearHref(
	baseHref: string,
	filters: AlertListFilterValues,
	removeKey: keyof AlertListFilterValues,
): string {
	const params = new URLSearchParams();
	const keys = Object.keys(filters) as (keyof AlertListFilterValues)[];
	for (const key of keys) {
		if (key === removeKey) {
			continue;
		}
		const value = filters[key];
		if (typeof value === "string" && value.length > 0) {
			params.set(key, value);
		}
	}
	const query = params.toString();
	return query.length === 0 ? baseHref : `${baseHref}?${query}`;
}

function toSeverityLabel(severity: AlertListFilterValues["severity"]): string {
	if (severity === "critical") {
		return "紧急";
	}
	if (severity === "warning") {
		return "警告";
	}
	return "";
}

function toStatusLabel(status: AlertListFilterValues["status"]): string {
	if (status === "open") {
		return "活跃";
	}
	if (status === "acknowledged") {
		return "已确认";
	}
	if (status === "resolved") {
		return "已解决";
	}
	return "";
}
