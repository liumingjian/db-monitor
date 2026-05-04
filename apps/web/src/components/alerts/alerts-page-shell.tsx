import type { AlertRecordResponse } from "@db-monitor/api-client";
import {
	Button,
	CanonicalPageTemplate,
	EntitySummary,
	PageContent,
	type QuickMetricItem,
	QuickMetrics,
	TabBar,
	type TabItem,
} from "@db-monitor/ui";
import type { ReactNode } from "react";

import type { AlertListFilterValues } from "../../monitoring-ui";
import { AlertFilterChips } from "./alert-filter-chips";
import { AlertList } from "./alert-list";
import { AlertOnCallToggle } from "./alert-oncall-toggle";
import { AlertTimeline } from "./alert-timeline";
import { type AlertTabKey, computeAlertCounts, filterAlertsByTab } from "./alert-view-model";

export interface AlertsPageShellProps {
	readonly alerts: readonly AlertRecordResponse[];
	readonly filters: AlertListFilterValues;
	readonly tab: AlertTabKey;
	readonly isDetail: boolean;
	readonly baseHref: string;
	readonly buildDrawerHref: (alertId: string) => string;
	readonly buildTabHref: (tab: AlertTabKey) => string;
	readonly drawerSlot?: ReactNode;
}

export function AlertsPageShell(props: AlertsPageShellProps) {
	const { alerts, filters, tab, isDetail, baseHref, buildDrawerHref, buildTabHref, drawerSlot } =
		props;
	const counts = computeAlertCounts(alerts);
	const filteredAlerts = filterAlertsByTab(alerts, tab);
	const hasAnyFilter =
		filters.instance.length > 0 ||
		filters.opened_after.length > 0 ||
		filters.opened_before.length > 0 ||
		filters.severity.length > 0 ||
		filters.status.length > 0;

	const tabs: readonly TabItem[] = [
		{ badge: counts.active, href: buildTabHref("active"), key: "active", label: "活跃" },
		{ href: buildTabHref("timeline"), key: "timeline", label: "时间线" },
		{
			badge: counts.acknowledged,
			href: buildTabHref("acknowledged"),
			key: "acknowledged",
			label: "已确认",
		},
		{ badge: counts.resolved, href: buildTabHref("resolved"), key: "resolved", label: "已解决" },
	];

	const metrics: readonly QuickMetricItem[] = [
		{ key: "active", label: "活跃", value: counts.active.toString() },
		{ key: "acknowledged", label: "已确认", value: counts.acknowledged.toString() },
		{ key: "resolved", label: "已解决", value: counts.resolved.toString() },
		{ hint: "紧急级告警", key: "critical", label: "紧急", value: counts.critical.toString() },
	];

	return (
		<CanonicalPageTemplate>
			<EntitySummary
				actions={
					<div className="flex items-center gap-2">
						<AlertOnCallToggle />
						<Button aria-disabled disabled size="sm" title="即将上线" variant="outline">
							告警抑制（即将上线）
						</Button>
					</div>
				}
				badges={[
					{ label: `总 ${counts.total.toString()}`, tone: "info" },
					{ label: `紧急 ${counts.critical.toString()}`, tone: "critical" },
					{ label: `未确认 ${counts.unacknowledged.toString()}`, tone: "warning" },
					{ label: `SLA 破损 ${counts.slaBreach.toString()}`, tone: "critical" },
				]}
				subtitle="实时告警队列、时间线与处置流"
				title="告警"
			/>
			<QuickMetrics items={metrics} />
			<TabBar activeKey={tab} tabs={tabs} />
			<PageContent>
				<AlertFilterChips
					baseHref={baseHref}
					filters={filters}
					matchedCount={filteredAlerts.length}
				/>
				{tab === "timeline" ? (
					<AlertTimeline alerts={filteredAlerts} buildDrawerHref={buildDrawerHref} />
				) : (
					<AlertList
						alerts={filteredAlerts}
						buildDrawerHref={buildDrawerHref}
						hasAnyFilter={hasAnyFilter}
						tab={tab}
					/>
				)}
			</PageContent>
			{drawerSlot}
		</CanonicalPageTemplate>
	);
}
