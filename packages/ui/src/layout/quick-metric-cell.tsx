import type { QuickMetricItem } from "./types";
import { cn } from "./utils";

export interface QuickMetricCellProps {
	readonly item: QuickMetricItem;
	readonly className?: string;
}

/**
 * Single cell in the 64px QuickMetrics strip.
 * label (text-xs muted) + value (mono, fg-primary) + optional sparkline slot.
 */
export function QuickMetricCell(props: QuickMetricCellProps) {
	const { item, className } = props;

	return (
		<div
			className={cn(
				"flex h-full min-w-0 items-center gap-3 border-r border-border-hairline px-4 last:border-r-0",
				className,
			)}
		>
			<div className="flex min-w-0 flex-1 flex-col justify-center">
				<span className="truncate text-[11px] uppercase tracking-wider text-fg-muted">
					{item.label}
				</span>
				<span className="truncate font-mono text-base text-fg-primary">{item.value}</span>
				{item.hint ? <span className="truncate text-[11px] text-fg-muted">{item.hint}</span> : null}
			</div>
			{item.sparkline ? <div className="h-8 w-16 shrink-0">{item.sparkline}</div> : null}
		</div>
	);
}
