import type { TablespaceHistoryEntryResponse } from "@db-monitor/api-client";

import { TablespaceTable } from "../_components/tablespace-table";
import { buildTablespaceViewModel } from "../../../../src/tablespaces-ui";
import { createServerApiClient } from "../../../../src/server-api";

interface TablespacesPageProps {
	readonly params: Promise<{
		readonly instanceId: string;
	}>;
}

const HOURS_PER_DAY = 24;
const MILLIS_PER_HOUR = 60 * 60 * 1000;

export default async function TablespacesPage({ params }: TablespacesPageProps) {
	const { instanceId } = await params;
	const apiClient = await createServerApiClient();
	const [instance, snapshot] = await Promise.all([
		apiClient.getInstance(instanceId),
		apiClient.listTablespaces(instanceId),
	]);
	if (instance.engine !== "oracle") {
		return <EngineUnsupportedNotice />;
	}
	const model = buildTablespaceViewModel(snapshot);
	const sparklineByName = await loadSparklineHistory({
		apiClient,
		instanceId,
		tablespaceNames: model.rows.map((row) => row.tablespace_name),
	});

	return (
		<section aria-labelledby="tablespaces-heading" className="space-y-4">
			<header className="flex flex-wrap items-baseline justify-between gap-3">
				<div>
					<h2 className="text-2xl font-semibold" id="tablespaces-heading">
						表空间
					</h2>
					<p className="mt-1 text-sm text-[var(--muted)]">
						最新采集: <span className="font-mono">{model.snapshotLabel}</span>
					</p>
				</div>
				<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
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
				<EmptySnapshotNotice />
			)}
		</section>
	);
}

function EngineUnsupportedNotice() {
	return (
		<section className="rounded-2xl border border-black/10 bg-white p-6 text-sm text-[var(--muted)]">
			仅 Oracle 实例支持表空间视图。
		</section>
	);
}

function EmptySnapshotNotice() {
	return (
		<section className="rounded-2xl border border-black/10 bg-white p-6 text-sm text-[var(--muted)]">
			采集任务尚未上报表空间数据，请稍后刷新。
		</section>
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
			const response = await input.apiClient.getTablespaceHistory(
				input.instanceId,
				name,
				{ from, to },
			);
			return [name, response.entries] as const;
		}),
	);
	return new Map(pairs);
}
