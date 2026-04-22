import { SlowQueryEmptyStateBanner } from "../_components/slow-query-empty-state";
import { SlowQueryFilterForm } from "../_components/slow-query-filter-form";
import { SlowQueryTable } from "../_components/slow-query-table";
import {
	buildSlowQueryFilterValues,
	buildSlowQueryViewModel,
	toSlowQueryApiFilters,
} from "../../../../src/slow-queries-ui";
import { createServerApiClient } from "../../../../src/server-api";

interface SlowQueriesPageProps {
	readonly params: Promise<{
		readonly instanceId: string;
	}>;
	readonly searchParams: Promise<{
		readonly minDurationMs?: string;
		readonly user?: string;
		readonly schema?: string;
		readonly digestPrefix?: string;
		readonly startedAfter?: string;
		readonly startedBefore?: string;
		readonly limit?: string;
	}>;
}

export default async function SlowQueriesPage({ params, searchParams }: SlowQueriesPageProps) {
	const { instanceId } = await params;
	const resolvedSearchParams = await searchParams;
	const filters = buildSlowQueryFilterValues(resolvedSearchParams);
	const apiClient = await createServerApiClient();
	const [instance, snapshot] = await Promise.all([
		apiClient.getInstance(instanceId),
		apiClient.getInstanceSlowQueries(instanceId, toSlowQueryApiFilters(filters)),
	]);
	const model = buildSlowQueryViewModel(instance, snapshot, filters);
	const formAction = `/instances/${instanceId}/slow-queries`;

	return (
		<section aria-labelledby="slow-queries-heading" className="space-y-4">
			<header className="flex flex-wrap items-baseline justify-between gap-3">
				<div>
					<h2 className="text-2xl font-semibold" id="slow-queries-heading">
						Slow queries
					</h2>
					<p className="mt-1 text-sm text-[var(--muted)]">
						窗口: <span className="font-mono">{model.window.fromAt}</span>
						<span className="mx-2">→</span>
						<span className="font-mono">{model.window.toAt}</span>
					</p>
				</div>
				<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
					{model.entries.length} events
				</p>
			</header>
			{model.psHint === null ? null : (
				<div
					className="rounded-[1.2rem] border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
					data-testid="slow-queries-ps-hint"
				>
					{model.psHint}
				</div>
			)}
			<SlowQueryFilterForm action={formAction} filters={model.filters} />
			{model.emptyState === null ? (
				<SlowQueryTable entries={model.entries} />
			) : (
				<SlowQueryEmptyStateBanner state={model.emptyState} />
			)}
		</section>
	);
}
