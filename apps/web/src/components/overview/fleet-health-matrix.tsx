import type { OverviewInstanceResponse } from "@db-monitor/api-client";
import { cn } from "@db-monitor/ui";
import Link from "next/link";

interface FleetHealthMatrixProps {
	readonly instances: readonly OverviewInstanceResponse[];
	readonly title: string;
	readonly subtitle: string;
	readonly emptyLabel: string;
	readonly statusLabels: StatusLabels;
}

interface StatusLabels {
	readonly healthy: string;
	readonly unhealthy: string;
	readonly unknown: string;
}

type CellTone = "ok" | "critical" | "warning" | "info";

interface Cell {
	readonly instance: OverviewInstanceResponse;
	readonly tone: CellTone;
	readonly statusText: string;
}

/**
 * Fleet Health Matrix (Q9 rule 5): each cell = 1 instance, clickable to /instances/[id].
 *
 * Server Component: renders static anchor tags; no JS needed for navigation.
 */
export function FleetHealthMatrix(props: FleetHealthMatrixProps) {
	const { instances, title, subtitle, emptyLabel, statusLabels } = props;
	const cells = instances.map((instance) => toCell(instance, statusLabels));

	return (
		<section className="flex flex-col gap-3 rounded-md border border-border-hairline bg-bg-base p-4">
			<header className="flex flex-wrap items-baseline justify-between gap-2">
				<div>
					<h3 className="text-sm font-semibold text-fg-primary">{title}</h3>
					<p className="text-xs text-fg-muted">{subtitle}</p>
				</div>
				<LegendRow labels={statusLabels} />
			</header>
			{cells.length === 0 ? (
				<div className="rounded-sm border border-border-hairline bg-bg-elevated px-3 py-6 text-center text-xs text-fg-muted">
					{emptyLabel}
				</div>
			) : (
				<div className="grid grid-cols-[repeat(auto-fill,minmax(168px,1fr))] gap-2">
					{cells.map((cell) => (
						<FleetCell key={cell.instance.instance_id} cell={cell} />
					))}
				</div>
			)}
		</section>
	);
}

function LegendRow({ labels }: { readonly labels: StatusLabels }) {
	return (
		<ul className="flex flex-wrap items-center gap-3 text-[11px] text-fg-muted">
			<LegendDot tone="ok" label={labels.healthy} />
			<LegendDot tone="critical" label={labels.unhealthy} />
			<LegendDot tone="info" label={labels.unknown} />
		</ul>
	);
}

function LegendDot({ tone, label }: { readonly tone: CellTone; readonly label: string }) {
	return (
		<li className="flex items-center gap-1.5">
			<span className={cn("inline-block h-2 w-2 rounded-full", toneDotClass(tone))} aria-hidden />
			<span>{label}</span>
		</li>
	);
}

function FleetCell({ cell }: { readonly cell: Cell }) {
	const { instance, tone, statusText } = cell;
	return (
		<Link
			href={`/instances/${encodeURIComponent(instance.instance_id)}`}
			aria-label={`${instance.name} · ${instance.engine} · ${instance.environment} · ${statusText}`}
			className={cn(
				"group flex min-h-[74px] flex-col justify-between gap-2 rounded-md border px-3 py-2.5 transition-colors",
				"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
				toneSurfaceClass(tone),
			)}
		>
			<div className="flex items-center gap-2">
				<span
					className={cn("inline-block h-2 w-2 shrink-0 rounded-full", toneDotClass(tone))}
					aria-hidden
				/>
				<span className="truncate text-xs font-semibold text-fg-primary">{instance.name}</span>
			</div>
			<div className="flex items-center justify-between gap-2 font-mono text-[11px] tabular-nums text-fg-muted">
				<span className="uppercase">{instance.engine}</span>
				<span>{instance.environment}</span>
			</div>
			<span className={cn("text-[11px] font-medium", toneTextClass(tone))}>{statusText}</span>
		</Link>
	);
}

function toCell(instance: OverviewInstanceResponse, labels: StatusLabels): Cell {
	const normalized = instance.status?.toLowerCase() ?? "";
	if (normalized === "healthy" || normalized === "ok") {
		return { instance, tone: "ok", statusText: labels.healthy };
	}
	if (normalized === "unhealthy" || normalized === "critical" || normalized === "down") {
		return { instance, tone: "critical", statusText: labels.unhealthy };
	}
	if (normalized === "warning" || normalized === "degraded") {
		return { instance, tone: "warning", statusText: labels.unhealthy };
	}
	return { instance, tone: "info", statusText: labels.unknown };
}

function toneDotClass(tone: CellTone): string {
	switch (tone) {
		case "ok":
			return "bg-sev-ok";
		case "critical":
			return "bg-sev-critical";
		case "warning":
			return "bg-sev-warning";
		default:
			return "bg-sev-info";
	}
}

function toneSurfaceClass(tone: CellTone): string {
	switch (tone) {
		case "ok":
			return "border-sev-ok-border bg-sev-ok-bg hover:border-sev-ok hover:bg-bg-elevated";
		case "critical":
			return "border-sev-critical-border bg-sev-critical-bg hover:border-sev-critical hover:bg-bg-elevated";
		case "warning":
			return "border-sev-warning-border bg-sev-warning-bg hover:border-sev-warning hover:bg-bg-elevated";
		default:
			return "border-sev-info-border bg-sev-info-bg hover:border-sev-info hover:bg-bg-elevated";
	}
}

function toneTextClass(tone: CellTone): string {
	switch (tone) {
		case "ok":
			return "text-sev-ok";
		case "critical":
			return "text-sev-critical";
		case "warning":
			return "text-sev-warning";
		default:
			return "text-sev-info";
	}
}
