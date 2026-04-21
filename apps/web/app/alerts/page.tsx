import { AppChrome } from "../../src/components/app-chrome";
import { buildOperationsModel, formatDatabaseEngine } from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

export default async function AlertsPage() {
	const session = await requireServerSession("/alerts");
	const apiClient = await createServerApiClient();
	const model = buildOperationsModel({
		alerts: await apiClient.listAlerts(),
	});

	return (
		<AppChrome session={session}>
			<div className="space-y-4">
				<h2 className="text-2xl font-semibold">Alert queue</h2>
				{model.alerts.length === 0 ? (
					<p className="rounded-[1.2rem] border border-dashed border-black/10 bg-[var(--panel)] p-4 text-sm text-[var(--muted)]">
						No active multi-engine alerts are open for this window.
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
