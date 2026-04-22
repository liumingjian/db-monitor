import Link from "next/link";

import { createServerApiClient } from "../../../../../../src/server-api";
import { DEFAULT_HISTORY_DAYS } from "../../../../../../src/tablespaces-ui";
import { TablespaceTrendChart } from "../../../_components/tablespace-trend-chart";

interface TablespaceTrendPageProps {
	readonly params: Promise<{
		readonly instanceId: string;
		readonly tablespaceName: string;
	}>;
}

const MILLIS_PER_DAY = 24 * 60 * 60 * 1000;

export default async function TablespaceTrendPage({ params }: TablespaceTrendPageProps) {
	const { instanceId, tablespaceName } = await params;
	const apiClient = await createServerApiClient();
	const now = Date.now();
	const from = new Date(now - DEFAULT_HISTORY_DAYS * MILLIS_PER_DAY).toISOString();
	const to = new Date(now).toISOString();
	const history = await apiClient.getTablespaceHistory(instanceId, tablespaceName, {
		from,
		to,
	});

	return (
		<section aria-labelledby="tablespace-trend-heading" className="space-y-4">
			<header className="flex items-baseline justify-between gap-4">
				<div>
					<h2 className="text-2xl font-semibold" id="tablespace-trend-heading">
						{tablespaceName}
					</h2>
					<p className="mt-1 text-sm text-[var(--muted)]">近 {DEFAULT_HISTORY_DAYS} 天使用率趋势</p>
				</div>
				<Link
					className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)] underline"
					href={`/instances/${instanceId}/tablespaces`}
				>
					返回列表
				</Link>
			</header>
			<div className="rounded-2xl border border-black/10 bg-white p-4">
				<TablespaceTrendChart history={history.entries} tablespaceName={tablespaceName} />
			</div>
		</section>
	);
}
