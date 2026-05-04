"use client";

import type { InstanceResponse } from "@db-monitor/api-client";
import { EntityBadge } from "@db-monitor/ui";
import type { SeverityTone } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import Link from "next/link";

import { InstanceSparkline } from "./instance-sparkline";
import { RevalidateInstanceButton } from "./revalidate-instance-button";
import { RowTier3Placeholders } from "./tier3-placeholder-actions";
import {
	SPARKLINE_FANOUT_LIMIT,
	type SparkMetricKey,
	type SparkValuesMap,
	pickMetricNameForEngine,
} from "./types";

interface InstancesTableProps {
	readonly rows: readonly InstanceResponse[];
	readonly sparkValues: SparkValuesMap;
	readonly sparkMetric: SparkMetricKey;
	readonly sparkColorIndex: number;
}

export function InstancesTable(props: InstancesTableProps) {
	const { rows, sparkValues, sparkMetric, sparkColorIndex } = props;
	const t = useTranslations("instancesPage");

	return (
		<div className="overflow-x-auto rounded-md border border-border-hairline bg-bg-base">
			<table className="min-w-full text-sm">
				<thead className="border-b border-border-hairline bg-bg-base">
					<tr className="text-left text-xs uppercase tracking-widest text-fg-muted">
						<th className="px-3 py-2 font-medium">{t("columnName")}</th>
						<th className="px-3 py-2 font-medium">{t("columnEngine")}</th>
						<th className="px-3 py-2 font-medium">{t("columnEnvironment")}</th>
						<th className="px-3 py-2 font-medium">{t("columnValidation")}</th>
						<th className="px-3 py-2 font-medium">{t(`columnSpark_${sparkMetric}`)}</th>
						<th className="px-3 py-2 font-medium">{t("columnLabels")}</th>
						<th className="px-3 py-2 font-medium text-right">{t("columnActions")}</th>
					</tr>
				</thead>
				<tbody className="divide-y divide-border-hairline">
					{rows.map((instance) => {
						const sparkEntry = sparkValues[instance.instance_id];
						const sparkSeries = sparkEntry === null ? null : (sparkEntry?.[sparkMetric] ?? []);
						const fanoutSkipped = sparkEntry === null;
						return (
							<tr className="transition-colors hover:bg-bg-elevated" key={instance.instance_id}>
								<td className="px-3 py-3 align-middle">
									<Link
										className="font-medium text-fg-primary hover:text-accent"
										href={`/instances/${instance.instance_id}`}
									>
										{instance.name}
									</Link>
									<p className="font-mono text-xs tabular-nums text-fg-muted">
										{instance.connection.host}:{instance.connection.port}
									</p>
								</td>
								<td className="px-3 py-3 align-middle">
									<span className="rounded-sm border border-border-subtle px-2 py-0.5 font-mono text-xs uppercase tracking-widest text-fg-secondary">
										{instance.engine}
									</span>
								</td>
								<td className="px-3 py-3 align-middle font-mono text-xs text-fg-secondary">
									{instance.environment}
								</td>
								<td className="px-3 py-3 align-middle">
									<EntityBadge
										label={translateValidation(t, instance.validation.status)}
										tone={validationTone(instance.validation.status)}
									/>
								</td>
								<td className="px-3 py-3 align-middle" style={{ minWidth: 120 }}>
									{fanoutSkipped ? (
										<span className="text-xs text-fg-muted">{t("sparkSkippedShort")}</span>
									) : (
										<InstanceSparkline
											ariaLabel={t("sparkAriaLabel", {
												metric: t(`sparkMetric_${sparkMetric}`),
												instance: instance.name,
												backendMetric: pickMetricNameForEngine(instance.engine, sparkMetric),
											})}
											colorIndex={sparkColorIndex}
											emptyLabel={t("sparkEmpty")}
											values={sparkSeries}
										/>
									)}
								</td>
								<td className="px-3 py-3 align-middle text-xs text-fg-muted">
									{instance.labels.length === 0 ? "—" : instance.labels.join(", ")}
								</td>
								<td className="px-3 py-3 align-middle">
									<div className="flex items-center justify-end gap-1">
										<RevalidateInstanceButton
											instanceId={instance.instance_id}
											instanceName={instance.name}
											size="sm"
										/>
										<RowTier3Placeholders compact />
									</div>
								</td>
							</tr>
						);
					})}
				</tbody>
			</table>
			{rows.length > SPARKLINE_FANOUT_LIMIT ? (
				<p className="border-t border-border-hairline px-3 py-2 text-xs text-fg-muted">
					{t("sparkFanoutNotice", { limit: SPARKLINE_FANOUT_LIMIT })}
				</p>
			) : null}
		</div>
	);
}

function validationTone(status: string): SeverityTone {
	if (status === "passed") return "ok";
	if (status === "failed") return "critical";
	return "info";
}

type TranslateFn = (key: string) => string;

function translateValidation(t: TranslateFn, status: string): string {
	if (status === "passed" || status === "failed") {
		return t(`validation_${status}`);
	}
	if (status === "pending") {
		return t("validation_pending");
	}
	return status;
}
