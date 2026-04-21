import type {
	AlertDetailResponse,
	AlertEngineCatalogResponse,
	AlertRecordResponse,
	AlertRuleResponse,
	InstanceResponse,
	InstanceTrendResponse,
	OverviewResponse,
	SystemSettingResponse,
} from "@db-monitor/api-client";

import type { InstanceFormValues, RuleFormValues } from "./monitoring-ui";

export const PREVIEW_INSTANCE_FORM_VALUES: InstanceFormValues = {
	engine: "mysql",
	database: "mysql",
	environment: "prod",
	host: "127.0.0.1",
	labels: "primary,critical",
	name: "prod-primary",
	password: "secret",
	port: "3306",
	username: "db_monitor",
};

export const PREVIEW_RULE_FORM_VALUES: RuleFormValues = {
	engine: "mysql",
	instance_ids: "inst-prod-primary",
	metric_name: "mysql_replication_lag_seconds",
	name: "Replication Lag High",
	operator: "gt",
	severity: "critical",
	threshold: "5",
};

export const PREVIEW_INSTANCE: InstanceResponse = {
	connection: {
		database: "mysql",
		host: "127.0.0.1",
		port: 3306,
		username: "db_monitor",
	},
	created_at: "2026-04-19T20:00:00+08:00",
	engine: "mysql",
	environment: "prod",
	instance_id: "inst-prod-primary",
	labels: ["primary", "critical"],
	name: "prod-primary",
	validation: {
		checked_at: "2026-04-19T20:00:00+08:00",
		detail: "ok",
		server_version: "8.4.0",
		status: "passed",
	},
};

export const PREVIEW_ORACLE_INSTANCE: InstanceResponse = {
	connection: {
		database: "ORCLCDB",
		host: "127.0.0.1",
		port: 1521,
		username: "system",
	},
	created_at: "2026-04-19T20:15:00+08:00",
	engine: "oracle",
	environment: "prod",
	instance_id: "inst-prod-oracle",
	labels: ["oracle", "baseline"],
	name: "prod-oracle-primary",
	validation: {
		checked_at: "2026-04-19T20:15:00+08:00",
		detail: "Oracle connection validated successfully using the supplied DSN/service name.",
		server_version: "19.21.0.0.0",
		status: "passed",
	},
};

export const PREVIEW_OVERVIEW: OverviewResponse = {
	bucket_seconds: 300,
	cards: [
		{
			label: "Threads Connected",
			metric_name: "mysql_threads_connected",
			unit: "connections",
			value: 18,
		},
		{
			label: "Threads Running",
			metric_name: "mysql_threads_running",
			unit: "threads",
			value: 4,
		},
		{ label: "QPS", metric_name: "mysql_queries_per_second", unit: "qps", value: 0.6 },
		{
			label: "Inbound Throughput",
			metric_name: "mysql_bytes_received_per_second",
			unit: "bytes/s",
			value: 1.8,
		},
		{
			label: "Outbound Throughput",
			metric_name: "mysql_bytes_sent_per_second",
			unit: "bytes/s",
			value: 2.7,
		},
		{
			label: "Buffer Pool Reads",
			metric_name: "mysql_innodb_buffer_pool_reads_per_second",
			unit: "reads/s",
			value: 0.15,
		},
		{
			label: "Replication Lag",
			metric_name: "mysql_replication_lag_seconds",
			unit: "seconds",
			value: 5,
		},
	],
	charts: [
		{
			label: "Threads Connected",
			metric_name: "mysql_threads_connected",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 16 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 18 },
			],
			unit: "connections",
		},
		{
			label: "Threads Running",
			metric_name: "mysql_threads_running",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 3 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 4 },
			],
			unit: "threads",
		},
		{
			label: "QPS",
			metric_name: "mysql_queries_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 0.4 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 0.6 },
			],
			unit: "qps",
		},
		{
			label: "Inbound Throughput",
			metric_name: "mysql_bytes_received_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 1.2 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 1.8 },
			],
			unit: "bytes/s",
		},
		{
			label: "Outbound Throughput",
			metric_name: "mysql_bytes_sent_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 1.9 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 2.7 },
			],
			unit: "bytes/s",
		},
		{
			label: "Buffer Pool Reads",
			metric_name: "mysql_innodb_buffer_pool_reads_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 0.08 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 0.15 },
			],
			unit: "reads/s",
		},
		{
			label: "Replication Lag",
			metric_name: "mysql_replication_lag_seconds",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 3 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 5 },
			],
			unit: "seconds",
		},
	],
	coverage: {
		detail_analytics_engines: ["mysql"],
		fleet_health_engines: ["mysql"],
		overview_instance_metric_engines: ["mysql"],
		overview_metric_engines: ["mysql"],
	},
	generated_at: "2026-04-19T20:00:00+08:00",
	instances: [
		{
			environment: "prod",
			engine: "mysql",
			instance_id: "inst-prod-primary",
			labels: ["primary", "critical"],
			name: "prod-primary",
			qps: 0.6,
			replication_lag_seconds: 5,
			status: "healthy",
			threads_connected: 18,
			threads_running: 4,
		},
	],
	summary: {
		engines: [
			{
				engine: "mysql",
				healthy_instances: 1,
				total_instances: 1,
				unhealthy_instances: 0,
			},
		],
		healthy_instances: 1,
		total_instances: 1,
		unhealthy_instances: 0,
	},
	window: "1h",
};

export const PREVIEW_INSTANCE_TREND: InstanceTrendResponse = {
	bucket_seconds: 300,
	cards: [
		{ label: "Uptime", metric_name: "mysql_uptime_seconds", unit: "seconds", value: 1300 },
		{
			label: "Threads Connected",
			metric_name: "mysql_threads_connected",
			unit: "connections",
			value: 18,
		},
		{ label: "Threads Running", metric_name: "mysql_threads_running", unit: "threads", value: 4 },
		{ label: "QPS", metric_name: "mysql_queries_per_second", unit: "qps", value: 0.6 },
		{
			label: "Inbound Throughput",
			metric_name: "mysql_bytes_received_per_second",
			unit: "bytes/s",
			value: 1.8,
		},
		{
			label: "Outbound Throughput",
			metric_name: "mysql_bytes_sent_per_second",
			unit: "bytes/s",
			value: 2.7,
		},
		{
			label: "Buffer Pool Reads",
			metric_name: "mysql_innodb_buffer_pool_reads_per_second",
			unit: "reads/s",
			value: 0.15,
		},
		{ label: "Replication Lag", metric_name: "mysql_replication_lag_seconds", unit: "seconds", value: 5 },
	],
	charts: [
		{
			label: "Threads Connected",
			metric_name: "mysql_threads_connected",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 16 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 18 },
			],
			unit: "connections",
		},
		{
			label: "Threads Running",
			metric_name: "mysql_threads_running",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 3 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 4 },
			],
			unit: "threads",
		},
		{
			label: "Inbound Throughput",
			metric_name: "mysql_bytes_received_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 1.2 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 1.8 },
			],
			unit: "bytes/s",
		},
		{
			label: "QPS",
			metric_name: "mysql_queries_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 0.4 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 0.6 },
			],
			unit: "qps",
		},
		{
			label: "Outbound Throughput",
			metric_name: "mysql_bytes_sent_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 1.9 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 2.7 },
			],
			unit: "bytes/s",
		},
		{
			label: "Buffer Pool Reads",
			metric_name: "mysql_innodb_buffer_pool_reads_per_second",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 0.08 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 0.15 },
			],
			unit: "reads/s",
		},
		{
			label: "Replication Lag",
			metric_name: "mysql_replication_lag_seconds",
			points: [
				{ timestamp: "2026-04-19T19:45:00+08:00", value: 3 },
				{ timestamp: "2026-04-19T19:50:00+08:00", value: 5 },
			],
			unit: "seconds",
		},
	],
	generated_at: "2026-04-19T20:00:00+08:00",
	instance: {
		environment: "prod",
		instance_id: "inst-prod-primary",
		labels: ["primary", "critical"],
		name: "prod-primary",
		status: "healthy",
	},
	window: "1h",
};

export const PREVIEW_ORACLE_INSTANCE_TREND: InstanceTrendResponse = {
	bucket_seconds: 300,
	cards: [
		{ label: "Uptime", metric_name: "oracle_uptime_seconds", unit: "seconds", value: 7200 },
		{
			label: "Sessions Total",
			metric_name: "oracle_sessions_total",
			unit: "sessions",
			value: 32,
		},
		{
			label: "Sessions Active",
			metric_name: "oracle_sessions_active",
			unit: "sessions",
			value: 8,
		},
		{
			label: "Session Waits",
			metric_name: "oracle_session_waits",
			unit: "sessions",
			value: 2,
		},
		{
			label: "User Calls",
			metric_name: "oracle_user_calls_per_second",
			unit: "calls/s",
			value: 1.2,
		},
		{
			label: "Physical Reads",
			metric_name: "oracle_physical_reads_per_second",
			unit: "reads/s",
			value: 0.4,
		},
	],
	charts: [
		{
			label: "Sessions Total",
			metric_name: "oracle_sessions_total",
			points: [
				{ timestamp: "2026-04-19T20:00:00+08:00", value: 28 },
				{ timestamp: "2026-04-19T20:05:00+08:00", value: 32 },
			],
			unit: "sessions",
		},
		{
			label: "Sessions Active",
			metric_name: "oracle_sessions_active",
			points: [
				{ timestamp: "2026-04-19T20:00:00+08:00", value: 5 },
				{ timestamp: "2026-04-19T20:05:00+08:00", value: 8 },
			],
			unit: "sessions",
		},
		{
			label: "Session Waits",
			metric_name: "oracle_session_waits",
			points: [
				{ timestamp: "2026-04-19T20:00:00+08:00", value: 1 },
				{ timestamp: "2026-04-19T20:05:00+08:00", value: 2 },
			],
			unit: "sessions",
		},
		{
			label: "User Calls",
			metric_name: "oracle_user_calls_per_second",
			points: [
				{ timestamp: "2026-04-19T20:00:00+08:00", value: 0.8 },
				{ timestamp: "2026-04-19T20:05:00+08:00", value: 1.2 },
			],
			unit: "calls/s",
		},
		{
			label: "Physical Reads",
			metric_name: "oracle_physical_reads_per_second",
			points: [
				{ timestamp: "2026-04-19T20:00:00+08:00", value: 0.2 },
				{ timestamp: "2026-04-19T20:05:00+08:00", value: 0.4 },
			],
			unit: "reads/s",
		},
	],
	generated_at: "2026-04-19T20:10:00+08:00",
	instance: {
		environment: "prod",
		instance_id: "inst-prod-oracle",
		labels: ["oracle", "baseline"],
		name: "prod-oracle-primary",
		status: "healthy",
	},
	window: "1h",
};

export const PREVIEW_RULES: readonly AlertRuleResponse[] = [
	{
		created_at: "2026-04-19T20:00:00+08:00",
		enabled: true,
		engine: "mysql",
		instance_ids: ["inst-prod-primary"],
		metric_name: "mysql_replication_lag_seconds",
		name: "Replication Lag High",
		operator: "gt",
		rule_id: "rule-lag",
		severity: "critical",
		threshold: 5,
	},
];

export const PREVIEW_RULE_CATALOG: readonly AlertEngineCatalogResponse[] = [
	{
		engine: "mysql",
		metrics: [
			{
				label: "Server Availability",
				metric_name: "mysql_server_available",
				unit: "status",
			},
			{
				label: "Threads Connected",
				metric_name: "mysql_threads_connected",
				unit: "connections",
			},
			{
				label: "Threads Running",
				metric_name: "mysql_threads_running",
				unit: "threads",
			},
			{
				label: "Uptime",
				metric_name: "mysql_uptime_seconds",
				unit: "seconds",
			},
			{
				label: "Replication Lag",
				metric_name: "mysql_replication_lag_seconds",
				unit: "seconds",
			},
		],
	},
	{
		engine: "oracle",
		metrics: [
			{
				label: "Server Availability",
				metric_name: "oracle_server_available",
				unit: "status",
			},
			{
				label: "Sessions Total",
				metric_name: "oracle_sessions_total",
				unit: "sessions",
			},
			{
				label: "Sessions Active",
				metric_name: "oracle_sessions_active",
				unit: "sessions",
			},
			{
				label: "Session Waits",
				metric_name: "oracle_session_waits",
				unit: "sessions",
			},
			{
				label: "Uptime",
				metric_name: "oracle_uptime_seconds",
				unit: "seconds",
			},
		],
	},
];

export const PREVIEW_ALERTS: readonly AlertRecordResponse[] = [
	{
		alert_id: "alert-lag",
		acknowledged_at: "2026-04-19T20:01:00+08:00",
		acknowledged_by_user_id: "user-ops",
		current_value: 8,
		engine: "mysql",
		instance_id: "inst-prod-primary",
		last_evaluated_at: "2026-04-19T20:00:00+08:00",
		metric_name: "mysql_replication_lag_seconds",
		opened_at: "2026-04-19T19:55:00+08:00",
		owner_assigned_at: "2026-04-19T20:02:00+08:00",
		owner_user_id: "user-ops",
		resolved_at: null,
		rule_id: "rule-lag",
		rule_name: "Replication Lag High",
		severity: "critical",
		status: "acknowledged",
		threshold: 5,
	},
];

export const PREVIEW_ALERT_DETAIL: AlertDetailResponse = {
	history: [
		{
			alert_id: "alert-lag",
			detail:
				"MySQL rule 'Replication Lag High' triggered on inst-prod-primary: mysql_replication_lag_seconds=8.0 threshold=5.0.",
			event_type: "opened",
			occurred_at: "2026-04-19T19:55:00+08:00",
		},
		{
			alert_id: "alert-lag",
			detail: "Notifier sent critical MySQL alert.",
			event_type: "notified",
			occurred_at: "2026-04-19T19:55:00+08:00",
		},
		{
			alert_id: "alert-lag",
			detail: "Acknowledged by user-ops.",
			event_type: "acknowledged",
			occurred_at: "2026-04-19T20:01:00+08:00",
		},
		{
			alert_id: "alert-lag",
			detail: "Owner assigned to user-ops by user-admin.",
			event_type: "owner_assigned",
			occurred_at: "2026-04-19T20:02:00+08:00",
		},
		{
			alert_id: "alert-lag",
			detail: "user-ops: Investigating replication lag.",
			event_type: "note_added",
			occurred_at: "2026-04-19T20:03:00+08:00",
		},
	],
	record: PREVIEW_ALERTS[0],
};

export const PREVIEW_SETTINGS: readonly SystemSettingResponse[] = [
	{
		key: "notification.channel",
		updated_at: "2026-04-19T20:00:00+08:00",
		value: "email",
	},
];
