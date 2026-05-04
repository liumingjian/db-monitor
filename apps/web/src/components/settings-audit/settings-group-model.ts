import type { SystemSettingResponse } from "@db-monitor/api-client";

export type SettingsGroupId =
	| "general"
	| "retention"
	| "notifications"
	| "integrations"
	| "advanced"
	| "about";

export interface SettingsGroupPartition {
	readonly general: readonly SystemSettingResponse[];
	readonly retention: readonly SystemSettingResponse[];
	readonly notifications: readonly SystemSettingResponse[];
	readonly integrations: readonly SystemSettingResponse[];
	readonly advanced: readonly SystemSettingResponse[];
}

const RETENTION_PREFIX = "retention.";
const NOTIFICATIONS_PREFIXES = ["notify.", "notification."];
const INTEGRATIONS_PREFIXES = ["integration.", "webhook."];
const GENERAL_PREFIXES = ["ui.", "locale."];

export function partitionSettings(
	settings: readonly SystemSettingResponse[],
): SettingsGroupPartition {
	const general: SystemSettingResponse[] = [];
	const retention: SystemSettingResponse[] = [];
	const notifications: SystemSettingResponse[] = [];
	const integrations: SystemSettingResponse[] = [];
	const advanced: SystemSettingResponse[] = [];

	for (const setting of [...settings].sort((left, right) => left.key.localeCompare(right.key))) {
		if (setting.key.startsWith(RETENTION_PREFIX)) {
			retention.push(setting);
			continue;
		}
		if (NOTIFICATIONS_PREFIXES.some((prefix) => setting.key.startsWith(prefix))) {
			notifications.push(setting);
			continue;
		}
		if (INTEGRATIONS_PREFIXES.some((prefix) => setting.key.startsWith(prefix))) {
			integrations.push(setting);
			continue;
		}
		if (GENERAL_PREFIXES.some((prefix) => setting.key.startsWith(prefix))) {
			general.push(setting);
			continue;
		}
		advanced.push(setting);
	}

	return { general, retention, notifications, integrations, advanced };
}
