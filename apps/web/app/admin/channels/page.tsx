import type { NotifyHistoryResponse } from "@db-monitor/api-client";
import {
	EntityBadge,
	EntitySummary,
	PageContent,
	type QuickMetricItem,
	QuickMetrics,
	formatRelativeTime,
} from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";
import Link from "next/link";

import { NotifyShell } from "../../../src/components/notify/notify-shell";
import {
	type ChannelSummaryRow,
	summarizeChannels,
	toChannelHealthKey,
	toChannelHealthTone,
} from "../../../src/components/notify/notify-view-model";
import { groupForHref, rootHrefForGroup } from "../../../src/components/shell/sidebar-groups";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

const CHANNEL_SNAPSHOT_LIMIT = 200;
const CATALOG_ITEM_KEYS: readonly string[] = [
	"catalogFeishu",
	"catalogSmtp",
	"catalogWecom",
	"catalogSms",
];

export default async function ChannelsPage() {
	await requireServerSession("/admin/channels");
	const apiClient = await createServerApiClient();
	const entries = await apiClient.listNotifyHistory({ limit: CHANNEL_SNAPSHOT_LIMIT });
	const summary = summarizeChannels(entries);
	const t = await getTranslations("channels");
	const tNav = await getTranslations("nav");

	const rootGroup = groupForHref("/admin/channels");
	const breadcrumbs = [
		{ label: tNav(rootGroup), href: rootHrefForGroup(rootGroup) },
		{ label: t("pageTitle") },
	];

	const metrics: readonly QuickMetricItem[] = [
		{ key: "registered", label: t("metricsRegistered"), value: String(summary.rows.length) },
		{ key: "active", label: t("metricsActive"), value: String(summary.activeCount) },
		{ key: "healthy", label: t("metricsHealthy"), value: String(summary.healthyCount) },
		{ key: "degraded", label: t("metricsDegraded"), value: String(summary.degradedCount) },
	];

	return (
		<NotifyShell breadcrumbs={breadcrumbs}>
			<EntitySummary
				badges={[{ label: "Read-only", tone: "warning" }]}
				subtitle={t("pageSubtitle")}
				title={t("pageTitle")}
			/>
			<QuickMetrics items={metrics} />
			<PageContent>
				<div className="flex flex-col gap-4">
					<ReadOnlyBanner message={t("readOnlyBanner")} hint={t("readOnlyBannerHint")} />
					<BindingSection entries={entries} rows={summary.rows} />
					<CatalogSection keys={CATALOG_ITEM_KEYS} />
				</div>
			</PageContent>
		</NotifyShell>
	);
}

function ReadOnlyBanner({ hint, message }: { hint: string; message: string }) {
	return (
		<div className="rounded-md border border-sev-warning-border bg-bg-elevated p-4 text-sev-warning">
			<p className="text-sm font-semibold">{message}</p>
			<p className="mt-1 text-xs text-fg-muted">{hint}</p>
		</div>
	);
}

async function BindingSection({
	entries,
	rows,
}: {
	readonly entries: readonly NotifyHistoryResponse[];
	readonly rows: readonly ChannelSummaryRow[];
}) {
	const t = await getTranslations("channels");
	return (
		<section className="rounded-md border border-border-hairline bg-bg-elevated">
			<header className="border-b border-border-hairline px-5 py-3">
				<h2 className="text-sm font-semibold text-fg-primary">{t("bindingSectionTitle")}</h2>
				<p className="mt-1 text-xs text-fg-muted">{t("bindingSectionHint")}</p>
			</header>
			{rows.length === 0 ? <EmptyBindings /> : <BindingTable entries={entries} rows={rows} />}
		</section>
	);
}

async function EmptyBindings() {
	const t = await getTranslations("channels");
	return (
		<div className="border-t border-border-hairline px-5 py-10 text-center">
			<p className="text-sm font-medium text-fg-primary">{t("emptyTitle")}</p>
			<p className="mt-1 text-xs text-fg-muted">{t("emptyHint")}</p>
		</div>
	);
}

async function BindingTable({
	entries,
	rows,
}: {
	readonly entries: readonly NotifyHistoryResponse[];
	readonly rows: readonly ChannelSummaryRow[];
}) {
	const t = await getTranslations("channels");
	return (
		<div className="overflow-x-auto">
			<table className="w-full min-w-[720px] border-collapse text-left text-sm">
				<thead className="border-b border-border-hairline text-[11px] uppercase tracking-widest text-fg-muted">
					<tr>
						<th className="px-4 py-2 font-medium">{t("columnChannel")}</th>
						<th className="px-4 py-2 font-medium">{t("columnStatus")}</th>
						<th className="px-4 py-2 font-medium">{t("columnLastAttempt")}</th>
						<th className="px-4 py-2 font-medium">{t("columnDelivered")}</th>
						<th className="px-4 py-2 font-medium">{t("columnFailed")}</th>
						<th className="px-4 py-2 font-medium">{t("columnSkipped")}</th>
						<th className="px-4 py-2 font-medium" aria-label={t("viewHistory")} />
					</tr>
				</thead>
				<tbody>
					{rows.map((row) => (
						<BindingRow entries={entries} key={row.channel} row={row} />
					))}
				</tbody>
			</table>
		</div>
	);
}

async function BindingRow({
	entries,
	row,
}: {
	readonly entries: readonly NotifyHistoryResponse[];
	readonly row: ChannelSummaryRow;
}) {
	const t = await getTranslations("channels");
	const tone = toChannelHealthTone(row);
	const statusKey = toChannelHealthKey(row);
	const statusLabel = t(`status${statusKey.charAt(0).toUpperCase()}${statusKey.slice(1)}`);
	// intentionally marks the entries prop as used so callers that pre-fetch stay honest;
	// the link below surfaces the full Feed view for this channel.
	void entries;
	return (
		<tr className="border-b border-border-hairline last:border-b-0">
			<td className="px-4 py-2 font-mono">{row.channel}</td>
			<td className="px-4 py-2">
				<EntityBadge label={statusLabel} tone={tone} />
			</td>
			<td className="px-4 py-2 font-mono text-xs text-fg-muted" title={row.lastAttemptedAt ?? ""}>
				{row.lastAttemptedAt ? formatRelativeTime(row.lastAttemptedAt) : "—"}
			</td>
			<td className="px-4 py-2 font-mono tabular-nums">{row.delivered}</td>
			<td className="px-4 py-2 font-mono tabular-nums text-sev-critical">{row.failed}</td>
			<td className="px-4 py-2 font-mono tabular-nums text-fg-muted">{row.skipped}</td>
			<td className="px-4 py-2 text-right">
				<Link
					className="text-xs font-medium text-accent hover:underline"
					href={`/admin/notify-history?channel=${encodeURIComponent(row.channel)}`}
				>
					{t("viewHistory")}
				</Link>
			</td>
		</tr>
	);
}

async function CatalogSection({ keys }: { readonly keys: readonly string[] }) {
	const t = await getTranslations("channels");
	return (
		<section className="rounded-md border border-border-hairline bg-bg-elevated">
			<header className="border-b border-border-hairline px-5 py-3">
				<h2 className="text-sm font-semibold text-fg-primary">{t("catalogTitle")}</h2>
				<p className="mt-1 text-xs text-fg-muted">{t("catalogNote")}</p>
			</header>
			<ul className="grid gap-3 p-5 md:grid-cols-2">
				{keys.map((key) => (
					<li
						className="rounded-md border border-border-hairline bg-bg-base p-3 text-sm text-fg-primary"
						key={key}
					>
						{t(key)}
					</li>
				))}
			</ul>
		</section>
	);
}
