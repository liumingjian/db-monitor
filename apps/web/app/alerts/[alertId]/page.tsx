import { AlertTriagePanel } from "../../../src/components/alert-triage-panel";
import { AppChrome } from "../../../src/components/app-chrome";
import { buildOperationsModel, formatDatabaseEngine } from "../../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

interface AlertDetailPageProps {
	readonly params: Promise<{
		readonly alertId: string;
	}>;
}

export default async function AlertDetailPage({ params }: AlertDetailPageProps) {
	const { alertId } = await params;
	const session = await requireServerSession(`/alerts/${alertId}`);
	const apiClient = await createServerApiClient();
	const model = buildOperationsModel({
		alertDetail: await apiClient.getAlert(alertId),
	});

	return (
		<AppChrome session={session}>
			<div className="space-y-4">
				<h2 className="text-2xl font-semibold">{model.alertDetail.record.rule_name}</h2>
				<div className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4">
					<p className="text-sm text-[var(--muted)]">
						{formatDatabaseEngine(model.alertDetail.record.engine)} alert · Instance{" "}
						{model.alertDetail.record.instance_id} · {model.alertDetail.record.metric_name}
					</p>
					<p className="mt-2 text-sm text-[var(--muted)]">
						Value {model.alertDetail.record.current_value} / threshold{" "}
						{model.alertDetail.record.threshold}
					</p>
				</div>
				<AlertTriagePanel alertDetail={model.alertDetail} />
				{model.alertDetail.history.map((event) => (
					<div
						className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4"
						key={event.occurred_at}
					>
						<p className="text-sm font-semibold">{event.event_type}</p>
						<p className="mt-2 text-sm text-[var(--muted)]">{event.detail}</p>
					</div>
				))}
			</div>
		</AppChrome>
	);
}
