export * from "./primitives";
export * from "./layout";
export * from "./utils";

export interface NavigationItem {
	readonly description: string;
	readonly href: string;
	readonly label: string;
}

export interface FormFieldContract {
	readonly label: string;
	readonly name: string;
	readonly placeholder: string;
	readonly type: "number" | "password" | "text";
}

export interface TableColumnContract {
	readonly key: string;
	readonly label: string;
	readonly tone: "accent" | "neutral" | "status";
}

export interface ChartFrameContract {
	readonly accent: string;
	readonly emptyState: string;
	readonly title: string;
}

export const UI_FOUNDATION_VERSION = "0.2.0";
export const uiPackageName = "@db-monitor/ui";

export const SHELL_NAVIGATION: readonly NavigationItem[] = [
	{
		description: "Fleet pulse and throughput",
		href: "/overview",
		label: "Overview",
	},
	{
		description: "Onboarded database inventory",
		href: "/instances",
		label: "Instances",
	},
	{
		description: "Alert lifecycle and triage",
		href: "/alerts",
		label: "Alerts",
	},
	{
		description: "Threshold rules and scope",
		href: "/rules",
		label: "Rules",
	},
	{
		description: "Global runtime settings",
		href: "/settings",
		label: "Settings",
	},
];

export const LOGIN_FORM_FIELDS: readonly FormFieldContract[] = [
	{
		label: "Username",
		name: "username",
		placeholder: "admin",
		type: "text",
	},
	{
		label: "Password",
		name: "password",
		placeholder: "admin-password",
		type: "password",
	},
];

export const INSTANCE_FORM_FIELDS: readonly FormFieldContract[] = [
	{
		label: "Name",
		name: "name",
		placeholder: "prod-primary",
		type: "text",
	},
	{
		label: "Environment",
		name: "environment",
		placeholder: "prod",
		type: "text",
	},
	{
		label: "Database / DSN",
		name: "database",
		placeholder: "mysql or ORCLCDB",
		type: "text",
	},
	{
		label: "Host",
		name: "host",
		placeholder: "127.0.0.1",
		type: "text",
	},
	{
		label: "Port",
		name: "port",
		placeholder: "3306",
		type: "number",
	},
	{
		label: "Username",
		name: "username",
		placeholder: "db_monitor",
		type: "text",
	},
	{
		label: "Password",
		name: "password",
		placeholder: "••••••••",
		type: "password",
	},
	{
		label: "Labels",
		name: "labels",
		placeholder: "primary,critical",
		type: "text",
	},
];

export const ALERT_TABLE_COLUMNS: readonly TableColumnContract[] = [
	{
		key: "rule_name",
		label: "Rule",
		tone: "accent",
	},
	{
		key: "status",
		label: "Status",
		tone: "status",
	},
	{
		key: "instance_id",
		label: "Instance",
		tone: "neutral",
	},
];

export const INSTANCE_TABLE_COLUMNS: readonly TableColumnContract[] = [
	{
		key: "name",
		label: "Instance",
		tone: "accent",
	},
	{
		key: "environment",
		label: "Environment",
		tone: "neutral",
	},
	{
		key: "status",
		label: "Status",
		tone: "status",
	},
];

export const RULE_TABLE_COLUMNS: readonly TableColumnContract[] = [
	{
		key: "name",
		label: "Rule",
		tone: "accent",
	},
	{
		key: "metric_name",
		label: "Metric",
		tone: "neutral",
	},
	{
		key: "severity",
		label: "Severity",
		tone: "status",
	},
];

export const RULE_FORM_FIELDS: readonly FormFieldContract[] = [
	{
		label: "Rule Name",
		name: "name",
		placeholder: "Replication Lag High",
		type: "text",
	},
	{
		label: "Metric Name",
		name: "metric_name",
		placeholder: "mysql_replication_lag_seconds or oracle_sessions_active",
		type: "text",
	},
	{
		label: "Threshold",
		name: "threshold",
		placeholder: "5",
		type: "number",
	},
	{
		label: "Instance Scope",
		name: "instance_ids",
		placeholder: "inst-prod-primary",
		type: "text",
	},
];

export const RULE_OPERATORS = ["gt", "gte", "lt", "lte"] as const;
export const RULE_SEVERITIES = ["warning", "critical"] as const;

export const SETTINGS_FORM_FIELDS: readonly FormFieldContract[] = [
	{
		label: "Notification Channel",
		name: "notification.channel",
		placeholder: "email",
		type: "text",
	},
];

export const OVERVIEW_CHART_FRAME: ChartFrameContract = {
	accent: "ember",
	emptyState: "No metrics have arrived for this window yet.",
	title: "Fleet Activity",
};

export const INSTANCE_CHART_FRAME: ChartFrameContract = {
	accent: "slate",
	emptyState: "This instance has not produced enough trend points yet.",
	title: "Instance Trends",
};
