"use client";

import type { NotifyHistoryResponse } from "@db-monitor/api-client";
import { formatRelativeTime } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

import { buildRowKey } from "./notify-view-model";
import { NotifyStatusBadge } from "./status-badge";

const DASH = "—";

export interface NotifyTableProps {
	readonly entries: readonly NotifyHistoryResponse[];
}

/**
 * Feed-style notifier delivery table. Row click opens the drawer by pushing
 * ?row=<rowKey> into the URL (shallow navigation, no refetch).
 */
export function NotifyTable({ entries }: NotifyTableProps) {
	const t = useTranslations("notifyHistory");
	const router = useRouter();
	const pathname = usePathname();
	const rawSearchParams = useSearchParams();

	const openRow = useCallback(
		(rowKey: string) => {
			const next = new URLSearchParams(rawSearchParams?.toString() ?? "");
			next.set("row", rowKey);
			router.replace(`${pathname}?${next.toString()}`, { scroll: false });
		},
		[pathname, rawSearchParams, router],
	);

	return (
		<div className="overflow-x-auto rounded-md border border-border-hairline bg-bg-elevated">
			<table className="w-full min-w-[960px] border-collapse text-left text-sm">
				<thead className="border-b border-border-hairline text-[11px] uppercase tracking-widest text-fg-muted">
					<tr>
						<TableHeader label={t("columnChannel")} />
						<TableHeader label={t("columnStatus")} />
						<TableHeader label={t("columnRule")} />
						<TableHeader label={t("columnInstance")} />
						<TableHeader label={t("columnAttempt")} />
						<TableHeader label={t("columnAttemptedAt")} />
						<TableHeader label={t("columnDeliveredAt")} />
						<TableHeader label={t("columnError")} />
					</tr>
				</thead>
				<tbody>
					{entries.map((entry) => {
						const rowKey = buildRowKey(entry);
						return <NotifyTableRow entry={entry} key={rowKey} onOpen={() => openRow(rowKey)} />;
					})}
				</tbody>
			</table>
		</div>
	);
}

function TableHeader({ label }: { label: string }) {
	return <th className="px-3 py-2 font-medium">{label}</th>;
}

interface NotifyTableRowProps {
	readonly entry: NotifyHistoryResponse;
	readonly onOpen: () => void;
}

function NotifyTableRow({ entry, onOpen }: NotifyTableRowProps) {
	const handleKeyDown = (event: React.KeyboardEvent<HTMLTableRowElement>) => {
		if (event.key === "Enter" || event.key === " ") {
			event.preventDefault();
			onOpen();
		}
	};
	return (
		<tr
			className="cursor-pointer border-b border-border-hairline align-top hover:bg-surface-overlay"
			onClick={onOpen}
			onKeyDown={handleKeyDown}
			tabIndex={0}
		>
			<td className="px-3 py-2 font-mono">{entry.channel}</td>
			<td className="px-3 py-2">
				<NotifyStatusBadge status={entry.status} />
			</td>
			<td className="px-3 py-2 font-mono text-xs">{entry.rule_id}</td>
			<td className="px-3 py-2 font-mono text-xs">{entry.instance_id ?? DASH}</td>
			<td className="px-3 py-2 font-mono tabular-nums">{entry.attempt}</td>
			<td className="px-3 py-2 font-mono text-xs text-fg-muted" title={entry.attempted_at}>
				{formatRelativeTime(entry.attempted_at)}
			</td>
			<td className="px-3 py-2 font-mono text-xs text-fg-muted">
				{entry.delivered_at ? (
					<span title={entry.delivered_at}>{formatRelativeTime(entry.delivered_at)}</span>
				) : (
					DASH
				)}
			</td>
			<td className="px-3 py-2 text-xs text-sev-critical">
				{entry.error ? <span className="break-all">{entry.error}</span> : DASH}
			</td>
		</tr>
	);
}
