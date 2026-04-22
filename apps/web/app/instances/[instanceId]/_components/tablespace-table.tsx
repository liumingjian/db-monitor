import Link from "next/link";

import type { TablespaceHistoryEntryResponse } from "@db-monitor/api-client";

import {
	bandLabel,
	formatBytes,
	type TablespaceRow,
} from "../../../../src/tablespaces-ui";
import { TablespaceBar } from "./tablespace-bar";
import { TablespaceSparkline } from "./tablespace-sparkline";

interface TablespaceTableProps {
	readonly rows: readonly TablespaceRow[];
	readonly instanceId: string;
	readonly sparklineByName: ReadonlyMap<string, readonly TablespaceHistoryEntryResponse[]>;
}

export function TablespaceTable({
	instanceId,
	rows,
	sparklineByName,
}: TablespaceTableProps) {
	return (
		<div className="overflow-x-auto rounded-2xl border border-black/10 bg-white">
			<table className="min-w-full text-left text-sm">
				<thead className="bg-black/5 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
					<tr>
						<th className="px-4 py-3">表空间</th>
						<th className="px-4 py-3">状态</th>
						<th className="px-4 py-3">已用</th>
						<th className="px-4 py-3">总计</th>
						<th className="px-4 py-3">使用率</th>
						<th className="px-4 py-3">24 小时趋势</th>
						<th className="px-4 py-3">告警</th>
					</tr>
				</thead>
				<tbody>
					{rows.map((row) => (
						<TablespaceRowView
							history={sparklineByName.get(row.tablespace_name) ?? []}
							instanceId={instanceId}
							key={row.tablespace_name}
							row={row}
						/>
					))}
				</tbody>
			</table>
		</div>
	);
}

interface TablespaceRowViewProps {
	readonly row: TablespaceRow;
	readonly instanceId: string;
	readonly history: readonly TablespaceHistoryEntryResponse[];
}

function TablespaceRowView({ history, instanceId, row }: TablespaceRowViewProps) {
	const trendHref = `/instances/${instanceId}/tablespaces/${encodeURIComponent(row.tablespace_name)}/trend`;
	return (
		<tr className="border-t border-black/5">
			<td className="px-4 py-3 font-mono text-sm">
				<Link className="underline hover:text-[var(--accent)]" href={trendHref}>
					{row.tablespace_name}
				</Link>
			</td>
			<td className="px-4 py-3 text-xs uppercase tracking-[0.12em] text-[var(--muted)]">
				{row.status}
				{row.autoextensible ? (
					<span className="ml-2 rounded-full bg-black/5 px-2 py-0.5 text-[10px] text-[var(--muted)]">
						自动扩展
					</span>
				) : null}
			</td>
			<td className="px-4 py-3 tabular-nums">{formatBytes(row.used_bytes)}</td>
			<td className="px-4 py-3 tabular-nums">{formatBytes(row.total_bytes)}</td>
			<td className="px-4 py-3">
				<TablespaceBar band={row.band} percent={row.used_rate_percent} />
			</td>
			<td className="px-4 py-3">
				<TablespaceSparkline history={history} />
			</td>
			<td className="px-4 py-3 text-xs uppercase tracking-[0.12em]">
				<span
					className={
						row.band === "critical"
							? "text-red-500"
							: row.band === "warning"
							? "text-amber-500"
							: "text-emerald-500"
					}
				>
					{bandLabel(row.band)}
				</span>
			</td>
		</tr>
	);
}
