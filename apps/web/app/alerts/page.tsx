import { AppChrome } from "../../src/components/app-chrome";
import {
	buildAlertListFilterValues,
	buildOperationsModel,
	formatDatabaseEngine,
} from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

interface AlertsPageProps {
	readonly searchParams: Promise<{
		readonly instance?: string;
		readonly opened_after?: string;
		readonly opened_before?: string;
		readonly severity?: string;
		readonly status?: string;
	}>;
}

export default async function AlertsPage({ searchParams }: AlertsPageProps) {
	const session = await requireServerSession("/alerts");
	const params = await searchParams;
	const filters = buildAlertListFilterValues(params);
	const apiClient = await createServerApiClient();
	const model = buildOperationsModel({
		alertFilters: filters,
		alerts: await apiClient.listAlerts({
			instance: emptyToUndefined(filters.instance),
			opened_after: emptyToUndefined(filters.opened_after),
			opened_before: emptyToUndefined(filters.opened_before),
			severity: emptyToUndefined(filters.severity),
			status: emptyToUndefined(filters.status),
		}),
	});

	return (
		<AppChrome session={session}>
			<div className="space-y-4">
				<h2 className="text-2xl font-semibold">Alert queue</h2>
				<form
					className="grid gap-3 rounded-[1.2rem] border border-black/5 bg-white p-4 md:grid-cols-2"
					method="get"
				>
					<label className="grid gap-2" htmlFor="status">
						<span className="text-sm font-medium">Status</span>
						<select
							className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
							defaultValue={model.alertFilters.status}
							id="status"
							name="status"
						>
							<option value="">All statuses</option>
							<option value="open">open</option>
							<option value="acknowledged">acknowledged</option>
							<option value="resolved">resolved</option>
						</select>
					</label>
					<label className="grid gap-2" htmlFor="severity">
						<span className="text-sm font-medium">Severity</span>
						<select
							className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
							defaultValue={model.alertFilters.severity}
							id="severity"
							name="severity"
						>
							<option value="">All levels</option>
							<option value="critical">critical</option>
							<option value="warning">warning</option>
						</select>
					</label>
					<label className="grid gap-2" htmlFor="instance">
						<span className="text-sm font-medium">Instance</span>
						<input
							className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
							defaultValue={model.alertFilters.instance}
							id="instance"
							name="instance"
							placeholder="inst-alert"
						/>
					</label>
					<label className="grid gap-2" htmlFor="opened_after">
						<span className="text-sm font-medium">Opened after</span>
						<input
							className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
							defaultValue={model.alertFilters.opened_after}
							id="opened_after"
							name="opened_after"
							type="datetime-local"
						/>
					</label>
					<label className="grid gap-2" htmlFor="opened_before">
						<span className="text-sm font-medium">Opened before</span>
						<input
							className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
							defaultValue={model.alertFilters.opened_before}
							id="opened_before"
							name="opened_before"
							type="datetime-local"
						/>
					</label>
					<div className="flex flex-wrap items-center gap-3 md:col-span-2">
						<button
							className="rounded-[1rem] bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white"
							type="submit"
						>
							Apply filters
						</button>
						<a className="text-sm font-medium text-[var(--accent)]" href="/alerts">
							Clear
						</a>
						<p className="text-sm text-[var(--muted)]">
							Showing {model.alerts.length} matching alert{model.alerts.length === 1 ? "" : "s"}.
						</p>
					</div>
				</form>
				{model.alerts.length === 0 ? (
					<p className="rounded-[1.2rem] border border-dashed border-black/10 bg-[var(--panel)] p-4 text-sm text-[var(--muted)]">
						No alerts matched the current filter window.
					</p>
				) : null}
				{model.alerts.map((alert) => (
					<a
						className="block rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4 transition hover:-translate-y-0.5 hover:border-[var(--accent)]"
						href={`/alerts/${alert.alert_id}`}
						key={alert.alert_id}
					>
						<p className="font-semibold">{alert.rule_name}</p>
						<p className="text-sm text-[var(--muted)]">
							{formatDatabaseEngine(alert.engine)} · {alert.instance_id} · {alert.metric_name}
						</p>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Current value {alert.current_value} vs threshold {alert.threshold}
						</p>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Owner {alert.owner_user_id ?? "unassigned"} · Ack{" "}
							{alert.acknowledged_by_user_id ?? "pending"}
						</p>
						<p className="mt-2 text-xs uppercase tracking-[0.22em] text-[var(--accent)]">
							{alert.status}
						</p>
					</a>
				))}
			</div>
		</AppChrome>
	);
}

function emptyToUndefined<T extends string>(value: T | ""): T | undefined {
	return value.length === 0 ? undefined : (value as T);
}
