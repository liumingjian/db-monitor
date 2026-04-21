import {
	type ApiClient,
	type ApiResponse,
	type TimeWindow,
	createApiClient,
} from "@db-monitor/api-client";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { LOGIN_ROUTE, type SessionSnapshot } from "./auth";

type CookieStore = Awaited<ReturnType<typeof cookies>>;

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
export const API_BASE_URL_ENV = "DB_MONITOR_API_BASE_URL";
export const DEFAULT_TIME_WINDOW: TimeWindow = "1h";
export const APPROVED_TIME_WINDOWS = ["15m", "1h", "6h", "24h"] as const satisfies readonly TimeWindow[];

export async function createServerApiClient(): Promise<ApiClient> {
	const cookieHeader = buildCookieHeader(await cookies());
	return createApiClient({
		baseUrl: getServerApiBaseUrl(),
		fetchImpl: async (input, init) => {
			const response = await fetch(input, {
				body: init?.body,
				cache: "no-store",
				credentials: init?.credentials,
				headers: {
					...init?.headers,
					...(cookieHeader === undefined ? {} : { cookie: cookieHeader }),
				},
				method: init?.method,
			});
			return response as unknown as ApiResponse;
		},
	});
}

export async function fetchServerSession(): Promise<SessionSnapshot | null> {
	const apiClient = await createServerApiClient();
	try {
		const session = await apiClient.me();
		return {
			activeOrganization: session.active_organization,
			displayName: session.display_name,
			isAuthenticated: true,
			organizationMemberships: session.organization_memberships,
			username: session.username,
		};
	} catch {
		return null;
	}
}

export async function requireServerSession(pathname: string): Promise<SessionSnapshot> {
	const session = await fetchServerSession();
	if (session !== null) {
		return session;
	}
	redirect(`${LOGIN_ROUTE}?next=${encodeURIComponent(pathname)}`);
}

export function getServerApiBaseUrl(): string {
	return process.env[API_BASE_URL_ENV] ?? DEFAULT_API_BASE_URL;
}

export function parseTimeWindow(value: string | undefined): TimeWindow {
	return APPROVED_TIME_WINDOWS.includes(value as TimeWindow)
		? (value as TimeWindow)
		: DEFAULT_TIME_WINDOW;
}

function buildCookieHeader(cookieStore: CookieStore): string | undefined {
	const cookies = cookieStore
		.getAll()
		.map((cookie) => `${cookie.name}=${cookie.value}`)
		.join("; ");
	return cookies.length === 0 ? undefined : cookies;
}
