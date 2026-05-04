import type { QuickMetricItem } from "./types";
import { cn } from "./utils";

export interface QuickMetricCellProps {
	readonly item: QuickMetricItem;
	readonly className?: string;
}

/**
 * Single cell in the QuickMetrics strip.
 *
 * Typography contract (Quick Reference §6 Typography):
 * - label: 11px uppercase muted (no font-mono — Chinese/English mixed safe)
 * - value: 18px tabular-nums; mono+semibold when numeric, sans+regular for text
 *   tokens like "通过". Keeps weight hierarchy stable across cells.
 * - unit: 12px muted, sits next to value as subordinate; no longer string-joined
 *   into the value (which previously made `0.4 qps` and `通过` render at
 *   different visual weights).
 * - hint: 11px muted secondary line, optional.
 */
export function QuickMetricCell(props: QuickMetricCellProps) {
	const { item, className } = props;
	const numeric = item.numeric !== false;

	return (
		<div
			className={cn(
				"flex min-h-16 min-w-0 items-center gap-3 border-b border-r border-border-hairline px-4 py-2 lg:h-full lg:min-h-0 lg:border-b-0 last:border-r-0",
				className,
			)}
		>
			<div className="flex min-w-0 flex-1 flex-col justify-center gap-0.5">
				<span className="truncate text-[11px] font-medium uppercase tracking-wider text-fg-muted">
					{item.label}
				</span>
				<div className="flex min-w-0 items-baseline gap-1.5">
					<span
						className={cn(
							"truncate text-lg leading-tight tabular-nums text-fg-primary",
							numeric ? "font-mono font-semibold" : "font-sans font-medium",
						)}
					>
						{item.value}
					</span>
					{item.unit ? <span className="shrink-0 text-xs text-fg-muted">{item.unit}</span> : null}
				</div>
				{item.hint ? <span className="truncate text-[11px] text-fg-muted">{item.hint}</span> : null}
			</div>
			{item.sparkline ? <div className="h-8 w-16 shrink-0">{item.sparkline}</div> : null}
		</div>
	);
}
