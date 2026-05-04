import type { ProcesslistEntryResponse } from "@db-monitor/api-client";

import { type KillRowState, resolveKillRowState } from "../../../../src/processlist-ui";
import { KillProcessDialog } from "./kill-process-dialog";

interface ProcesslistTableProps {
	readonly canKill: boolean;
	readonly entries: readonly ProcesslistEntryResponse[];
	readonly instanceId: string;
	readonly monitorUsername: string;
	readonly validationPassed: boolean;
}

const BASE_COLUMN_HEADERS: readonly { readonly key: string; readonly label: string }[] = [
	{ key: "process_id", label: "PID" },
	{ key: "user", label: "User" },
	{ key: "host", label: "Host" },
	{ key: "db", label: "DB" },
	{ key: "command", label: "Command" },
	{ key: "time_seconds", label: "Time (s)" },
	{ key: "state", label: "State" },
	{ key: "info", label: "Info" },
];

export function ProcesslistTable({
	canKill,
	entries,
	instanceId,
	monitorUsername,
	validationPassed,
}: ProcesslistTableProps) {
	const headers = canKill
		? [...BASE_COLUMN_HEADERS, { key: "actions", label: "Actions" }]
		: BASE_COLUMN_HEADERS;
	return (
		<div className="overflow-x-auto rounded-[1.2rem] border border-black/5 bg-white">
			<table className="min-w-full border-collapse text-left text-sm">
				<thead className="bg-[var(--panel)] text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
					<tr>
						{headers.map((column) => (
							<th className="px-4 py-3" key={column.key} scope="col">
								{column.label}
							</th>
						))}
					</tr>
				</thead>
				<tbody>
					{entries.map((entry) => (
						<ProcesslistTableRow
							canKill={canKill}
							entry={entry}
							instanceId={instanceId}
							key={`${entry.process_id}-${entry.host}`}
							killState={resolveKillRowState({
								entryUser: entry.user,
								monitorUsername,
								validationPassed,
							})}
						/>
					))}
				</tbody>
			</table>
		</div>
	);
}

interface ProcesslistTableRowProps {
	readonly canKill: boolean;
	readonly entry: ProcesslistEntryResponse;
	readonly instanceId: string;
	readonly killState: KillRowState;
}

function ProcesslistTableRow({ canKill, entry, instanceId, killState }: ProcesslistTableRowProps) {
	return (
		<tr className="border-t border-black/5">
			<td className="px-4 py-3 font-mono text-xs text-[var(--ink)]">{entry.process_id}</td>
			<td className="px-4 py-3 text-[var(--ink)]">{entry.user}</td>
			<td className="px-4 py-3 font-mono text-xs text-[var(--muted)]">{entry.host}</td>
			<td className="px-4 py-3 text-[var(--muted)]">{entry.db || "—"}</td>
			<td className="px-4 py-3 text-[var(--ink)]">{entry.command}</td>
			<td className="px-4 py-3 font-mono text-xs text-[var(--ink)]">{entry.time_seconds}</td>
			<td className="px-4 py-3 text-[var(--muted)]">{entry.state || "—"}</td>
			<td className="px-4 py-3 align-top">
				<ProcesslistInfoCell info={entry.info} />
			</td>
			{canKill ? (
				<td className="px-4 py-3 align-top">
					<KillCell entry={entry} instanceId={instanceId} killState={killState} />
				</td>
			) : null}
		</tr>
	);
}

interface KillCellProps {
	readonly entry: ProcesslistEntryResponse;
	readonly instanceId: string;
	readonly killState: KillRowState;
}

function KillCell({ entry, instanceId, killState }: KillCellProps) {
	if (killState.disabled) {
		return (
			<button
				className="rounded-[0.7rem] border border-black/10 bg-white px-3 py-1 text-xs font-semibold text-[var(--muted)] opacity-60"
				disabled
				title={killState.reason ?? undefined}
				type="button"
			>
				Kill
			</button>
		);
	}
	return (
		<KillProcessDialog instanceId={instanceId} processId={entry.process_id} user={entry.user} />
	);
}

interface ProcesslistInfoCellProps {
	readonly info: string;
}

function ProcesslistInfoCell({ info }: ProcesslistInfoCellProps) {
	if (info.length === 0) {
		return <span className="text-[var(--muted)]">—</span>;
	}
	return (
		<details className="max-w-[28rem] text-xs text-[var(--ink)]">
			<summary className="cursor-pointer truncate font-mono text-[var(--muted)]" title={info}>
				{truncate(info, 72)}
			</summary>
			<pre className="mt-2 whitespace-pre-wrap break-all rounded-[0.6rem] bg-[var(--panel)] p-3 font-mono text-xs text-[var(--ink)]">
				{info}
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
