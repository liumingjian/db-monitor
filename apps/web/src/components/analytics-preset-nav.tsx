import type { TimeWindow } from "@db-monitor/api-client";
import Link from "next/link";

import type { AnalyticsPreset } from "../analytics-presets";

interface AnalyticsPresetNavProps {
	readonly currentWindow: TimeWindow;
	readonly presets: readonly AnalyticsPreset[];
}

export function AnalyticsPresetNav({
	currentWindow,
	presets,
}: AnalyticsPresetNavProps) {
	return (
		<div className="grid gap-3 md:grid-cols-3">
			{presets.map((preset) => {
				const isActive = preset.window === currentWindow;
				return (
					<Link
						className={
							isActive
								? "rounded-[1.2rem] border border-[var(--accent)] bg-[var(--panel)] px-4 py-4"
								: "rounded-[1.2rem] border border-black/5 bg-white px-4 py-4 transition hover:-translate-y-0.5 hover:border-[var(--accent)]"
						}
						href={preset.href}
						key={preset.label}
					>
						<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
							{preset.label}
						</p>
						<p className="mt-3 text-sm font-semibold text-black">{preset.window}</p>
						<p className="mt-2 text-sm leading-6 text-[var(--muted)]">
							{preset.description}
						</p>
					</Link>
				);
			})}
		</div>
	);
}
