import { QueryClient } from "@tanstack/react-query";

import {
	API_CONTRACT_VERSION,
	type ApiClient,
	type ApiClientConfig,
	type TimeWindow,
	createApiClient,
} from "@db-monitor/api-client";
import {
	ALERT_TABLE_COLUMNS,
	type ChartFrameContract,
	type FormFieldContract,
	LOGIN_FORM_FIELDS,
	OVERVIEW_CHART_FRAME,
	type TableColumnContract,
} from "@db-monitor/ui";

const QUERY_GC_TIME_MS = 300_000;
const QUERY_RETRY_COUNT = 1;
const QUERY_STALE_TIME_MS = 30_000;

export interface WebDataLayer {
	readonly apiClient: ApiClient;
	readonly chartFrame: ChartFrameContract;
	readonly contractVersion: string;
	readonly formFields: readonly FormFieldContract[];
	readonly queryClient: QueryClient;
	readonly queryKeys: {
		readonly alerts: () => readonly ["alerts", "list"];
		readonly authSession: () => readonly ["auth", "session"];
		readonly instanceTrends: (
			instanceId: string,
			window: TimeWindow,
		) => readonly ["analytics", "instance-trends", string, TimeWindow];
		readonly overview: (window: TimeWindow) => readonly ["analytics", "overview", TimeWindow];
		readonly rules: () => readonly ["alerts", "rules"];
	};
	readonly tableColumns: readonly TableColumnContract[];
}

export function createShellQueryClient(): QueryClient {
	return new QueryClient({
		defaultOptions: {
			queries: {
				gcTime: QUERY_GC_TIME_MS,
				retry: QUERY_RETRY_COUNT,
				staleTime: QUERY_STALE_TIME_MS,
			},
		},
	});
}

export function createWebDataLayer(config: ApiClientConfig): WebDataLayer {
	return {
		apiClient: createApiClient(config),
		chartFrame: OVERVIEW_CHART_FRAME,
		contractVersion: API_CONTRACT_VERSION,
		formFields: LOGIN_FORM_FIELDS,
		queryClient: createShellQueryClient(),
		queryKeys: {
			alerts: () => ["alerts", "list"] as const,
			authSession: () => ["auth", "session"] as const,
			instanceTrends: (instanceId, window) =>
				["analytics", "instance-trends", instanceId, window] as const,
			overview: (window) => ["analytics", "overview", window] as const,
			rules: () => ["alerts", "rules"] as const,
		},
		tableColumns: ALERT_TABLE_COLUMNS,
	};
}
