// pm2 process definitions for the dev workflow.
//
// Scope: api + web (the two pieces that benefit from hot reload).
// DB infra (postgres / clickhouse / redis / mysql / mysql-target) and the
// background runtime services (scheduler / worker-mysql) keep running in
// docker compose — they need the in-network DNS (e.g. `mysql-target`) and
// don't carry user-facing edit-reload pain.

const path = require("node:path");

const ROOT = __dirname;

const RUNTIME_ENV = {
	DB_MONITOR_RUNTIME: "postgres",
	DB_MONITOR_POSTGRES_DSN: "postgresql://db_monitor:db_monitor@127.0.0.1:5432/db_monitor",
	DB_MONITOR_REDIS_URL: "redis://127.0.0.1:6379/0",
	DB_MONITOR_CLICKHOUSE_ENDPOINT: "http://127.0.0.1:8123",
	DB_MONITOR_CLICKHOUSE_DATABASE: "db_monitor",
	DB_MONITOR_CLICKHOUSE_USERNAME: "db_monitor",
	DB_MONITOR_CLICKHOUSE_PASSWORD: "db_monitor",
};

module.exports = {
	apps: [
		{
			name: "api",
			cwd: ROOT,
			script: "uv",
			args: [
				"run",
				"python",
				"-m",
				"uvicorn",
				"db_monitor_api.main:app",
				"--app-dir",
				"apps/api/src",
				"--host",
				"127.0.0.1",
				"--port",
				"39100",
				"--reload",
				"--reload-dir",
				"apps/api/src",
			],
			interpreter: "none",
			autorestart: true,
			watch: false,
			max_restarts: 10,
			env: RUNTIME_ENV,
		},
		{
			name: "web",
			cwd: path.join(ROOT, "apps/web"),
			script: "pnpm",
			args: ["exec", "next", "dev", "--hostname", "127.0.0.1", "--port", "39101"],
			interpreter: "none",
			autorestart: true,
			watch: false,
			max_restarts: 10,
			env: {
				NODE_ENV: "development",
				NEXT_TELEMETRY_DISABLED: "1",
				DB_MONITOR_API_BASE_URL: "http://127.0.0.1:39100",
			},
		},
	],
};
