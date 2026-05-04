import { QuickMetricCell } from "./quick-metric-cell";
import type { QuickMetricItem } from "./types";
import { cn } from "./utils";

export interface QuickMetricsProps {
	readonly items: readonly QuickMetricItem[];
	readonly className?: string;
}

const MAX_CELLS = 6;

const GRID_COL_CLASS: Readonly<Record<number, string>> = {
	1: "grid-cols-1",
	2: "grid-cols-2",
	3: "grid-cols-3",
	4: "grid-cols-4",
	5: "grid-cols-5",
	6: "grid-cols-6",
};

/**
 * 64px horizontal metric strip. Displays up to 6 QuickMetricCell items.
 */
export function QuickMetrics(props: QuickMetricsProps) {
	const { items, className } = props;
	const capped = items.slice(0, MAX_CELLS);
	if (capped.length === 0) {
		return null;
	}

	const colClass = GRID_COL_CLASS[capped.length] ?? GRID_COL_CLASS[MAX_CELLS];

	return (
		<div
			className={cn(
				"grid h-16 shrink-0 border-b border-border-hairline bg-bg-base",
				colClass,
				className,
			)}
		>
			{capped.map((item) => (
				<QuickMetricCell key={item.key} item={item} />
			))}
		</div>
	);
}
