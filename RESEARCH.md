# RESEARCH

## Executive Summary
`lepus-v3.8` is now treated as a domain reference, not as the runtime base of the
new product. The legacy system is not mainly problematic because it uses PHP; it
is problematic because UI, configuration, collection, aggregation, and alerting
are all coupled through one shared MySQL control database.

Boss confirmed there is no legacy migration burden and no need to preserve old runtime
compatibility. The correct strategy is a greenfield rebuild that keeps domain knowledge
and discards the old runtime structure.
## Scope and Method
This document is based on direct inspection of:
- `lepus-v3.8/web/`
- `lepus-v3.8/*.py`
- `lepus-v3.8/check_os.sh`
- `lepus-v3.8/sql/`
- `lepus-v3.8/install.sh`
- `lepus-v3.8/lepus`
- `lepus-v3.8/lepus_monitor`
It also records the final architecture decisions explicitly approved by Boss.
## Current Workspace Snapshot
Top-level content at research time included `AGENT.md`, `lepus-v3.8/`,
`scripts/`, and local tooling folders such as `.claude/` and `.playwright/`.
The workspace was not a Git repository when this publishing task started.
## Legacy Lepus v3.8 Findings
### Runtime Topology
Legacy Lepus is a dual-runtime system:
- PHP CodeIgniter web application under `lepus-v3.8/web/`
- Python and shell collection/alarm runtime under `lepus-v3.8/`
Both runtimes read and write the same MySQL control database.
Key runtime files:
- `lepus-v3.8/lepus.py`
- `lepus-v3.8/lepus`
- `lepus-v3.8/lepus_monitor`
- `lepus-v3.8/install.sh`
Observed runtime behavior:
- `lepus.py` reads switches from `options`
- it spawns long-running loops for collectors and alerts
- loops use `while True`, `os.system("python xxx.py")`, and `sleep(...)`
- MySQL, Oracle, MongoDB, Redis, SQLServer, and OS each have dedicated scripts
### Web Architecture
The web layer is a classic server-rendered CodeIgniter application.
Key files:
- `lepus-v3.8/web/index.php`
- `lepus-v3.8/web/application/config/routes.php`
- `lepus-v3.8/web/application/config/autoload.php`
- `lepus-v3.8/web/application/core/MY_Controller.php`
Confirmed characteristics:
- controller/method routing
- PHP server-side rendering for most pages
- controllers frequently execute SQL directly through `$this->db`
- models often read `$_GET` directly
- views depend on controller-assembled chart arrays and page-specific SQL
Heavy domain controllers:
- `web/application/controllers/lp_mysql.php`
- `web/application/controllers/lp_oracle.php`
- `web/application/controllers/lp_redis.php`
- `web/application/controllers/lp_os.php`
- `web/application/controllers/lp_mongodb.php`
- `web/application/controllers/screen.php`
- `web/application/controllers/index.php`
- `web/application/controllers/task.php`
Control-side CRUD controllers:
- `web/application/controllers/servers_mysql.php`
- `web/application/controllers/servers_oracle.php`
- `web/application/controllers/servers_redis.php`
- `web/application/controllers/servers_os.php`
- `web/application/controllers/settings.php`

### Data and Control Flow
The old platform is integrated through database tables, not APIs:
1. Web writes configuration to `options` and `db_servers_*`.
2. Collectors read those tables.
3. Collectors connect to targets and write fresh snapshots.
4. Alert logic reads snapshots plus thresholds from `db_servers_*`.
5. Alert logic writes `alarm`, `alarm_temp`, `alarm_history`, and updates
   `db_status`.
6. Web pages read current and historical state directly from those tables.
The schema is therefore the real integration contract.
### Collector Inventory
Primary scripts:
- `check_mysql.py`
- `check_oracle.py`
- `check_mongodb.py`
- `check_redis.py`
- `check_sqlserver.py`
- `check_os.py`
- `check_os.sh`
- `alarm.py`
- `check_mysql_bigtable.py`
- `admin_mysql_purge_binlog.py`
Special OS note: `check_os.py` calls `check_os.sh`, which uses `snmpwalk`,
`snmpdf`, and the MySQL CLI directly; this is the hardest runtime boundary in
the old system.

### Schema Groups
`lepus-v3.8/sql/lepus_table.sql` contains five major groups:

- `admin_*`: users, roles, privileges, logs
- `options`, `lepus_status`: global configuration and runtime state
- `db_servers_*`: monitored assets and thresholds
- `*_status`, `*_history`, `*_replication*`, `oracle_tablespace*`, `os_*`: snapshots and histories
- `alarm`, `alarm_temp`, `alarm_history`: alerting pipeline

### Confirmed Legacy Problems
#### 1. Tight coupling through shared tables

Examples:
- `web/application/models/lepus_model.php`
- `web/application/models/mysql_model.php`
- `web/application/controllers/screen.php`
- `check_mysql.py`
- `alarm.py`
#### 2. Controllers carry too much domain logic

`lp_mysql.php` mixes privilege checks, raw SQL, time-series loops, chart data
assembly, slow query reporting, and backup reporting in one place.
#### 3. Alerting is overloaded

`alarm.py` currently combines threshold loading, evaluation, repeat suppression,
recovery handling, sending, and history archiving.
#### 4. Runtime model is fragile

Collector control relies on looped process launching, manual timing, and ad hoc
termination behavior.
#### 5. Repository schema and runtime schema already drifted apart

Confirmed examples:

- code references `db_application`, but the shipped schema does not include it
- code references `os_resource` and `os_diskinfo`, but the shipped schema does
  not include them
- code references `mysql_process`, while collection writes `mysql_processlist`
- `servers_sqlserver_model.php` removes `db_status` rows with the wrong
  `db_type`

This drift is the strongest evidence that the old runtime architecture should not be reused.
## Final Product Direction Approved by Boss
Boss approved the following direction:

1. No legacy migration is required.
2. Lepus is a research sample only.
3. The new system is a greenfield rebuild.
4. The first deliverable is `MySQL-first`.
5. The first version is internal and single-tenant.
6. Development is local-first, not container-first.
7. Database test environments may use `docker compose`.
8. The repository should be a monorepo.
9. `Next.js` is UI only and must not own business logic or database access.
10. `FastAPI` is the single business API boundary.
11. API internals must follow `router -> service -> repository`.
12. Frontend stack: `Next.js`, `React`, `Tailwind CSS v4`, `shadcn/ui`.
13. Charts should standardize on `ECharts`.
14. Frontend data access should use `TanStack Query`.
15. API style should be REST/JSON, not GraphQL.
16. Contracts should be `OpenAPI-first` with generated typed clients.
17. Auth and RBAC should be rebuilt for the new product.
18. Storage should be split from day one: `PostgreSQL` for control data and
    `ClickHouse` for analytics/time-series.
19. `Redis` should be used as the task distribution bus.
20. Runtime should be `scheduler + typed workers`.
21. Alerting must be split into `collection -> rule evaluation -> notification`.
22. Metrics should use a unified domain model with engine-specific extensions.
23. The first MySQL version should be `agentless`.
24. The first MySQL version should focus on high-value core metrics only.
25. The first alerting version should support only the basic rule set.
26. The control API should remain a modular monolith in phase one.
27. Quality gates must exist from day one.
28. No multitenancy in phase one.
## Target Greenfield Architecture
### Control Plane
Recommended control-plane layout:

- `apps/web`: Next.js UI
- `apps/api`: FastAPI business API
- `PostgreSQL`: users, RBAC, assets, datasource configs, task definitions, rule
  definitions, alert records, audit logs, saved views

Responsibilities:

- authentication
- RBAC
- datasource and instance management
- alert rule management
- system settings
- alert history queries
- dashboard aggregation APIs

### Data Plane
Recommended data-plane layout:

- `ClickHouse`: metrics, snapshots, histories, top-N analytics
- `Redis`: task dispatch only
- typed workers by engine, starting with `mysql-worker`

Key processes: `scheduler`, `mysql-worker`, `rule-engine`, and `notifier`.

### Alerting Pipeline
Target pipeline:

1. collector gathers facts
2. collector writes normalized results
3. rule engine evaluates rules
4. rule engine emits alert events
5. notifier sends messages
6. control plane stores alert history

Collectors must not send notifications directly.
## Suggested Monorepo Layout

```text
apps/
  web/
  api/
  scheduler/
  worker-mysql/
  rule-engine/
  notifier/
packages/
  ui/
  api-client/
  shared-types/
docs/
  adr/
legacy/
  lepus-v3.8/
```

New code should not depend on legacy runtime files.
## Phase-One Product Scope
Phase one should prioritize a clean `MySQL-first` control plane:

- login and session handling
- new RBAC
- MySQL instance onboarding
- overview dashboard
- instance list and instance detail pages
- core MySQL trend views
- alert list and alert detail
- rule management
- system settings

Do not include in phase one unless later justified:

- all-engine parity with Lepus
- slow query deep analysis
- bigtable scans
- backup monitoring
- binlog maintenance
- advanced report generators
- complex rule DSL
- multitenancy

## Initial MySQL Metric Scope
The first MySQL metric set should focus on:

- availability and role
- version and uptime
- threads connected
- threads running
- connection rate
- QPS and TPS
- bytes in and out
- core InnoDB health metrics
- replication status
- replication delay
- basic utilization ratios

## Quality Baseline
Minimum quality gates:

- frontend type checking
- frontend linting
- backend linting
- backend type checking
- service and repository unit tests
- OpenAPI generation and contract diff checks
- data access integration tests
- minimal end-to-end smoke tests

## Local Development Baseline
Approved local-first baseline:

- package manager: `pnpm`
- Python toolchain: `uv`
- Python: `3.12`
- Node: `22 LTS`
- local scripts for dev startup
- database test environments may use `docker compose`

## Public Publishing Notes
Files intentionally excluded from public version control include
`lepus-v3.8/etc/config.ini`, `lepus-v3.8/web/application/config/database.php`,
generated Python bytecode, and local-only tooling directories already ignored in
the root `.gitignore`.

## Key Source References
Runtime and deployment:

- `lepus-v3.8/lepus.py`
- `lepus-v3.8/lepus`
- `lepus-v3.8/lepus_monitor`
- `lepus-v3.8/install.sh`
- `lepus-v3.8/.gitignore`

Collection and alerting:

- `lepus-v3.8/check_mysql.py`
- `lepus-v3.8/check_oracle.py`
- `lepus-v3.8/check_mongodb.py`
- `lepus-v3.8/check_redis.py`
- `lepus-v3.8/check_sqlserver.py`
- `lepus-v3.8/check_os.py`
- `lepus-v3.8/check_os.sh`
- `lepus-v3.8/alarm.py`
- `lepus-v3.8/include/functions.py`

Web layer and schema:

- `lepus-v3.8/web/index.php`
- `lepus-v3.8/web/application/config/routes.php`
- `lepus-v3.8/web/application/config/autoload.php`
- `lepus-v3.8/web/application/core/MY_Controller.php`
- `lepus-v3.8/web/application/controllers/index.php`
- `lepus-v3.8/web/application/controllers/screen.php`
- `lepus-v3.8/web/application/controllers/lp_mysql.php`
- `lepus-v3.8/web/application/controllers/servers_mysql.php`
- `lepus-v3.8/web/application/controllers/settings.php`
- `lepus-v3.8/web/application/controllers/task.php`
- `lepus-v3.8/web/application/models/lepus_model.php`
- `lepus-v3.8/web/application/models/mysql_model.php`
- `lepus-v3.8/web/application/models/option_model.php`
- `lepus-v3.8/web/application/models/servers_sqlserver_model.php`
- `lepus-v3.8/sql/lepus_table.sql`
- `lepus-v3.8/sql/lepus_data.sql`

## Final Recommendation
Build the new product as a clean internal monitoring platform with a new control-plane
schema, a new API boundary, split storage, explicit workers, explicit alert stages,
and explicit contracts. Reuse Lepus only for domain vocabulary, metric ideas, workflow
reference, and historical pitfalls.
