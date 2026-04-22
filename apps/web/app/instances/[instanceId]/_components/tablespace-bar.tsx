import { bandToneClassName, formatPercent, type UsedRateBand } from "../../../../src/tablespaces-ui";

interface TablespaceBarProps {
	readonly percent: number;
	readonly band: UsedRateBand;
}

export function TablespaceBar({ percent, band }: TablespaceBarProps) {
	const clamped = Math.min(100, Math.max(0, percent));
	const fillClass = bandToneClassName(band);
	return (
		<div
			aria-label={`使用率 ${formatPercent(percent)}`}
			className="flex items-center gap-2"
			role="group"
		>
			<div className="h-2 w-28 overflow-hidden rounded-full bg-black/10">
				<div
					className={`h-full ${fillClass}`}
					data-band={band}
					style={{ width: `${clamped}%` }}
				/>
			</div>
			<span className="tabular-nums text-xs text-[var(--muted)]">
				{formatPercent(percent)}
			</span>
		</div>
	);
}
