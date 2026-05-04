"use client";

import type { InstanceResponse } from "@db-monitor/api-client";
import { Card, CardContent, CardHeader, EntityBadge } from "@db-monitor/ui";
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

interface InstancesGridProps {
	readonly rows: readonly InstanceResponse[];
	readonly sparkValues: SparkValuesMap;
	readonly sparkMetric: SparkMetricKey;
	readonly sparkColorIndex: number;
}

export function InstancesGrid(props: InstancesGridProps) {
	const { rows, sparkValues, sparkMetric, sparkColorIndex } = props;
	const t = useTranslations("instancesPage");

	return (
		<div className="flex flex-col gap-3">
			<div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
				{rows.map((instance) => {
					const sparkEntry = sparkValues[instance.instance_id];
					const sparkSeries = sparkEntry === null ? null : (sparkEntry?.[sparkMetric] ?? []);
					const fanoutSkipped = sparkEntry === null;
					return (
						<Card className="transition-colors hover:border-accent" key={instance.instance_id}>
							<CardHeader className="flex flex-row items-start justify-between gap-3 pb-2">
								<div className="min-w-0">
									<Link
										className="block truncate text-base font-semibold text-fg-primary hover:text-accent"
										href={`/instances/${instance.instance_id}`}
									>
										{instance.name}
									</Link>
									<p className="font-mono text-xs tabular-nums text-fg-muted">
										{instance.connection.host}:{instance.connection.port}
									</p>
								</div>
								<EntityBadge
									label={translateValidation(t, instance.validation.status)}
									tone={validationTone(instance.validation.status)}
								/>
							</CardHeader>
							<CardContent className="flex flex-col gap-3">
								<div className="flex flex-wrap items-center gap-2 text-xs text-fg-muted">
									<span className="rounded-sm border border-border-subtle px-2 py-0.5 font-mono uppercase tracking-widest text-fg-secondary">
										{instance.engine}
									</span>
									<span className="font-mono tabular-nums">{instance.environment}</span>
									{instance.labels.length > 0 ? (
										<span className="truncate">{instance.labels.join(", ")}</span>
									) : null}
								</div>
								<div>
									<p className="mb-1 text-[11px] uppercase tracking-widest text-fg-muted">
										{t(`columnSpark_${sparkMetric}`)}
									</p>
									{fanoutSkipped ? (
										<p className="text-xs text-fg-muted">{t("sparkSkipped")}</p>
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
								</div>
								<div className="flex items-center justify-between gap-2 border-t border-border-hairline pt-3">
									<RevalidateInstanceButton
										instanceId={instance.instance_id}
										instanceName={instance.name}
										size="sm"
									/>
									<RowTier3Placeholders compact />
								</div>
							</CardContent>
						</Card>
					);
				})}
			</div>
			{rows.length > SPARKLINE_FANOUT_LIMIT ? (
				<p className="rounded-md border border-dashed border-border-subtle bg-bg-base px-3 py-2 text-xs text-fg-muted">
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
