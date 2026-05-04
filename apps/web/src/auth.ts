import type { OrganizationMembership, OrganizationSummary } from "@db-monitor/api-client";

export interface SessionSnapshot {
	readonly activeOrganization: OrganizationSummary | null;
	readonly displayName: string | null;
	readonly isAuthenticated: boolean;
	readonly organizationMemberships: readonly OrganizationMembership[];
	readonly username: string | null;
}

export interface RouteAccessDecision {
	readonly allow: boolean;
	readonly redirectTo: string | null;
	readonly surface: "protected" | "public";
}

export const LOGIN_ROUTE = "/login";
export const DEFAULT_PROTECTED_ROUTE = "/overview";

export function resolveRouteAccess(
	pathname: string,
	session: SessionSnapshot,
): RouteAccessDecision {
	if (pathname === LOGIN_ROUTE) {
		return {
			allow: true,
			redirectTo: session.isAuthenticated ? DEFAULT_PROTECTED_ROUTE : null,
			surface: "public",
		};
	}
	if (session.isAuthenticated) {
		return {
			allow: true,
			redirectTo: null,
			surface: "protected",
		};
	}
	return {
		allow: false,
		redirectTo: `${LOGIN_ROUTE}?next=${encodeURIComponent(pathname)}`,
		surface: "protected",
	};
}

export function resolveActiveMembership(session: SessionSnapshot): OrganizationMembership | null {
	if (session.activeOrganization === null) {
		return null;
	}
	return (
		session.organizationMemberships.find(
			(membership) =>
				membership.organization.organization_id === session.activeOrganization?.organization_id,
		) ?? null
	);
}
