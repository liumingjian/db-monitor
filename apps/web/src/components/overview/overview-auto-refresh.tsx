"use client";

import { Button, cn, useAutoRefresh } from "@db-monitor/ui";
import { Pause as PauseIcon, Play as PlayIcon, RefreshCw as RefreshIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

const DEFAULT_INTERVAL_MS = 30_000;

interface OverviewAutoRefreshProps {
	readonly generatedAt: string;
	readonly generatedAtLabel: string;
	readonly pauseLabel: string;
	readonly resumeLabel: string;
	readonly refreshLabel: string;
	readonly intervalMs?: number;
}

/**
 * Client-side auto-refresh controller (Q9 rule 6).
 *
 * - 30s default interval (configurable).
 * - Toggles pause/resume; no spinner; uses `useAutoRefresh` hook.
 * - Manual refresh button always available.
 * - `router.refresh()` re-renders the server component with fresh data.
 */
export function OverviewAutoRefresh(props: OverviewAutoRefreshProps) {
	const {
		generatedAt,
		generatedAtLabel,
		pauseLabel,
		resumeLabel,
		refreshLabel,
		intervalMs = DEFAULT_INTERVAL_MS,
	} = props;
	const router = useRouter();
	const [paused, setPaused] = useState<boolean>(false);

	const tick = useCallback(() => {
		router.refresh();
	}, [router]);

	useAutoRefresh(tick, { intervalMs, paused });

	return (
		<div className="flex flex-wrap items-center gap-3">
			<div className="flex flex-col text-right">
				<span className="text-[11px] uppercase tracking-wide text-fg-muted">
					{generatedAtLabel}
				</span>
				<span className="font-mono text-xs tabular-nums text-fg-secondary">{generatedAt}</span>
			</div>
			<div
				className={cn(
					"flex items-center gap-1 rounded-md border border-border-subtle bg-bg-elevated p-0.5",
				)}
			>
				<Button
					type="button"
					variant="ghost"
					size="sm"
					aria-pressed={paused}
					onClick={() => setPaused((prev) => !prev)}
				>
					{paused ? (
						<>
							<PlayIcon className="h-3.5 w-3.5" aria-hidden />
							{resumeLabel}
						</>
					) : (
						<>
							<PauseIcon className="h-3.5 w-3.5" aria-hidden />
							{pauseLabel}
						</>
					)}
				</Button>
				<Button type="button" variant="ghost" size="sm" onClick={tick} aria-label={refreshLabel}>
					<RefreshIcon className="h-3.5 w-3.5" aria-hidden />
					{refreshLabel}
				</Button>
			</div>
		</div>
	);
}
