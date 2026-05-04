import type { NotifyHistoryResponse } from "@db-monitor/api-client";
import { EntitySummary, PageContent, type QuickMetricItem, QuickMetrics } from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";

import { NotifyDrawer } from "../../../src/components/notify/notify-drawer";
import { NotifyEmptyState } from "../../../src/components/notify/notify-empty-state";
import {
	NOTIFY_DEFAULT_LIMIT,
	NotifyFilterBar,
	notifyFiltersHasAny,
	parseNotifyFilters,
} from "../../../src/components/notify/notify-filter-bar";
import { NotifyLoadMore } from "../../../src/components/notify/notify-load-more";
import { NotifyShell } from "../../../src/components/notify/notify-shell";
import { NotifyTable } from "../../../src/components/notify/notify-table";
import {
	applyClientFilters,
	summarizeChannels,
} from "../../../src/components/notify/notify-view-model";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

const LIMIT_STEP_MULTIPLIER = 2;
const LIMIT_MAX = 500;

interface NotifyHistoryPageProps {
	readonly searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function NotifyHistoryPage({ searchParams }: NotifyHistoryPageProps) {
	await requireServerSession("/admin/notify-history");
	const params = await searchParams;
	const filters = parseNotifyFilters(params);
	const activeRowKey = typeof params.row === "string" ? params.row : null;

	const apiClient = await createServerApiClient();
	const rawEntries = await apiClient.listNotifyHistory({
		channel: filters.channel.length > 0 ? filters.channel : undefined,
		limit: filters.limit,
		rule_id: filters.ruleId.length > 0 ? filters.ruleId : undefined,
		status: filters.status.length > 0 ? filters.status : undefined,
	});
	// Client-side only: instance_id post-filter (the Feed API accepts channel/status/rule_id only).
	const entries = applyClientFilters(rawEntries, { instanceId: filters.instanceId });

	const t = await getTranslations("notifyHistory");
	const summary = summarizeChannels(entries);

	const breadcrumbs = [
		{ label: t("breadcrumbAdmin"), href: "/admin/notify-history" },
		{ label: t("pageTitle") },
	];

	const metrics: readonly QuickMetricItem[] = [
		{ key: "total", label: t("metricsTotal"), value: String(entries.length) },
		{
			key: "delivered",
			label: t("metricsDelivered"),
			value: String(entries.filter((entry) => entry.status === "delivered").length),
		},
		{
			key: "failed",
			label: t("metricsFailed"),
			value: String(entries.filter((entry) => entry.status === "failed").length),
		},
		{
			key: "skipped",
			label: t("metricsSkipped"),
			value: String(entries.filter((entry) => entry.status === "skipped").length),
		},
		{ key: "channels", label: t("filterChannel"), value: String(summary.rows.length) },
	];

	const emptyVariant = chooseEmptyVariant(entries, rawEntries, notifyFiltersHasAny(filters));
	const nextHref = buildNextHref(filters.limit, params);

	return (
		<NotifyShell breadcrumbs={breadcrumbs}>
			<EntitySummary
				badges={[{ label: "Feed", tone: "info" }]}
				subtitle={t("pageSubtitle")}
				title={t("pageTitle")}
			/>
			<QuickMetrics items={metrics} />
			<PageContent>
				<div className="flex flex-col gap-4">
					<NotifyFilterBar defaults={filters} />
					{entries.length === 0 ? (
						<NotifyEmptyState variant={emptyVariant} />
					) : (
						<>
							<NotifyTable entries={entries} />
							{shouldShowLoadMore(entries.length, filters.limit) ? (
								<NotifyLoadMore nextHref={nextHref} />
							) : null}
						</>
					)}
				</div>
				<NotifyDrawer activeRowKey={activeRowKey} entries={entries} />
			</PageContent>
		</NotifyShell>
	);
}

function chooseEmptyVariant(
	entries: readonly NotifyHistoryResponse[],
	rawEntries: readonly NotifyHistoryResponse[],
	hasFilter: boolean,
): "firstRun" | "filtered" | "busy" {
	if (!hasFilter && rawEntries.length === 0) {
		return "firstRun";
	}
	if (hasFilter && entries.length === 0) {
		return "filtered";
	}
	if (rawEntries.length > 0 && entries.length === 0) {
		return "filtered";
	}
	return "busy";
}

function shouldShowLoadMore(actualCount: number, limit: number): boolean {
	if (limit >= LIMIT_MAX) {
		return false;
	}
	// Heuristic: if the API returned a full page, assume more exist.
	return actualCount >= limit;
}

function buildNextHref(
	currentLimit: number,
	params: Record<string, string | string[] | undefined>,
): string {
	const nextLimit = Math.min(
		LIMIT_MAX,
		Math.max(currentLimit * LIMIT_STEP_MULTIPLIER, NOTIFY_DEFAULT_LIMIT),
	);
	const next = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (key === "limit" || key === "row") {
			continue;
		}
		if (typeof value === "string" && value.length > 0) {
			next.set(key, value);
		}
	}
	next.set("limit", String(nextLimit));
	return `/admin/notify-history?${next.toString()}`;
}
