import type {
	ManagedUserResponse,
	OrganizationMembership,
	RoleCatalogEntryResponse,
} from "@db-monitor/api-client";

export interface SettingsManagementModel {
	readonly canManageUsers: boolean;
	readonly roleCatalog: readonly RoleCatalogEntryResponse[];
	readonly users: readonly ManagedUserResponse[];
}

interface BuildSettingsManagementModelOptions {
	readonly activeMembership: OrganizationMembership | null;
	readonly roleCatalog: readonly RoleCatalogEntryResponse[];
	readonly users: readonly ManagedUserResponse[];
}

export function buildSettingsManagementModel(
	options: BuildSettingsManagementModelOptions,
): SettingsManagementModel {
	return {
		canManageUsers: options.activeMembership?.roles.includes("admin") ?? false,
		roleCatalog: [...options.roleCatalog].sort((left, right) =>
			left.role.localeCompare(right.role),
		),
		users: [...options.users].sort((left, right) =>
			left.display_name.localeCompare(right.display_name),
		),
	};
}
