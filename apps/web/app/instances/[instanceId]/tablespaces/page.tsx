import type { TablespaceHistoryEntryResponse } from "@db-monitor/api-client";
import { PageContent } from "@db-monitor/ui";

import { createServerApiClient } from "../../../../src/server-api";
import { buildTablespaceViewModel } from "../../../../src/tablespaces-ui";
import { TablespaceTable } from "../_components/tablespace-table";

interface TablespacesPageProps {
	readonly params: Promise<{ readonly instanceId: string }>;
}

const HOURS_PER_DAY = 24;
const MILLIS_PER_HOUR = 60 * 60 * 1000;

/**
 * Q13 存储 tab（engine=oracle）。非 oracle 引擎仍保留 tab 可访问，内容降级为
 * 说明卡（与 slow-queries 的 MySQL 对称）。
 */
export default async function TablespacesPage({ params }: TablespacesPageProps) {
	const { instanceId } = await params;
	const apiClient = await createServerApiClient();
	const [instance, snapshot] = await Promise.all([
		apiClient.getInstance(instanceId),
		apiClient.listTablespaces(instanceId),
	]);
	if (instance.engine !== "oracle") {
		return (
			<PageContent>
				<div className="px-6 py-6">
					<p className="rounded-md border border-border-subtle bg-surface-overlay px-4 py-3 text-sm text-fg-secondary">
						表空间视图仅对 Oracle 实例开放。该实例的引擎为 {instance.engine.toUpperCase()}。
					</p>
				</div>
			</PageContent>
		);
	}
	const model = buildTablespaceViewModel(snapshot);
	const sparklineByName = await loadSparklineHistory({
		apiClient,
		instanceId,
		tablespaceNames: model.rows.map((row) => row.tablespace_name),
	});

	return (
		<PageContent>
			<section aria-labelledby="tablespaces-heading" className="space-y-4 p-6">
				<header className="flex flex-wrap items-baseline justify-between gap-3">
					<div>
						<h2 className="text-lg font-semibold text-fg-primary" id="tablespaces-heading">
							表空间
						</h2>
						<p className="mt-1 text-sm text-fg-muted">
							最新采集: <span className="font-mono tabular-nums">{model.snapshotLabel}</span>
						</p>
					</div>
					<p className="font-mono text-xs font-semibold uppercase tracking-[0.18em] tabular-nums text-fg-muted">
						{model.rows.length} 表空间
					</p>
				</header>
				{model.hasSnapshot ? (
					<TablespaceTable
						instanceId={instanceId}
						rows={model.rows}
						sparklineByName={sparklineByName}
					/>
				) : (
					<p className="rounded-md border border-dashed border-border-subtle bg-bg-elevated px-5 py-8 text-center text-sm text-fg-secondary">
						采集任务尚未上报表空间数据，请稍后刷新。
					</p>
				)}
			</section>
		</PageContent>
	);
}

interface SparklineInput {
	readonly apiClient: Awaited<ReturnType<typeof createServerApiClient>>;
	readonly instanceId: string;
	readonly tablespaceNames: readonly string[];
}

async function loadSparklineHistory(
	input: SparklineInput,
): Promise<ReadonlyMap<string, readonly TablespaceHistoryEntryResponse[]>> {
	const now = Date.now();
	const from = new Date(now - HOURS_PER_DAY * MILLIS_PER_HOUR).toISOString();
	const to = new Date(now).toISOString();
	const pairs = await Promise.all(
		input.tablespaceNames.map(async (name) => {
			const response = await input.apiClient.getTablespaceHistory(input.instanceId, name, {
				from,
				to,
			});
			return [name, response.entries] as const;
		}),
	);
	return new Map(pairs);
}
