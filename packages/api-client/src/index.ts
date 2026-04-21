export interface ApiRequestInit {
	readonly body?: string;
	readonly credentials?: "include";
	readonly headers?: Record<string, string>;
	readonly method?: "GET" | "POST" | "PUT";
}

export interface ApiResponse {
	readonly ok: boolean;
	readonly status: number;
	json(): Promise<unknown>;
	text(): Promise<string>;
}

export type FetchLike = (input: string, init?: ApiRequestInit) => Promise<ApiResponse>;

export interface ApiClientConfig {
	readonly baseUrl: string;
	readonly fetchImpl?: FetchLike;
}

export interface OrganizationSummary {
	readonly name: string;
	readonly organization_id: string;
	readonly slug: string;
}

export interface OrganizationMembership {
	readonly organization: OrganizationSummary;
	readonly roles: readonly string[];
}

export interface SessionUser {
	readonly active_organization: OrganizationSummary;
	readonly display_name: string;
	readonly organization_memberships: readonly OrganizationMembership[];
	readonly permissions: readonly string[];
	readonly roles: readonly string[];
	readonly session_id: string;
	readonly user_id: string;
	readonly username: string;
}

export type TimeWindow = "15m" | "1h" | "6h" | "24h";

export interface ValidationResponse {
	readonly checked_at: string;
	readonly detail: string;
	readonly server_version: string | null;
	readonly status: string;
}

export type DatabaseEngine = "mysql" | "oracle";

export interface InstanceResponse {
	readonly connection: {
		readonly database: string;
		readonly host: string;
		readonly port: number;
		readonly username: string;
	};
	readonly created_at: string;
	readonly engine: DatabaseEngine;
	readonly environment: string;
	readonly instance_id: string;
	readonly labels: readonly string[];
	readonly name: string;
	readonly validation: ValidationResponse;
}

export interface CreateInstanceRequest {
	readonly connection: {
		readonly database: string;
		readonly host: string;
		readonly password: string;
		readonly port: number;
		readonly username: string;
	};
	readonly engine: DatabaseEngine;
	readonly environment: string;
	readonly labels: readonly string[];
	readonly name: string;
}

export type CreateMySQLInstanceRequest = Omit<CreateInstanceRequest, "engine">;

export interface ListInstancesFilters {
	readonly environment?: string;
	readonly label?: string;
	readonly name?: string;
	readonly status?: "failed" | "passed";
}

export interface SystemSettingResponse {
	readonly key: string;
	readonly updated_at: string;
	readonly value: string;
}

export interface MetricCardResponse {
	readonly label: string;
	readonly metric_name: string;
	readonly unit: string;
	readonly value: number;
}

export interface ChartPointResponse {
	readonly timestamp: string;
	readonly value: number;
}

export interface MetricSeriesResponse {
	readonly label: string;
	readonly metric_name: string;
	readonly points: readonly ChartPointResponse[];
	readonly unit: string;
}

export interface OverviewInstanceResponse {
	readonly environment: string;
	readonly engine: DatabaseEngine;
	readonly instance_id: string;
	readonly labels: readonly string[];
	readonly name: string;
	readonly qps: number;
	readonly replication_lag_seconds: number;
	readonly status: string;
	readonly threads_connected: number;
	readonly threads_running: number;
}

export interface OverviewResponse {
	readonly bucket_seconds: number;
	readonly cards: readonly MetricCardResponse[];
	readonly charts: readonly MetricSeriesResponse[];
	readonly coverage: {
		readonly detail_analytics_engines: readonly DatabaseEngine[];
		readonly fleet_health_engines: readonly DatabaseEngine[];
		readonly overview_instance_metric_engines: readonly DatabaseEngine[];
		readonly overview_metric_engines: readonly DatabaseEngine[];
	};
	readonly generated_at: string;
	readonly instances: readonly OverviewInstanceResponse[];
	readonly summary: {
		readonly engines: readonly {
			readonly engine: DatabaseEngine;
			readonly healthy_instances: number;
			readonly total_instances: number;
			readonly unhealthy_instances: number;
		}[];
		readonly healthy_instances: number;
		readonly total_instances: number;
		readonly unhealthy_instances: number;
	};
	readonly window: TimeWindow;
}

export interface InstanceTrendResponse {
	readonly bucket_seconds: number;
	readonly cards: readonly MetricCardResponse[];
	readonly charts: readonly MetricSeriesResponse[];
	readonly generated_at: string;
	readonly instance: {
		readonly environment: string;
		readonly instance_id: string;
		readonly labels: readonly string[];
		readonly name: string;
		readonly status: string;
	};
	readonly window: TimeWindow;
}

export interface AlertRuleResponse {
	readonly created_at: string;
	readonly enabled: boolean;
	readonly engine: DatabaseEngine;
	readonly instance_ids: readonly string[];
	readonly metric_name: string;
	readonly name: string;
	readonly operator: string;
	readonly rule_id: string;
	readonly severity: string;
	readonly threshold: number;
}

export interface CreateAlertRuleRequest {
	readonly enabled: boolean;
	readonly engine: DatabaseEngine;
	readonly instance_ids: readonly string[];
	readonly metric_name: string;
	readonly name: string;
	readonly operator: "gt" | "gte" | "lt" | "lte";
	readonly severity: "warning" | "critical";
	readonly threshold: number;
}

export interface ListAlertsFilters {
	readonly instance?: string;
	readonly opened_after?: string;
	readonly opened_before?: string;
	readonly severity?: "critical" | "warning";
	readonly status?: "acknowledged" | "open" | "resolved";
}

export interface AlertRecordResponse {
	readonly alert_id: string;
	readonly acknowledged_at: string | null;
	readonly acknowledged_by_user_id: string | null;
	readonly current_value: number;
	readonly engine: DatabaseEngine;
	readonly instance_id: string;
	readonly last_evaluated_at: string;
	readonly metric_name: string;
	readonly opened_at: string;
	readonly owner_assigned_at: string | null;
	readonly owner_user_id: string | null;
	readonly resolved_at: string | null;
	readonly rule_id: string;
	readonly rule_name: string;
	readonly severity: string;
	readonly status: string;
	readonly threshold: number;
}

export interface AssignAlertOwnerRequest {
	readonly owner_user_id: string;
}

export interface AlertMetricCatalogEntryResponse {
	readonly label: string;
	readonly metric_name: string;
	readonly unit: string;
}

export interface AlertEngineCatalogResponse {
	readonly engine: DatabaseEngine;
	readonly metrics: readonly AlertMetricCatalogEntryResponse[];
}

export interface AddAlertNoteRequest {
	readonly note: string;
}

export interface AlertDetailResponse {
	readonly history: readonly {
		readonly alert_id: string;
		readonly detail: string;
		readonly event_type: string;
		readonly occurred_at: string;
	}[];
	readonly record: AlertRecordResponse;
}

export interface ApiClient {
	readonly baseUrl: string;
	readonly contractVersion: string;
	acknowledgeAlert(alertId: string): Promise<AlertDetailResponse>;
	addAlertNote(alertId: string, request: AddAlertNoteRequest): Promise<AlertDetailResponse>;
	assignAlertOwner(alertId: string, request: AssignAlertOwnerRequest): Promise<AlertDetailResponse>;
	createInstance(request: CreateInstanceRequest): Promise<InstanceResponse>;
	createMySQLInstance(request: CreateMySQLInstanceRequest): Promise<InstanceResponse>;
	createRule(request: CreateAlertRuleRequest): Promise<AlertRuleResponse>;
	getAlert(alertId: string): Promise<AlertDetailResponse>;
	getInstance(instanceId: string): Promise<InstanceResponse>;
	getMySQLInstance(instanceId: string): Promise<InstanceResponse>;
	getInstanceTrends(instanceId: string, window: TimeWindow): Promise<InstanceTrendResponse>;
	getOverview(window: TimeWindow): Promise<OverviewResponse>;
	listInstances(filters?: ListInstancesFilters): Promise<readonly InstanceResponse[]>;
	listMySQLInstances(filters?: ListInstancesFilters): Promise<readonly InstanceResponse[]>;
	listAlerts(filters?: ListAlertsFilters): Promise<readonly AlertRecordResponse[]>;
	listRuleCatalog(): Promise<readonly AlertEngineCatalogResponse[]>;
	listRules(): Promise<readonly AlertRuleResponse[]>;
	listSettings(): Promise<readonly SystemSettingResponse[]>;
	login(credentials: {
		readonly password: string;
		readonly username: string;
	}): Promise<SessionUser>;
	logout(): Promise<void>;
	me(): Promise<SessionUser>;
	updateSetting(key: string, value: string): Promise<SystemSettingResponse>;
}

export const API_CONTRACT_VERSION = "0.8.0";
export const apiClientPackageName = "@db-monitor/api-client";

export function createApiClient(config: ApiClientConfig): ApiClient {
	const request = buildRequester(config);
	return {
		baseUrl: trimTrailingSlash(config.baseUrl),
		contractVersion: API_CONTRACT_VERSION,
		acknowledgeAlert: (alertId) =>
			request<AlertDetailResponse>(`/alerts/${alertId}/acknowledge`, {
				method: "POST",
			}),
		addAlertNote: (alertId, payload) =>
			request<AlertDetailResponse>(`/alerts/${alertId}/notes`, {
				body: JSON.stringify(payload),
				method: "POST",
			}),
		assignAlertOwner: (alertId, payload) =>
			request<AlertDetailResponse>(`/alerts/${alertId}/owner`, {
				body: JSON.stringify(payload),
				method: "PUT",
			}),
		createInstance: (payload) =>
			request<InstanceResponse>("/control/instances", {
				body: JSON.stringify(payload),
				method: "POST",
			}),
		createMySQLInstance: (payload) =>
			request<InstanceResponse>("/control/mysql-instances", {
				body: JSON.stringify(payload),
				method: "POST",
			}),
		createRule: (payload) =>
			request<AlertRuleResponse>("/alerts/rules", {
				body: JSON.stringify(payload),
				method: "POST",
			}),
		getAlert: (alertId) => request<AlertDetailResponse>(`/alerts/${alertId}`),
		getInstance: (instanceId) => request<InstanceResponse>(`/control/instances/${instanceId}`),
		getMySQLInstance: (instanceId) =>
			request<InstanceResponse>(`/control/mysql-instances/${instanceId}`),
		getInstanceTrends: (instanceId, window) =>
			request<InstanceTrendResponse>(`/analytics/instances/${instanceId}/trends?window=${window}`),
		getOverview: (window) => request<OverviewResponse>(`/analytics/overview?window=${window}`),
		listInstances: (filters) =>
			request<readonly InstanceResponse[]>(`/control/instances${buildQueryString(filters)}`),
		listMySQLInstances: (filters) =>
			request<readonly InstanceResponse[]>(
				`/control/mysql-instances${buildQueryString(filters)}`,
			),
		listAlerts: (filters) =>
			request<readonly AlertRecordResponse[]>(`/alerts${buildQueryString(filters)}`),
		listRuleCatalog: () => request<readonly AlertEngineCatalogResponse[]>("/alerts/rule-catalog"),
		listRules: () => request<readonly AlertRuleResponse[]>("/alerts/rules"),
		listSettings: () => request<readonly SystemSettingResponse[]>("/control/settings"),
		login: (credentials) =>
			request<SessionUser>("/auth/login", {
				body: JSON.stringify(credentials),
				method: "POST",
			}),
		logout: async () => {
			await request<void>("/auth/logout", { method: "POST" });
		},
		me: () => request<SessionUser>("/auth/me"),
		updateSetting: (key, value) =>
			request<SystemSettingResponse>(`/control/settings/${key}`, {
				body: JSON.stringify({ value }),
				method: "PUT",
			}),
	};
}

function buildQueryString(
	filters: ListAlertsFilters | ListInstancesFilters | undefined,
): string {
	if (filters === undefined) {
		return "";
	}
	const params = new URLSearchParams();
	for (const [key, rawValue] of Object.entries(filters)) {
		if (rawValue === undefined) {
			continue;
		}
		const value = String(rawValue).trim();
		if (value.length === 0) {
			continue;
		}
		params.set(key, value);
	}
	const queryString = params.toString();
	return queryString.length === 0 ? "" : `?${queryString}`;
}

function buildRequester(config: ApiClientConfig) {
	const fetchImpl = config.fetchImpl ?? defaultFetch;
	const baseUrl = trimTrailingSlash(config.baseUrl);

	return async function request<T>(path: string, init: ApiRequestInit = {}): Promise<T> {
		const response = await fetchImpl(`${baseUrl}${path}`, {
			body: init.body,
			credentials: init.credentials ?? "include",
			headers: {
				"Content-Type": "application/json",
				...init.headers,
			},
			method: init.method ?? "GET",
		});
		if (!response.ok) {
			throw new Error(await response.text());
		}
		if (response.status === 204) {
			return undefined as T;
		}
		return (await response.json()) as T;
	};
}

function trimTrailingSlash(value: string): string {
	return value.endsWith("/") ? value.slice(0, -1) : value;
}

async function defaultFetch(input: string, init?: ApiRequestInit): Promise<ApiResponse> {
	const runtimeFetch = globalThis.fetch as FetchLike | undefined;
	if (runtimeFetch === undefined) {
		throw new Error("No fetch implementation is available for the API client.");
	}
	return runtimeFetch(input, init);
}
