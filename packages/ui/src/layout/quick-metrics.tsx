import { QuickMetricCell } from "./quick-metric-cell";
import type { QuickMetricItem } from "./types";
import { cn } from "./utils";

export interface QuickMetricsProps {
	readonly items: readonly QuickMetricItem[];
	readonly className?: string;
}

const MAX_CELLS = 6;

// Desktop column layout maps the actual cell count to a grid template; below
// the lg breakpoint we collapse to 2/3 columns so cells don't truncate to a
// single character on phones / tablets.
const LG_GRID_COL_CLASS: Readonly<Record<number, string>> = {
	1: "lg:grid-cols-1",
	2: "lg:grid-cols-2",
	3: "lg:grid-cols-3",
	4: "lg:grid-cols-4",
	5: "lg:grid-cols-5",
	6: "lg:grid-cols-6",
};

/**
 * Responsive metric strip. Displays up to 6 QuickMetricCell items.
 *
 * Layout:
 * - <sm: 2 columns
 * - sm-md: 3 columns
 * - lg+: one column per cell (matches original 64px single-row strip)
 */
export function QuickMetrics(props: QuickMetricsProps) {
	const { items, className } = props;
	const capped = items.slice(0, MAX_CELLS);
	if (capped.length === 0) {
		return null;
	}

	const lgColClass = LG_GRID_COL_CLASS[capped.length] ?? LG_GRID_COL_CLASS[MAX_CELLS];

	return (
		<div
			className={cn(
				"grid shrink-0 grid-cols-2 border-b border-border-hairline bg-bg-base sm:grid-cols-3 lg:h-16",
				lgColClass,
				className,
			)}
		>
			{capped.map((item) => (
				<QuickMetricCell key={item.key} item={item} />
			))}
		</div>
	);
}
