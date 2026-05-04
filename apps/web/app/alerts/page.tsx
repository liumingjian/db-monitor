import { toAlertTabKey } from "../../src/components/alerts/alert-view-model";
import { AlertsPageShell } from "../../src/components/alerts/alerts-page-shell";
import { AppChrome } from "../../src/components/app-chrome";
import { buildAlertListFilterValues, buildOperationsModel } from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

interface AlertsPageProps {
	readonly searchParams: Promise<{
		readonly instance?: string;
		readonly opened_after?: string;
		readonly opened_before?: string;
		readonly severity?: string;
		readonly status?: string;
		readonly tab?: string;
	}>;
}

export default async function AlertsPage({ searchParams }: AlertsPageProps) {
	const session = await requireServerSession("/alerts");
	const params = await searchParams;
	const filters = buildAlertListFilterValues(params);
	const tab = toAlertTabKey(params.tab);
	const apiClient = await createServerApiClient();
	const model = buildOperationsModel({
		alertFilters: filters,
		alerts: await apiClient.listAlerts({
			instance: emptyToUndefined(filters.instance),
			opened_after: emptyToUndefined(filters.opened_after),
			opened_before: emptyToUndefined(filters.opened_before),
			severity: emptyToUndefined(filters.severity),
			status: emptyToUndefined(filters.status),
		}),
	});

	const queryString = buildQueryString({ filters, tab });
	const baseHref = queryString.length === 0 ? "/alerts" : `/alerts?${queryString}`;

	return (
		<AppChrome session={session}>
			<AlertsPageShell
				alerts={model.alerts}
				baseHref={baseHref}
				buildDrawerHref={(alertId) => buildDrawerHref(alertId, queryString)}
				buildTabHref={(nextTab) => buildTabHref(nextTab, filters)}
				filters={model.alertFilters}
				isDetail={false}
				tab={tab}
			/>
		</AppChrome>
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
