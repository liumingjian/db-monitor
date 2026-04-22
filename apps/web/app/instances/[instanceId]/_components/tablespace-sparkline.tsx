import type { TablespaceHistoryEntryResponse } from "@db-monitor/api-client";

import {
	HISTORY_ALERT_LINE_PERCENT,
	buildSparklinePoints,
	sparklineSvgPath,
} from "../../../../src/tablespaces-ui";

interface TablespaceSparklineProps {
	readonly history: readonly TablespaceHistoryEntryResponse[];
}

export function TablespaceSparkline({ history }: TablespaceSparklineProps) {
	const points = buildSparklinePoints(history);
	if (points.length === 0) {
		return (
			<span aria-label="暂无 24 小时趋势" className="text-xs text-[var(--muted)]">
				—
			</span>
		);
	}
	const path = sparklineSvgPath(points);
	const threshold = 100 - HISTORY_ALERT_LINE_PERCENT;
	return (
		<svg
			aria-label="24 小时使用率走势"
			className="h-6 w-24 text-[var(--accent)]"
			preserveAspectRatio="none"
			role="img"
			viewBox="0 0 100 100"
		>
			<line
				stroke="rgba(239, 68, 68, 0.45)"
				strokeDasharray="4 3"
				strokeWidth="1"
				x1="0"
				x2="100"
				y1={threshold}
				y2={threshold}
			/>
			<path
				d={path}
				fill="none"
				stroke="currentColor"
				strokeLinecap="round"
				strokeLinejoin="round"
				strokeWidth="2"
			/>
		</svg>
	);
}
