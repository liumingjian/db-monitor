import { API_CONTRACT_VERSION, apiClientPackageName } from "@db-monitor/api-client";
import {
	type NavigationItem,
	SHELL_NAVIGATION,
	UI_FOUNDATION_VERSION,
	uiPackageName,
} from "@db-monitor/ui";

import {
	DEFAULT_PROTECTED_ROUTE,
	LOGIN_ROUTE,
	type SessionSnapshot,
	resolveActiveMembership,
	resolveRouteAccess,
} from "./auth";

export interface WebShellContract {
	readonly appName: string;
	readonly apiClient: string;
	readonly apiVersion: string;
	readonly landingRoute: string;
	readonly loginRoute: string;
	readonly providers: readonly string[];
	readonly uiPackage: string;
	readonly uiVersion: string;
}

export interface ShellPanel {
	readonly eyebrow: string;
	readonly href: string;
	readonly summary: string;
	readonly title: string;
}

export interface WebShellModel {
	readonly activeOrganization: {
		readonly membershipCount: number;
		readonly name: string;
		readonly roles: readonly string[];
		readonly slug: string;
	} | null;
	readonly navItems: readonly NavigationItem[];
	readonly panels: readonly ShellPanel[];
	readonly routeGuard: ReturnType<typeof resolveRouteAccess>;
	readonly title: string;
}

const SHELL_PANELS: readonly ShellPanel[] = [
	{
		eyebrow: "Observe",
		href: "/overview",
		summary: "Fleet activity, replication lag, and throughput at one glance.",
		title: "Overview cockpit",
	},
	{
		eyebrow: "Investigate",
		href: "/alerts",
		summary: "Triage alert transitions with explicit history and notifier evidence.",
		title: "Alert timeline",
	},
	{
		eyebrow: "Operate",
		href: "/settings",
		summary:
			"Keep runtime knobs and organization governance visible without leaking backend logic into the UI.",
		title: "Control settings",
	},
];

export const WEB_SHELL_CONTRACT: WebShellContract = {
	appName: "db-monitor-web",
	apiClient: apiClientPackageName,
	apiVersion: API_CONTRACT_VERSION,
	landingRoute: DEFAULT_PROTECTED_ROUTE,
	loginRoute: LOGIN_ROUTE,
	providers: ["react-query", "typed-api-client"],
	uiPackage: uiPackageName,
	uiVersion: UI_FOUNDATION_VERSION,
};

export function buildWebShellModel(session: SessionSnapshot): WebShellModel {
	const activeMembership = resolveActiveMembership(session);
	return {
		activeOrganization:
			session.isAuthenticated && session.activeOrganization !== null
				? {
						membershipCount: session.organizationMemberships.length,
						name: session.activeOrganization.name,
						roles: activeMembership?.roles ?? [],
						slug: session.activeOrganization.slug,
					}
				: null,
		navItems: SHELL_NAVIGATION,
		panels: SHELL_PANELS,
		routeGuard: resolveRouteAccess(DEFAULT_PROTECTED_ROUTE, session),
		title: session.isAuthenticated
			? `Operations shell for ${session.displayName ?? session.username ?? "operator"}`
			: "Operations shell locked behind session auth",
	};
}
