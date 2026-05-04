import { PageContent } from "@db-monitor/ui";

import { createServerApiClient } from "../../../../src/server-api";
import {
	buildSlowQueryFilterValues,
	buildSlowQueryViewModel,
	toSlowQueryApiFilters,
} from "../../../../src/slow-queries-ui";
import { SlowQueryEmptyStateBanner } from "../_components/slow-query-empty-state";
import { SlowQueryFilterForm } from "../_components/slow-query-filter-form";
import { SlowQueryTable } from "../_components/slow-query-table";

interface SlowQueriesPageProps {
	readonly params: Promise<{ readonly instanceId: string }>;
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

/**
 * Q13 SQL tab（engine=mysql）。MySQL 以外的引擎由 tab 本身保持可见，但内容会是
 * "当前引擎不支持" 提示（avoid 404，保 URL 深链）。
 */
export default async function SlowQueriesPage({ params, searchParams }: SlowQueriesPageProps) {
	const { instanceId } = await params;
	const resolvedSearchParams = await searchParams;
	const filters = buildSlowQueryFilterValues(resolvedSearchParams);
	const apiClient = await createServerApiClient();
	const [instance, snapshot] = await Promise.all([
		apiClient.getInstance(instanceId),
		apiClient.getInstanceSlowQueries(instanceId, toSlowQueryApiFilters(filters)),
	]);
	if (instance.engine !== "mysql") {
		return (
			<PageContent>
				<div className="px-6 py-6">
					<p className="rounded-md border border-border-subtle bg-surface-overlay px-4 py-3 text-sm text-fg-secondary">
						慢查询视图仅对 MySQL 实例开放。该实例的引擎为 {instance.engine.toUpperCase()}。
					</p>
				</div>
			</PageContent>
		);
	}
	const model = buildSlowQueryViewModel(instance, snapshot, filters);
	const formAction = `/instances/${instanceId}/slow-queries`;

	return (
		<PageContent>
			<section aria-labelledby="slow-queries-heading" className="space-y-4 p-6">
				<header className="flex flex-wrap items-baseline justify-between gap-3">
					<div>
						<h2 className="text-lg font-semibold text-fg-primary" id="slow-queries-heading">
							慢查询
						</h2>
						<p className="mt-1 text-sm text-fg-muted">
							窗口: <span className="font-mono tabular-nums">{model.window.fromAt}</span>
							<span className="mx-2">→</span>
							<span className="font-mono tabular-nums">{model.window.toAt}</span>
						</p>
					</div>
					<p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] tabular-nums text-fg-muted">
						{model.entries.length} events
					</p>
				</header>
				{model.psHint === null ? null : (
					<div
						className="rounded-md border border-sev-warning-border bg-sev-warning-bg px-4 py-3 text-sm text-fg-primary"
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
		</PageContent>
	);
}
