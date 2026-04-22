import { OVERVIEW_PRESETS } from "../../src/analytics-presets";
import { AnalyticsPresetNav } from "../../src/components/analytics-preset-nav";
import { AppChrome } from "../../src/components/app-chrome";
import { MetricChart } from "../../src/components/metric-chart";
import { TimeWindowNav } from "../../src/components/time-window-nav";
import { type InsightTone, buildDashboardModel } from "../../src/monitoring-ui";
import { createServerApiClient, parseTimeWindow, requireServerSession } from "../../src/server-api";

interface OverviewPageProps {
	readonly searchParams: Promise<{
		readonly window?: string;
	}>;
}

export default async function OverviewPage({ searchParams }: OverviewPageProps) {
	const session = await requireServerSession("/overview");
	const params = await searchParams;
	const window = parseTimeWindow(params.window);
	const apiClient = await createServerApiClient();
	const model = buildDashboardModel(await apiClient.getOverview(window));

	return (
		<AppChrome session={session}>
			<div className="space-y-6">
				<div className="flex flex-col gap-3 rounded-[1.2rem] border border-black/5 bg-white px-5 py-4 md:flex-row md:items-center md:justify-between">
					<div>
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Analytics Window
						</p>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Switch the overview between approved observation windows without leaving the route.
						</p>
					</div>
					<TimeWindowNav currentWindow={model.overview.window} pathname="/overview" />
				</div>
				<div className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5">
					<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
						Preset views
					</p>
					<p className="mt-2 text-sm text-[var(--muted)]">
						Reopen the same fleet analysis route without rebuilding the path and window from memory.
						Presets keep the current coverage boundary in view while you pivot between approved
						observation windows.
					</p>
					<div className="mt-4">
						<AnalyticsPresetNav currentWindow={model.overview.window} presets={OVERVIEW_PRESETS} />
					</div>
				</div>
				<div className="rounded-[1.6rem] border border-black/5 bg-white p-5">
					<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
						{model.capabilityBoundary.label}
					</p>
					<p className="mt-3 text-2xl font-semibold">{model.capabilityBoundary.value}</p>
					<p className="mt-2 max-w-3xl text-sm text-[var(--muted)]">
						{model.capabilityBoundary.detail}
					</p>
					<div className="mt-4 grid gap-3 md:grid-cols-3">
						{model.coverageReadout.map((readout) => (
							<div
								className="rounded-[1rem] border border-black/5 bg-[var(--panel)] px-4 py-3"
								key={readout.title}
							>
								<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
									{readout.title}
								</p>
								<p className="mt-2 text-xl font-semibold">{readout.value}</p>
								<p className="mt-2 text-sm text-[var(--muted)]">{readout.detail}</p>
							</div>
						))}
					</div>
				</div>
				<div className="grid gap-4 md:grid-cols-3">
					{model.heroMetrics.map((metric) => (
						<div
							className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5"
							key={metric.label}
						>
							<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
								{metric.label}
							</p>
							<p className="mt-3 text-3xl font-semibold">{metric.value}</p>
						</div>
					))}
				</div>
				<div className="rounded-[1.6rem] border border-black/5 bg-white p-5">
					<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
						{model.chartFrame.title}
					</p>
					<div className="mt-4">
						<MetricChart
							emptyState={model.chartFrame.emptyState}
							series={model.overview.charts}
							title={model.chartFrame.title}
						/>
					</div>
				</div>
				<div className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5">
					<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
						Fleet summary
					</p>
					<div className="mt-4 grid gap-3 md:grid-cols-4">
						<div className="rounded-[1rem] bg-white px-4 py-3">
							<p className="text-sm text-[var(--muted)]">Healthy</p>
							<p className="mt-2 text-2xl font-semibold">
								{model.overview.summary.healthy_instances}
							</p>
						</div>
						<div className="rounded-[1rem] bg-white px-4 py-3">
							<p className="text-sm text-[var(--muted)]">Unhealthy</p>
							<p className="mt-2 text-2xl font-semibold">
								{model.overview.summary.unhealthy_instances}
							</p>
						</div>
						<div className="rounded-[1rem] bg-white px-4 py-3">
							<p className="text-sm text-[var(--muted)]">Observed window</p>
							<p className="mt-2 text-2xl font-semibold">{model.overview.window}</p>
						</div>
						<div className="rounded-[1rem] bg-white px-4 py-3">
							<p className="text-sm text-[var(--muted)]">Engines observed</p>
							<p className="mt-2 text-2xl font-semibold">{model.engineSummaries.length}</p>
						</div>
					</div>
					<div className="mt-4 grid gap-3 md:grid-cols-2">
						{model.engineSummaries.map((summary) => (
							<div className="rounded-[1rem] bg-white px-4 py-3" key={summary.title}>
								<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
									{summary.title}
								</p>
								<p className="mt-2 text-xl font-semibold">{summary.value}</p>
								<p className="mt-2 text-sm text-[var(--muted)]">{summary.detail}</p>
							</div>
						))}
					</div>
				</div>
				<div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
					<section className="rounded-[1.6rem] border border-black/5 bg-white p-5">
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Capacity outlook
						</p>
						<div className="mt-4 grid gap-3 md:grid-cols-3">
							{model.capacityInsights.map((insight) => (
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
					</section>
					<section className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5">
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Signal leaders
						</p>
						{model.capacityLeaders.length === 0 ? (
							<p className="mt-4 rounded-[1.2rem] bg-white px-4 py-4 text-sm text-[var(--muted)]">
								No overview signal leaders are populated for the observed engines yet. Use the
								coverage boundary above and open individual instances for supported detail
								analytics.
							</p>
						) : (
							<div className="mt-4 space-y-3">
								{model.capacityLeaders.map((leader) => (
									<div className="rounded-[1.2rem] bg-white px-4 py-4" key={leader.title}>
										<div className="flex items-start justify-between gap-3">
											<div>
												<p className="text-sm font-semibold">{leader.title}</p>
												<p className="mt-1 text-sm text-[var(--muted)]">{leader.instanceName}</p>
											</div>
											<p className="text-sm font-semibold text-[var(--accent)]">{leader.value}</p>
										</div>
										<p className="mt-3 text-sm text-[var(--muted)]">{leader.detail}</p>
									</div>
								))}
							</div>
						)}
					</section>
				</div>
			</div>
		</AppChrome>
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
