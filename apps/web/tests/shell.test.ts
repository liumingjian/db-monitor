import { describe, expect, it } from "vitest";

import { WEB_SHELL_CONTRACT, buildWebShellModel } from "../src/app-shell";

describe("shell scaffold", () => {
	it("pins providers, landing route, and navigation", () => {
		expect(WEB_SHELL_CONTRACT).toMatchObject({
			apiClient: "@db-monitor/api-client",
			appName: "db-monitor-web",
			landingRoute: "/overview",
			loginRoute: "/login",
			uiPackage: "@db-monitor/ui",
		});

		const shell = buildWebShellModel({
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
		});

		expect(shell.navItems.map((item) => item.href)).toEqual([
			"/overview",
			"/instances",
			"/alerts",
			"/rules",
			"/settings",
		]);
		expect(shell.activeOrganization).toEqual({
			membershipCount: 1,
			name: "Internal Operations",
			roles: ["admin"],
			slug: "internal-ops",
		});
		expect(shell.routeGuard.allow).toBe(true);
	});
});
