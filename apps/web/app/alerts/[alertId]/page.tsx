import type { BreadcrumbItem } from "@db-monitor/ui";

import { AlertDrawer } from "../../../src/components/alerts/alert-drawer";
import { toAlertTabKey } from "../../../src/components/alerts/alert-view-model";
import { AlertsAppShell } from "../../../src/components/alerts/alerts-app-shell";
import { AlertsPageShell } from "../../../src/components/alerts/alerts-page-shell";
import { buildAlertListFilterValues } from "../../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

const BREADCRUMBS: readonly BreadcrumbItem[] = [
	{ label: "告警", href: "/alerts" },
	{ label: "告警详情" },
];

interface AlertDetailPageProps {
	readonly params: Promise<{
		readonly alertId: string;
	}>;
	readonly searchParams: Promise<{
		readonly instance?: string;
		readonly opened_after?: string;
		readonly opened_before?: string;
		readonly severity?: string;
		readonly status?: string;
		readonly tab?: string;
	}>;
}

export default async function AlertDetailPage({ params, searchParams }: AlertDetailPageProps) {
	const { alertId } = await params;
	const session = await requireServerSession(`/alerts/${alertId}`);
	const query = await searchParams;
	const filters = buildAlertListFilterValues(query);
	const tab = toAlertTabKey(query.tab);
	const apiClient = await createServerApiClient();
	const [alerts, alertDetail] = await Promise.all([
		apiClient.listAlerts({
			instance: emptyToUndefined(filters.instance),
			opened_after: emptyToUndefined(filters.opened_after),
			opened_before: emptyToUndefined(filters.opened_before),
			severity: emptyToUndefined(filters.severity),
			status: emptyToUndefined(filters.status),
		}),
		apiClient.getAlert(alertId),
	]);

	const queryString = buildQueryString({ filters, tab });
	const listHref = queryString.length === 0 ? "/alerts" : `/alerts?${queryString}`;

	return (
		<AlertsAppShell session={session} breadcrumbs={BREADCRUMBS}>
			<AlertsPageShell
				alerts={alerts}
				baseHref={listHref}
				buildDrawerHref={(nextAlertId) => buildDrawerHref(nextAlertId, queryString)}
				buildTabHref={(nextTab) => buildTabHref(nextTab, filters)}
				drawerSlot={<AlertDrawer alertDetail={alertDetail} alerts={alerts} closeHref={listHref} />}
				filters={filters}
				isDetail={true}
				tab={tab}
			/>
		</AlertsAppShell>
	);
}

function emptyToUndefined<T extends string>(value: T | ""): T | undefined {
	return value.length === 0 ? undefined : (value as T);
}

function buildQueryString(options: {
	readonly filters: ReturnType<typeof buildAlertListFilterValues>;
	readonly tab: string;
}): string {
	const params = new URLSearchParams();
	const { filters, tab } = options;
	if (filters.instance.length > 0) {
		params.set("instance", filters.instance);
	}
	if (filters.opened_after.length > 0) {
		params.set("opened_after", filters.opened_after);
	}
	if (filters.opened_before.length > 0) {
		params.set("opened_before", filters.opened_before);
	}
	if (filters.severity.length > 0) {
		params.set("severity", filters.severity);
	}
	if (filters.status.length > 0) {
		params.set("status", filters.status);
	}
	if (tab !== "active") {
		params.set("tab", tab);
	}
	return params.toString();
}

function buildDrawerHref(alertId: string, queryString: string): string {
	return queryString.length === 0 ? `/alerts/${alertId}` : `/alerts/${alertId}?${queryString}`;
}

function buildTabHref(tab: string, filters: ReturnType<typeof buildAlertListFilterValues>): string {
	const params = new URLSearchParams();
	if (filters.instance.length > 0) {
		params.set("instance", filters.instance);
	}
	if (filters.opened_after.length > 0) {
		params.set("opened_after", filters.opened_after);
	}
	if (filters.opened_before.length > 0) {
		params.set("opened_before", filters.opened_before);
	}
	if (filters.severity.length > 0) {
		params.set("severity", filters.severity);
	}
	if (filters.status.length > 0) {
		params.set("status", filters.status);
	}
	if (tab !== "active") {
		params.set("tab", tab);
	}
	const query = params.toString();
	return query.length === 0 ? "/alerts" : `/alerts?${query}`;
}
