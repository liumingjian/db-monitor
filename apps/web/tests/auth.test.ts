import { describe, expect, it } from "vitest";

import { resolveRouteAccess } from "../src/auth";

describe("auth route guards", () => {
	it("redirects anonymous users away from protected routes", () => {
		expect(
			resolveRouteAccess("/overview", {
				activeOrganization: null,
				displayName: null,
				isAuthenticated: false,
				organizationMemberships: [],
				username: null,
			}),
		).toEqual({
			allow: false,
			redirectTo: "/login?next=%2Foverview",
			surface: "protected",
		});
	});

	it("bounces authenticated users away from login", () => {
		expect(
			resolveRouteAccess("/login", {
				activeOrganization: {
					name: "Internal Operations",
					organization_id: "org-internal",
					slug: "internal-ops",
				},
				displayName: "Platform Admin",
				isAuthenticated: true,
				organizationMemberships: [
					{
						organization: {
							name: "Internal Operations",
							organization_id: "org-internal",
							slug: "internal-ops",
						},
						roles: ["admin"],
					},
				],
				username: "admin",
			}),
		).toEqual({
			allow: true,
			redirectTo: "/overview",
			surface: "public",
		});
	});
});
