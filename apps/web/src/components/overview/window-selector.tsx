"use client";

import type { TimeWindow } from "@db-monitor/api-client";
import { cn } from "@db-monitor/ui";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useTransition } from "react";

interface WindowSelectorProps {
	readonly currentWindow: TimeWindow;
	readonly windows: readonly TimeWindow[];
	readonly ariaLabel: string;
}

/**
 * Segmented control for Overview time window (Q9 rule 7).
 * Writes `?window=` on the current route and triggers server re-fetch.
 */
export function WindowSelector(props: WindowSelectorProps) {
	const { currentWindow, windows, ariaLabel } = props;
	const router = useRouter();
	const pathname = usePathname();
	const searchParams = useSearchParams();
	const [pending, startTransition] = useTransition();

	const setWindow = useCallback(
		(next: TimeWindow) => {
			if (next === currentWindow) {
				return;
			}
			const params = new URLSearchParams(searchParams?.toString());
			params.set("window", next);
			startTransition(() => {
				router.push(`${pathname}?${params.toString()}`);
			});
		},
		[currentWindow, pathname, router, searchParams],
	);

	return (
		<div
			role="tablist"
			aria-label={ariaLabel}
			className={cn(
				"inline-flex items-center gap-0.5 rounded-md border border-border-subtle bg-bg-elevated p-0.5",
				pending ? "opacity-70" : undefined,
			)}
		>
			{windows.map((window) => {
				const active = window === currentWindow;
				return (
					<button
						key={window}
						type="button"
						role="tab"
						aria-selected={active}
						onClick={() => setWindow(window)}
						className={cn(
							"rounded-sm px-3 py-1 font-mono text-xs uppercase tabular-nums transition-colors",
							"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
							active
								? "bg-accent text-on-accent"
								: "text-fg-secondary hover:bg-surface-overlay hover:text-fg-primary",
						)}
					>
						{window}
					</button>
				);
			})}
		</div>
	);
}
