import { buildInstancePresets } from "../../../src/analytics-presets";
import { AnalyticsPresetNav } from "../../../src/components/analytics-preset-nav";
import { MetricChart } from "../../../src/components/metric-chart";
import { TimeWindowNav } from "../../../src/components/time-window-nav";
import {
	type InsightTone,
	MONITORING_CHART_FRAME,
	buildInstanceCapabilityBoundary,
	buildInstancesFlowModel,
	getInstanceConnectionLabel,
	supportsInstanceAnalytics,
} from "../../../src/monitoring-ui";
import { createServerApiClient, parseTimeWindow } from "../../../src/server-api";

interface InstanceDetailPageProps {
	readonly params: Promise<{
		readonly instanceId: string;
	}>;
	readonly searchParams: Promise<{
		readonly window?: string;
	}>;
}

export default async function InstanceDetailPage({
	params,
	searchParams,
}: InstanceDetailPageProps) {
	const { instanceId } = await params;
	const resolvedSearchParams = await searchParams;
	const window = parseTimeWindow(resolvedSearchParams.window);
	const apiClient = await createServerApiClient();
	const instance = await apiClient.getInstance(instanceId);
	const trend = supportsInstanceAnalytics(instance)
		? await apiClient.getInstanceTrends(instanceId, window)
		: null;
	const model = buildInstancesFlowModel({
		selectedInstance: instance,
		tableRows: [instance],
		trend,
	});
	const capabilityBoundary = buildInstanceCapabilityBoundary(instance);
	const analyticsEnabled = supportsInstanceAnalytics(instance);

	return (
		<div className="space-y-6">
			<div>
				<div className="flex flex-wrap items-center gap-3">
					<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
						{model.selectedInstance.environment}
					</p>
					<span className="rounded-full border border-[var(--accent)]/25 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">
						{model.selectedInstance.engine}
					</span>
				</div>
				<h2 className="mt-3 text-3xl font-semibold">{model.selectedInstance.name}</h2>
				<p className="mt-3 text-sm text-[var(--muted)]">
					{model.selectedInstance.connection.host}:{model.selectedInstance.connection.port} ·{" "}
					{getInstanceConnectionLabel(model.selectedInstance)}:{" "}
					{model.selectedInstance.connection.database}
				</p>
			</div>
			<div className="grid gap-4 md:grid-cols-3">
				{model.detailReadouts.map((readout) => (
					<div
						className="rounded-[1.2rem] border border-black/5 bg-white px-4 py-4"
						key={readout.title}
					>
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							{readout.title}
						</p>
						<p className="mt-3 text-xl font-semibold">{readout.value}</p>
					</div>
				))}
			</div>
			<div className="rounded-[1.2rem] border border-black/5 bg-white px-5 py-4">
				<div>
					<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
						{capabilityBoundary.label}
					</p>
					<p className="mt-3 text-xl font-semibold">{capabilityBoundary.value}</p>
					<p className="mt-2 text-sm text-[var(--muted)]">{capabilityBoundary.detail}</p>
				</div>
			</div>
			{analyticsEnabled && model.trend !== null ? (
				<>
					<div className="flex flex-col gap-3 rounded-[1.2rem] border border-black/5 bg-white px-5 py-4 md:flex-row md:items-center md:justify-between">
						<div>
							<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
								Trend Window
							</p>
							<p className="mt-2 text-sm text-[var(--muted)]">
								Inspect this instance across approved observation windows without changing the
								route family.
							</p>
						</div>
						<TimeWindowNav
							currentWindow={model.trend.window}
							pathname={`/instances/${model.selectedInstance.instance_id}`}
						/>
					</div>
					<div className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5">
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Preset views
						</p>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Reopen this instance with a stable route and observation window for common triage
							loops.
						</p>
						<div className="mt-4">
							<AnalyticsPresetNav
								currentWindow={model.trend.window}
								presets={buildInstancePresets(model.selectedInstance.instance_id)}
							/>
						</div>
					</div>
					<div className="grid gap-4 md:grid-cols-2">
						{model.trend.cards.map((card) => (
							<div
								className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4"
								key={card.metric_name}
							>
								<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
									{card.label}
								</p>
								<p className="mt-3 text-3xl font-semibold">{card.value}</p>
								<p className="mt-1 text-sm text-[var(--muted)]">{card.unit}</p>
							</div>
						))}
					</div>
					<div className="rounded-[1.6rem] border border-black/5 bg-white p-5">
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Capacity readout
						</p>
						<div className="mt-4 grid gap-3 md:grid-cols-3">
							{model.capacityReadout.map((insight) => (
								<div
									className="rounded-[1.2rem] border px-4 py-4"
									key={insight.title}
									style={insightToneStyle(insight.tone)}
								>
									<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
										{insight.title}
									</p>
									<p className="mt-3 text-xl font-semibold">{insight.value}</p>
									<p className="mt-2 text-sm text-[var(--muted)]">{insight.detail}</p>
								</div>
							))}
						</div>
					</div>
					<div className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5">
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							{MONITORING_CHART_FRAME.title}
						</p>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Observed window:{" "}
							<span className="font-semibold text-black">{model.trend.window}</span>
						</p>
						<div className="mt-4">
							<MetricChart
								emptyState={MONITORING_CHART_FRAME.emptyState}
								series={model.trend.charts}
								title={MONITORING_CHART_FRAME.title}
							/>
						</div>
					</div>
				</>
			) : null}
		</div>
	);
}

function insightToneStyle(tone: InsightTone): {
	readonly backgroundColor: string;
	readonly borderColor: string;
} {
	if (tone === "risk") {
		return {
			backgroundColor: "rgba(246, 214, 209, 0.5)",
			borderColor: "rgba(182, 79, 44, 0.18)",
		};
	}
	if (tone === "watch") {
		return {
			backgroundColor: "rgba(249, 236, 205, 0.55)",
			borderColor: "rgba(196, 137, 31, 0.18)",
		};
	}
	return {
		backgroundColor: "rgba(230, 237, 232, 0.55)",
		borderColor: "rgba(74, 110, 89, 0.16)",
	};
}
