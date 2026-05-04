import { describe, expect, it } from "vitest";

import { buildSettingsManagementModel } from "../src/settings-management";

describe("settings management model", () => {
	it("enables user management for admin memberships and sorts payloads", () => {
		const model = buildSettingsManagementModel({
			activeMembership: {
				organization: {
					name: "Internal Operations",
					organization_id: "org-internal",
					slug: "internal-ops",
				},
				roles: ["admin"],
			},
			roleCatalog: [
				{ permissions: ["settings:read"], role: "viewer" },
				{ permissions: ["settings:write"], role: "admin" },
			],
			users: [
				{
					active_organization_id: "org-internal",
					display_name: "Zulu Operator",
					effective_permissions: ["settings:read"],
					roles: ["viewer"],
					user_id: "user-zulu",
					username: "zulu",
				},
				{
					active_organization_id: "org-internal",
					display_name: "Alpha Operator",
					effective_permissions: ["settings:write"],
					roles: ["admin"],
					user_id: "user-alpha",
					username: "alpha",
				},
			],
		});

		expect(model.canManageUsers).toBe(true);
		expect(model.roleCatalog.map((entry) => entry.role)).toEqual(["admin", "viewer"]);
		expect(model.users.map((user) => user.display_name)).toEqual([
			"Alpha Operator",
			"Zulu Operator",
		]);
	});

	it("keeps non-admin memberships read-only", () => {
		const model = buildSettingsManagementModel({
			activeMembership: {
				organization: {
					name: "Internal Operations",
					organization_id: "org-internal",
					slug: "internal-ops",
				},
				roles: ["viewer"],
			},
			roleCatalog: [],
			users: [],
		});

		expect(model.canManageUsers).toBe(false);
	});
});
