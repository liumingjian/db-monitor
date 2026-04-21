import type { TimeWindow } from "@db-monitor/api-client";
import Link from "next/link";

import { APPROVED_TIME_WINDOWS } from "../server-api";

const TIME_WINDOW_LABELS: Record<TimeWindow, string> = {
	"15m": "15m",
	"1h": "1h",
	"6h": "6h",
	"24h": "24h",
};

interface TimeWindowNavProps {
	readonly currentWindow: TimeWindow;
	readonly pathname: string;
}

export function TimeWindowNav({ currentWindow, pathname }: TimeWindowNavProps) {
	return (
		<div className="flex flex-wrap gap-2">
			{APPROVED_TIME_WINDOWS.map((window) => {
				const isActive = window === currentWindow;
				return (
					<Link
						className={
							isActive
								? "rounded-full bg-[var(--accent)] px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-white"
								: "rounded-full border border-black/10 bg-white px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]"
						}
						href={`${pathname}?window=${window}`}
						key={window}
					>
						{TIME_WINDOW_LABELS[window]}
					</Link>
				);
			})}
		</div>
	);
}
