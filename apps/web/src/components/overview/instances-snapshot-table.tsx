import type { MetricCardResponse, OverviewInstanceResponse } from "@db-monitor/api-client";
import { cn } from "@db-monitor/ui";
import Link from "next/link";

interface InstancesSnapshotTableProps {
	readonly instances: readonly OverviewInstanceResponse[];
	readonly heading: string;
	readonly subheading: string;
	readonly emptyLabel: string;
	readonly columns: ColumnLabels;
	readonly statusLabels: StatusLabels;
	readonly keyMetricName: string;
	readonly keyMetricLabel: string;
}

interface ColumnLabels {
	readonly name: string;
	readonly engine: string;
	readonly environment: string;
	readonly status: string;
	readonly keyMetric: string;
	readonly labels: string;
}

interface StatusLabels {
	readonly healthy: string;
	readonly unhealthy: string;
	readonly unknown: string;
}

/**
 * Row5 instances snapshot table (Q9 rule 4).
 * Server Component: all links are anchors; no client JS required.
 */
export function InstancesSnapshotTable(props: InstancesSnapshotTableProps) {
	const {
		instances,
		heading,
		subheading,
		emptyLabel,
		columns,
		statusLabels,
		keyMetricName,
		keyMetricLabel,
	} = props;

	if (instances.length === 0) {
		return (
			<section className="flex flex-col gap-2 rounded-md border border-border-hairline bg-bg-base p-4">
				<header>
					<h3 className="text-sm font-semibold text-fg-primary">{heading}</h3>
					<p className="text-xs text-fg-muted">{subheading}</p>
				</header>
				<div className="rounded-sm border border-border-hairline bg-bg-elevated px-3 py-6 text-center text-xs text-fg-muted">
					{emptyLabel}
				</div>
			</section>
		);
	}

	return (
		<section className="flex flex-col gap-2 rounded-md border border-border-hairline bg-bg-base p-4">
			<header className="flex flex-wrap items-baseline justify-between gap-2">
				<div>
					<h3 className="text-sm font-semibold text-fg-primary">{heading}</h3>
					<p className="text-xs text-fg-muted">{subheading}</p>
				</div>
				<span className="font-mono text-[11px] text-fg-muted tabular-nums">{keyMetricLabel}</span>
			</header>
			<div className="overflow-x-auto">
				<table className="min-w-full border-separate border-spacing-0 text-sm">
					<thead>
						<tr className="text-left text-[11px] uppercase tracking-wide text-fg-muted">
							<Th>{columns.name}</Th>
							<Th>{columns.engine}</Th>
							<Th>{columns.environment}</Th>
							<Th>{columns.status}</Th>
							<Th numeric>{columns.keyMetric}</Th>
							<Th>{columns.labels}</Th>
						</tr>
					</thead>
					<tbody>
						{instances.map((instance) => {
							const metric = pickMetric(instance.metrics, keyMetricName);
							const tone = resolveTone(instance.status);
							return (
								<tr
									key={instance.instance_id}
									className="border-t border-border-hairline transition-colors hover:bg-bg-elevated active:bg-surface-overlay"
								>
									<Td>
										<Link
											href={`/instances/${encodeURIComponent(instance.instance_id)}`}
											className="font-medium text-fg-primary underline-offset-2 hover:text-accent hover:underline"
										>
											{instance.name}
										</Link>
									</Td>
									<Td mono>{instance.engine.toUpperCase()}</Td>
									<Td>{instance.environment}</Td>
									<Td>
										<span
											className={cn(
												"inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 text-[11px] font-medium",
												toneBadgeClass(tone),
											)}
										>
											<span
												className={cn("inline-block h-1.5 w-1.5 rounded-full", toneDotClass(tone))}
												aria-hidden
											/>
											{toneStatusLabel(tone, statusLabels)}
										</span>
									</Td>
									<Td mono numeric>
										{formatMetric(metric)}
									</Td>
									<Td>
										<div className="flex flex-wrap gap-1">
											{instance.labels.length === 0 ? (
												<span className="text-xs text-fg-muted">—</span>
											) : (
												instance.labels.map((label) => (
													<span
														key={`${instance.instance_id}-${label}`}
														className="rounded-sm border border-border-hairline bg-bg-elevated px-1.5 py-0.5 text-[11px] text-fg-secondary"
													>
														{label}
													</span>
												))
											)}
										</div>
									</Td>
								</tr>
							);
						})}
					</tbody>
				</table>
			</div>
		</section>
	);
}

function Th({
	children,
	numeric = false,
}: {
	readonly children: React.ReactNode;
	readonly numeric?: boolean;
}) {
	return (
		<th
			scope="col"
			className={cn(
				"border-b border-border-hairline px-3 py-2 font-semibold",
				numeric ? "text-right" : "text-left",
			)}
		>
			{children}
		</th>
	);
}

function Td({
	children,
	mono = false,
	numeric = false,
}: {
	readonly children: React.ReactNode;
	readonly mono?: boolean;
	readonly numeric?: boolean;
}) {
	return (
		<td
			className={cn(
				"px-3 py-2 text-fg-secondary align-middle",
				numeric ? "text-right" : "text-left",
				mono ? "font-mono tabular-nums" : undefined,
			)}
		>
			{children}
		</td>
	);
}

type StatusTone = "ok" | "critical" | "warning" | "info";

function resolveTone(status: string): StatusTone {
	const normalized = status?.toLowerCase() ?? "";
	if (normalized === "healthy" || normalized === "ok") {
		return "ok";
	}
	if (normalized === "unhealthy" || normalized === "critical" || normalized === "down") {
		return "critical";
	}
	if (normalized === "warning" || normalized === "degraded") {
		return "warning";
	}
	return "info";
}

function toneStatusLabel(tone: StatusTone, labels: StatusLabels): string {
	if (tone === "ok") return labels.healthy;
	if (tone === "critical" || tone === "warning") return labels.unhealthy;
	return labels.unknown;
}

function toneBadgeClass(tone: StatusTone): string {
	switch (tone) {
		case "ok":
			return "border-sev-ok-border bg-sev-ok-bg text-sev-ok";
		case "critical":
			return "border-sev-critical-border bg-sev-critical-bg text-sev-critical";
		case "warning":
			return "border-sev-warning-border bg-sev-warning-bg text-sev-warning";
		default:
			return "border-sev-info-border bg-sev-info-bg text-sev-info";
	}
}

function toneDotClass(tone: StatusTone): string {
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

function pickMetric(
	metrics: readonly MetricCardResponse[],
	metricName: string,
): MetricCardResponse | undefined {
	return metrics.find((entry) => entry.metric_name === metricName);
}

function formatMetric(metric: MetricCardResponse | undefined): string {
	if (!metric) {
		return "—";
	}
	const formatted = Number.isFinite(metric.value) ? metric.value.toFixed(2) : "—";
	return `${formatted} ${metric.unit}`;
}
