import type { SlowQueryEntryResponse } from "@db-monitor/api-client";

interface SlowQueryTableProps {
	readonly entries: readonly SlowQueryEntryResponse[];
}

const COLUMN_HEADERS: readonly { readonly key: string; readonly label: string }[] = [
	{ key: "started_at", label: "Started at" },
	{ key: "timer_wait_ms", label: "Duration (ms)" },
	{ key: "user", label: "User" },
	{ key: "schema", label: "Schema" },
	{ key: "rows_examined", label: "Rows examined" },
	{ key: "rows_sent", label: "Rows sent" },
	{ key: "sql_text", label: "SQL" },
];

export function SlowQueryTable({ entries }: SlowQueryTableProps) {
	return (
		<div className="overflow-x-auto rounded-[1.2rem] border border-black/5 bg-white">
			<table className="min-w-full border-collapse text-left text-sm">
				<thead className="bg-[var(--panel)] text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
					<tr>
						{COLUMN_HEADERS.map((column) => (
							<th className="px-4 py-3" key={column.key} scope="col">
								{column.label}
							</th>
						))}
					</tr>
				</thead>
				<tbody>
					{entries.map((entry) => (
						<SlowQueryTableRow entry={entry} key={`${entry.event_id}-${entry.started_at}`} />
					))}
				</tbody>
			</table>
		</div>
	);
}

interface SlowQueryTableRowProps {
	readonly entry: SlowQueryEntryResponse;
}

function SlowQueryTableRow({ entry }: SlowQueryTableRowProps) {
	return (
		<tr className="border-t border-black/5">
			<td className="px-4 py-3 font-mono text-xs text-[var(--muted)]">{entry.started_at}</td>
			<td className="px-4 py-3 font-mono text-xs text-[var(--ink)]">
				{entry.timer_wait_ms.toFixed(1)}
			</td>
			<td className="px-4 py-3 text-[var(--ink)]">{entry.user || "—"}</td>
			<td className="px-4 py-3 text-[var(--muted)]">{entry.schema_name || "—"}</td>
			<td className="px-4 py-3 font-mono text-xs text-[var(--ink)]">{entry.rows_examined}</td>
			<td className="px-4 py-3 font-mono text-xs text-[var(--ink)]">{entry.rows_sent}</td>
			<td className="px-4 py-3 align-top">
				<SlowQuerySqlCell sqlText={entry.sql_text} />
			</td>
		</tr>
	);
}

interface SlowQuerySqlCellProps {
	readonly sqlText: string;
}

function SlowQuerySqlCell({ sqlText }: SlowQuerySqlCellProps) {
	if (sqlText.length === 0) {
		return <span className="text-[var(--muted)]">—</span>;
	}
	return (
		<details className="max-w-[32rem] text-xs text-[var(--ink)]">
			<summary className="cursor-pointer truncate font-mono text-[var(--muted)]" title={sqlText}>
				{truncate(sqlText, 96)}
			</summary>
			<pre className="mt-2 whitespace-pre-wrap break-all rounded-[0.6rem] bg-[var(--panel)] p-3 font-mono text-xs text-[var(--ink)]">
				{sqlText}
			</pre>
		</details>
	);
}

function truncate(value: string, max: number): string {
	if (value.length <= max) {
		return value;
	}
	return `${value.slice(0, max - 1)}…`;
}
