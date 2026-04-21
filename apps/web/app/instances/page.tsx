import { AppChrome } from "../../src/components/app-chrome";
import { createInstanceAction } from "../../src/monitoring-actions";
import {
	buildInstanceCapabilityBoundary,
	buildInstancesFlowModel,
	getInstanceConnectionLabel,
} from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

const ENGINE_OPTIONS = [
	{ description: "Fleet metrics, live analytics, preset views, and capacity readouts are available.", label: "MySQL", value: "mysql" },
	{ description: "Onboarding, validation, fleet health visibility, and minimal detail trends are available. Overview cards and leaders follow fleet coverage.", label: "Oracle", value: "oracle" },
] as const;

export default async function InstancesPage() {
	const session = await requireServerSession("/instances");
	const apiClient = await createServerApiClient();
	const model = buildInstancesFlowModel({
		tableRows: await apiClient.listInstances(),
	});

	return (
		<AppChrome session={session}>
			<div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
				<section className="space-y-4">
					<h2 className="text-2xl font-semibold">Onboard an instance</h2>
					<p className="max-w-2xl text-sm text-[var(--muted)]">
						The current UI supports MySQL analytics end to end. Oracle now contributes to fleet health
						and engine coverage on the overview and exposes minimal detail trends after collection.
						Overview cards, charts, and signal leaders still follow the supported overview metric
						engines shown on the dashboard. The database field is interpreted as the DSN or service
						name for Oracle.
					</p>
					<form action={createInstanceAction} className="grid gap-4 md:grid-cols-2">
						<label className="grid gap-2 md:col-span-2" htmlFor="engine">
							<span className="text-sm font-medium">Engine</span>
							<select
								className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
								defaultValue={model.formValues.engine}
								id="engine"
								name="engine"
							>
								{ENGINE_OPTIONS.map((option) => (
									<option key={option.value} value={option.value}>
										{option.label}
									</option>
								))}
							</select>
							<p className="text-sm text-[var(--muted)]">
								{
									ENGINE_OPTIONS.find((option) => option.value === model.formValues.engine)
										?.description
								}
							</p>
						</label>
						{model.formFields.map((field) => (
							<label className="grid gap-2" htmlFor={field.name} key={field.name}>
								<span className="text-sm font-medium">{field.label}</span>
								<input
									className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
									defaultValue={getInstanceFieldValue(model, field.name)}
									id={field.name}
									name={field.name}
									type={field.type}
								/>
							</label>
						))}
						<button
							className="rounded-[1rem] bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white md:col-span-2"
							type="submit"
						>
							Create and validate instance
						</button>
					</form>
				</section>
				<section className="space-y-3">
					<h2 className="text-2xl font-semibold">Fleet inventory</h2>
					{model.tableRows.length === 0 ? (
						<p className="rounded-[1.2rem] border border-dashed border-black/10 bg-[var(--panel)] p-4 text-sm text-[var(--muted)]">
							No monitored instances have been onboarded yet.
						</p>
					) : null}
					{model.tableRows.map((instance) => (
						<a
							className="block rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4 transition hover:-translate-y-0.5 hover:border-[var(--accent)]"
							href={`/instances/${instance.instance_id}`}
							key={instance.instance_id}
						>
							<div className="flex items-start justify-between gap-3">
								<div>
									<p className="font-semibold">{instance.name}</p>
									<p className="text-sm text-[var(--muted)]">{instance.environment}</p>
								</div>
								<span className="rounded-full border border-[var(--accent)]/25 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">
									{instance.engine}
								</span>
							</div>
							<p className="mt-2 text-sm text-[var(--muted)]">
								{instance.connection.host}:{instance.connection.port}
							</p>
							<p className="mt-1 text-sm text-[var(--muted)]">
								{getInstanceConnectionLabel(instance)}: {instance.connection.database}
							</p>
							<p className="mt-3 text-sm text-[var(--muted)]">
								{buildInstanceCapabilityBoundary(instance).value}
							</p>
							<p className="mt-3 text-xs uppercase tracking-[0.22em] text-[var(--accent)]">
								{instance.validation.status}
							</p>
						</a>
					))}
				</section>
			</div>
		</AppChrome>
	);
}

function getInstanceFieldValue(
	model: ReturnType<typeof buildInstancesFlowModel>,
	key: string,
): string {
	return model.formValues[key as keyof typeof model.formValues] ?? "";
}
